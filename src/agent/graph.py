import os
import logging
from typing import Optional, Dict, Any
from functools import lru_cache

from agent.tools_and_schemas import SearchQueryList, Reflection
from dotenv import load_dotenv
from langchain_core.messages import AIMessage
from langgraph.types import Send
from langgraph.graph import StateGraph
from langgraph.graph import START, END
from langchain_core.runnables import RunnableConfig
from google.genai import Client
from google.api_core import exceptions as google_exceptions

from agent.state import (
    OverallState,
    QueryGenerationState,
    ReflectionState,
    WebSearchState,
)
from agent.configuration import Configuration
from agent.prompts import (
    get_current_date,
    query_writer_instructions,
    web_searcher_instructions,
    reflection_instructions,
    answer_instructions,
)
from langchain_google_genai import ChatGoogleGenerativeAI
from agent.utils import (
    get_citations,
    get_research_topic,
    insert_citation_markers,
    resolve_urls,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

# Validate environment variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    logger.error("GEMINI_API_KEY environment variable is not set")
    raise ValueError("GEMINI_API_KEY is not set. Please set it in your .env file.")

# Used for Google Search API
@lru_cache(maxsize=1)
def get_genai_client() -> Client:
    """Get or create a cached Google GenAI client instance.

    Returns:
        Client: Cached Google GenAI client instance
    """
    try:
        return Client(api_key=GEMINI_API_KEY)
    except Exception as e:
        logger.error(f"Failed to initialize Google GenAI client: {e}")
        raise


genai_client = get_genai_client()


def create_llm(model: str, temperature: float = 1.0, max_retries: int = 2) -> ChatGoogleGenerativeAI:
    """Factory function to create configured LLM instances.

    Args:
        model: Model name to use
        temperature: Temperature setting for generation
        max_retries: Maximum number of retry attempts

    Returns:
        ChatGoogleGenerativeAI: Configured LLM instance
    """
    return ChatGoogleGenerativeAI(
        model=model,
        temperature=temperature,
        max_retries=max_retries,
        api_key=GEMINI_API_KEY,
    )


# Nodes
def generate_query(state: OverallState, config: RunnableConfig) -> QueryGenerationState:
    """LangGraph node that generates search queries based on the User's question.

    Uses Gemini 2.0 Flash to create an optimized search queries for web research based on
    the User's question.

    Args:
        state: Current graph state containing the User's question
        config: Configuration for the runnable, including LLM provider settings

    Returns:
        Dictionary with state update, including search_query key containing the generated queries

    Raises:
        ValueError: If no messages are provided in state
        Exception: If query generation fails
    """
    try:
        logger.info("Starting query generation")

        if not state.get("messages"):
            logger.error("No messages provided in state")
            raise ValueError("State must contain messages")

        configurable = Configuration.from_runnable_config(config)

        # check for custom initial search query count
        if state.get("initial_search_query_count") is None:
            state["initial_search_query_count"] = configurable.number_of_initial_queries

        logger.info(f"Generating {state['initial_search_query_count']} initial queries")

        # init Gemini 2.0 Flash using factory function
        llm = create_llm(
            model=configurable.query_generator_model,
            temperature=1.0,
            max_retries=2
        )
        structured_llm = llm.with_structured_output(SearchQueryList)

        # Format the prompt
        current_date = get_current_date()
        research_topic = get_research_topic(state["messages"])
        formatted_prompt = query_writer_instructions.format(
            current_date=current_date,
            research_topic=research_topic,
            number_queries=state["initial_search_query_count"],
        )

        # Generate the search queries
        result = structured_llm.invoke(formatted_prompt)

        if not result.query:
            logger.warning("No queries generated, using default query")
            result.query = [research_topic]

        logger.info(f"Successfully generated {len(result.query)} queries")
        return {"search_query": result.query}

    except Exception as e:
        logger.error(f"Error in generate_query: {e}", exc_info=True)
        raise


def continue_to_web_research(state: QueryGenerationState):
    """LangGraph node that sends the search queries to the web research node.

    This is used to spawn n number of web research nodes, one for each search query.
    """
    return [
        Send("web_research", {"search_query": search_query, "id": int(idx)})
        for idx, search_query in enumerate(state["search_query"])
    ]


def web_research(state: WebSearchState, config: RunnableConfig) -> OverallState:
    """LangGraph node that performs web research using the native Google Search API tool.

    Executes a web search using the native Google Search API tool in combination with Gemini 2.0 Flash.

    Args:
        state: Current graph state containing the search query and research loop count
        config: Configuration for the runnable, including search API settings

    Returns:
        Dictionary with state update, including sources_gathered, research_loop_count, and web_research_results

    Raises:
        Exception: If web search fails after retries
    """
    try:
        logger.info(f"Starting web research for query: {state['search_query']}")

        # Configure
        configurable = Configuration.from_runnable_config(config)
        formatted_prompt = web_searcher_instructions.format(
            current_date=get_current_date(),
            research_topic=state["search_query"],
        )

        # Uses the google genai client as the langchain client doesn't return grounding metadata
        max_retries = 3
        retry_count = 0
        response = None

        while retry_count < max_retries:
            try:
                response = genai_client.models.generate_content(
                    model=configurable.query_generator_model,
                    contents=formatted_prompt,
                    config={
                        "tools": [{"google_search": {}}],
                        "temperature": 0,
                    },
                )
                break  # Success, exit retry loop

            except google_exceptions.GoogleAPIError as e:
                retry_count += 1
                logger.warning(f"Google API error (attempt {retry_count}/{max_retries}): {e}")
                if retry_count >= max_retries:
                    logger.error(f"Failed to perform web search after {max_retries} attempts")
                    raise
            except Exception as e:
                retry_count += 1
                logger.warning(f"Unexpected error (attempt {retry_count}/{max_retries}): {e}")
                if retry_count >= max_retries:
                    raise

        if not response:
            raise ValueError("No response received from Google Search API")

        # Validate response structure
        if not response.candidates or len(response.candidates) == 0:
            logger.warning("No candidates in response, returning empty results")
            return {
                "sources_gathered": [],
                "search_query": [state["search_query"]],
                "web_research_result": ["No results found for this query."],
            }

        # resolve the urls to short urls for saving tokens and time
        resolved_urls = resolve_urls(
            response.candidates[0].grounding_metadata.grounding_chunks, state["id"]
        )

        # Gets the citations and adds them to the generated text
        citations = get_citations(response, resolved_urls)
        modified_text = insert_citation_markers(response.text, citations)
        sources_gathered = [item for citation in citations for item in citation["segments"]]

        logger.info(f"Web research completed. Found {len(sources_gathered)} sources")

        return {
            "sources_gathered": sources_gathered,
            "search_query": [state["search_query"]],
            "web_research_result": [modified_text],
        }

    except Exception as e:
        logger.error(f"Error in web_research: {e}", exc_info=True)
        # Return partial results instead of failing completely
        return {
            "sources_gathered": [],
            "search_query": [state["search_query"]],
            "web_research_result": [f"Error performing research: {str(e)}"],
        }


def reflection(state: OverallState, config: RunnableConfig) -> ReflectionState:
    """LangGraph node that identifies knowledge gaps and generates potential follow-up queries.

    Analyzes the current summary to identify areas for further research and generates
    potential follow-up queries. Uses structured output to extract
    the follow-up query in JSON format.

    Args:
        state: Current graph state containing the running summary and research topic
        config: Configuration for the runnable, including LLM provider settings

    Returns:
        Dictionary with state update, including search_query key containing the generated follow-up query

    Raises:
        Exception: If reflection fails
    """
    try:
        logger.info("Starting reflection on research results")

        configurable = Configuration.from_runnable_config(config)
        # Increment the research loop count and get the reasoning model
        state["research_loop_count"] = state.get("research_loop_count", 0) + 1
        reasoning_model = state.get("reasoning_model", configurable.reflection_model)

        logger.info(f"Research loop count: {state['research_loop_count']}, Model: {reasoning_model}")

        # Format the prompt
        current_date = get_current_date()
        formatted_prompt = reflection_instructions.format(
            current_date=current_date,
            research_topic=get_research_topic(state["messages"]),
            summaries="\n\n---\n\n".join(state["web_research_result"]),
        )

        # init Reasoning Model using factory function
        llm = create_llm(
            model=reasoning_model,
            temperature=1.0,
            max_retries=2
        )
        result = llm.with_structured_output(Reflection).invoke(formatted_prompt)

        logger.info(f"Reflection complete. Sufficient: {result.is_sufficient}, Follow-up queries: {len(result.follow_up_queries)}")

        return {
            "is_sufficient": result.is_sufficient,
            "knowledge_gap": result.knowledge_gap,
            "follow_up_queries": result.follow_up_queries,
            "research_loop_count": state["research_loop_count"],
            "number_of_ran_queries": len(state["search_query"]),
        }

    except Exception as e:
        logger.error(f"Error in reflection: {e}", exc_info=True)
        # Return a default response to continue the flow
        return {
            "is_sufficient": True,  # Stop on error
            "knowledge_gap": "",
            "follow_up_queries": [],
            "research_loop_count": state.get("research_loop_count", 0) + 1,
            "number_of_ran_queries": len(state.get("search_query", [])),
        }


def evaluate_research(
    state: ReflectionState,
    config: RunnableConfig,
) -> str:
    """LangGraph routing function that determines the next step in the research flow.

    Controls the research loop by deciding whether to continue gathering information
    or to finalize the summary based on the configured maximum number of research loops.

    Args:
        state: Current graph state containing the research loop count
        config: Configuration for the runnable, including max_research_loops setting

    Returns:
        String literal indicating the next node to visit ("web_research" or "finalize_answer")
    """
    configurable = Configuration.from_runnable_config(config)
    max_research_loops = (
        state.get("max_research_loops")
        if state.get("max_research_loops") is not None
        else configurable.max_research_loops
    )

    logger.info(f"Evaluating research: Loop {state['research_loop_count']}/{max_research_loops}, Sufficient: {state['is_sufficient']}")

    if state["is_sufficient"] or state["research_loop_count"] >= max_research_loops:
        logger.info("Research complete, finalizing answer")
        return "finalize_answer"
    else:
        logger.info(f"Continuing research with {len(state['follow_up_queries'])} follow-up queries")
        return [
            Send(
                "web_research",
                {
                    "search_query": follow_up_query,
                    "id": state["number_of_ran_queries"] + int(idx),
                },
            )
            for idx, follow_up_query in enumerate(state["follow_up_queries"])
        ]


def finalize_answer(state: OverallState, config: RunnableConfig):
    """LangGraph node that finalizes the research summary.

    Prepares the final output by deduplicating and formatting sources, then
    combining them with the running summary to create a well-structured
    research report with proper citations.

    Args:
        state: Current graph state containing the running summary and sources gathered
        config: Configuration for the runnable

    Returns:
        Dictionary with state update, including messages with the final answer and unique sources

    Raises:
        Exception: If finalization fails
    """
    try:
        logger.info("Starting answer finalization")

        configurable = Configuration.from_runnable_config(config)
        reasoning_model = state.get("reasoning_model") or configurable.answer_model

        logger.info(f"Using model: {reasoning_model}")

        # Format the prompt
        current_date = get_current_date()
        formatted_prompt = answer_instructions.format(
            current_date=current_date,
            research_topic=get_research_topic(state["messages"]),
            summaries="\n---\n\n".join(state["web_research_result"]),
        )

        # init Reasoning Model using factory function with temperature 0 for consistency
        llm = create_llm(
            model=reasoning_model,
            temperature=0,
            max_retries=2
        )
        result = llm.invoke(formatted_prompt)

        # Replace the short urls with the original urls and add all used urls to the sources_gathered
        unique_sources = []
        for source in state["sources_gathered"]:
            if source["short_url"] in result.content:
                result.content = result.content.replace(
                    source["short_url"], source["value"]
                )
                unique_sources.append(source)

        logger.info(f"Answer finalized with {len(unique_sources)} unique sources")

        return {
            "messages": [AIMessage(content=result.content)],
            "sources_gathered": unique_sources,
        }

    except Exception as e:
        logger.error(f"Error in finalize_answer: {e}", exc_info=True)
        # Return error message instead of crashing
        error_message = f"An error occurred while finalizing the answer: {str(e)}"
        return {
            "messages": [AIMessage(content=error_message)],
            "sources_gathered": state.get("sources_gathered", []),
        }


# Create our Agent Graph
builder = StateGraph(OverallState, config_schema=Configuration)

# Define the nodes we will cycle between
builder.add_node("generate_query", generate_query)
builder.add_node("web_research", web_research)
builder.add_node("reflection", reflection)
builder.add_node("finalize_answer", finalize_answer)

# Set the entrypoint as `generate_query`
# This means that this node is the first one called
builder.add_edge(START, "generate_query")
# Add conditional edge to continue with search queries in a parallel branch
builder.add_conditional_edges(
    "generate_query", continue_to_web_research, ["web_research"]
)
# Reflect on the web research
builder.add_edge("web_research", "reflection")
# Evaluate the research
builder.add_conditional_edges(
    "reflection", evaluate_research, ["web_research", "finalize_answer"]
)
# Finalize the answer
builder.add_edge("finalize_answer", END)

graph = builder.compile(name="pro-search-agent")
