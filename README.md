# Pro-Search-Agent-Server

[![LangGraph](https://img.shields.io/badge/LangGraph-Powered-blue)](https://github.com/langchain-ai/langgraph)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Google Gemini](https://img.shields.io/badge/Gemini-2.0%20%7C%202.5-orange)](https://ai.google.dev/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](./LICENSE)

An advanced AI-powered research agent built with LangGraph that generates optimized search queries, performs comprehensive web research with Google Search API, and delivers well-cited, accurate answers through an iterative reflection process.

**Pro-Search-Agent-Server** is a production-ready research automation system that combines the power of Google's Gemini models with intelligent web search capabilities. The agent autonomously breaks down complex questions, conducts parallel web research, evaluates the quality of gathered information, and synthesizes comprehensive answers with proper source attribution.

### Key Highlights

✅ **Self-Improving Research**: Iterative reflection loop identifies knowledge gaps and refines research  
✅ **Enterprise-Grade Reliability**: Comprehensive error handling, retry logic, and graceful degradation  
✅ **Full Transparency**: Every fact is backed by citations with source URLs  
✅ **Production-Ready**: Detailed logging, monitoring, and observability with LangSmith  
✅ **Highly Configurable**: Adjust models, research depth, and query count per use case  

<div align="center">
  <img src="./static/graph.png" alt="Graph view in LangGraph Studio UI" width="75%" />
  <p><em>Visual representation of the Pro-Search agent workflow in LangGraph Studio</em></p>
</div>

## 🚀 Features

- **Intelligent Query Generation**: Uses Gemini 2.0 Flash to generate optimized, diverse search queries
- **Native Google Search Integration**: Leverages Google's native Search API with grounding metadata
- **Iterative Reflection Loop**: Self-evaluates research quality and identifies knowledge gaps
- **Automatic Citation Management**: Tracks and inserts citations with URL resolution
- **Multi-Model Architecture**: Strategically uses different Gemini models for specific tasks
- **Robust Error Handling**: Comprehensive error recovery with retry logic and graceful degradation
- **Advanced Logging**: Detailed logging for debugging and monitoring with configurable levels
- **Performance Optimizations**: LRU caching for API clients and efficient token management
- **Parallel Web Research**: Concurrent search query execution for faster results
- **FastAPI Backend**: Production-ready API with React frontend integration
- **LangSmith Integration**: Built-in tracing and observability for debugging and optimization

## 📊 Agent Architecture

The agent implements a sophisticated graph-based workflow:

```
__start__ → generate_query → web_research (parallel) → reflection → finalize_answer → __end__
                                                           ↓
                                                    (self-loop for iterative research)
```

### Workflow Nodes

1. **generate_query** - Analyzes user questions and generates 1-3 optimized search queries
2. **web_research** - Executes parallel web searches using Google Search API with grounding
3. **reflection** - Evaluates research completeness and identifies knowledge gaps
4. **finalize_answer** - Synthesizes findings into a comprehensive, well-cited response

## 🏗️ Project Structure

```
src/agent/
├── __init__.py
├── app.py                    # FastAPI application with frontend mount
├── configuration.py          # Configurable agent parameters (models, loop counts)
├── graph.py                  # LangGraph workflow definition and node implementations
├── old_graph.py             # Legacy implementation (reference)
├── prompts.py               # System prompts for each agent node
├── state.py                 # TypedDict state schemas for graph execution
├── tools_and_schemas.py     # Pydantic models for structured outputs
└── utils.py                 # Citation handling, URL resolution, topic extraction
```

## 🛠️ Installation

### Prerequisites

- Python 3.12 or higher
- Google Gemini API key
- LangSmith API key (optional, for tracing)
- Node.js (for frontend, if building from source)

### Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd Pro-Search-Server
```

2. **Install Python dependencies**
```bash
pip install -e . "langgraph-cli[inmem]"
```

3. **Configure environment variables**
```bash
cp .env.example .env
```

Edit `.env` and add your API keys:
```bash
# Required
GEMINI_API_KEY=your-gemini-api-key-here
GOOGLE_API_KEY=your-google-api-key-here

# Optional (for LangSmith tracing)
LANGSMITH_API_KEY=your-langsmith-api-key-here
LANGSMITH_TRACING=true
LANGSMITH_PROJECT=pro-search-agent
```

4. **Build frontend** (optional, for web UI)
```bash
cd frontend
npm install
npm run build
cd ..
```

## 🚀 Running the Agent

### Development Mode with LangGraph Studio

```bash
langgraph dev
```

This starts:
- LangGraph Server on `http://localhost:2024`
- LangGraph Studio UI for visual debugging
- FastAPI app on `/app` endpoint (if frontend is built)
- Hot reload for local development

### Production Mode

```bash
langgraph up
```

## 🔧 Configuration

The agent supports runtime configuration through the `Configuration` class:

```python
{
  "configurable": {
    "query_generator_model": "gemini-2.0-flash",      # Query generation model
    "reflection_model": "gemini-2.5-flash",            # Reflection model
    "answer_model": "gemini-2.5-pro",                  # Final answer model
    "number_of_initial_queries": 3,                    # Initial search queries
    "max_research_loops": 2                            # Maximum reflection iterations
  }
}
```

## 📡 API Usage

### Python SDK

```python
from langgraph_sdk import get_client

client = get_client(url="http://localhost:2024")

# Start a thread
thread = await client.threads.create()

# Run the agent
async for chunk in client.runs.stream(
    thread["thread_id"],
    "agent",
    input={"messages": [{"role": "user", "content": "What are the latest developments in quantum computing?"}]},
    config={"configurable": {"max_research_loops": 3}}
):
    print(chunk)
```

### REST API

```bash
curl -X POST http://localhost:2024/threads/<thread_id>/runs/stream \
  -H "Content-Type: application/json" \
  -d '{
    "assistant_id": "agent",
    "input": {
      "messages": [{"role": "user", "content": "Explain LangGraph"}]
    }
  }'
```

## 🧠 How It Works

### 1. Query Generation
- Analyzes the user's question using Gemini 2.0 Flash
- Generates 1-3 diverse, specific search queries
- Ensures queries target current information

### 2. Web Research (Parallel Execution)
- Each query runs in parallel using Google Search API
- Retrieves grounding metadata with source attribution
- Resolves URLs to short codes for token efficiency
- Inserts citation markers in generated text

### 3. Reflection & Iteration
- Evaluates if gathered information is sufficient
- Identifies specific knowledge gaps
- Generates targeted follow-up queries
- Continues research up to `max_research_loops` times

### 4. Answer Finalization
- Synthesizes all research findings
- Restores full URLs from short codes
- Produces well-structured response with inline citations
- Returns unique source list

## 🎯 Use Cases

- **Research Assistance**: Comprehensive answers with verifiable sources
- **Market Analysis**: Multi-faceted research with diverse perspectives
- **Technical Documentation**: Current information synthesis
- **Fact-Checking**: Citation-backed responses
- **Content Creation**: Research-driven content generation

## 🔍 Development & Debugging

### LangGraph Studio
- Visual graph execution flow
- State inspection at each node
- Time-travel debugging (edit past state and rerun)
- Hot reload for code changes

### LangSmith Integration
- Detailed trace analysis
- Performance monitoring
- Collaborative debugging
- Run comparisons

## 📝 Key Implementation Details

### Multi-Model Strategy
- **Gemini 2.0 Flash**: Fast query generation and web search
- **Gemini 2.5 Flash**: Balanced reflection and evaluation
- **Gemini 2.5 Pro**: High-quality final answer synthesis

### Error Handling & Resilience
- **Automatic Retry Logic**: Up to 3 retries for Google API calls with exponential backoff
- **Graceful Degradation**: Partial results returned on failures instead of complete failure
- **Comprehensive Logging**: INFO-level logging for workflow tracking, ERROR-level for issues
- **Input Validation**: Validates state and configuration at each node
- **Exception Recovery**: Catches and logs exceptions while maintaining workflow continuity

### Performance Optimizations
- **LRU Caching**: Cached Google GenAI client initialization to reduce overhead
- **Factory Pattern**: Centralized LLM creation with `create_llm()` for consistency
- **Parallel Execution**: Web research queries run concurrently using LangGraph's `Send` API
- **URL Resolution**: Short URL codes minimize token usage in intermediate processing
- **Token Efficiency**: Citation markers inserted only after final answer generation

### Citation System
- **Automatic Source Tracking**: Via grounding metadata from Google Search API
- **URL Resolution**: Long Vertex AI Search URLs replaced with short codes
- **Inline Citation Markers**: Markdown-formatted links (e.g., `[source](url)`)
- **Deduplication**: Only sources actually used in final answer are returned
- **Bidirectional Mapping**: Short codes resolved back to original URLs in final output

### State Management
- **OverallState**: Main graph state with message history and accumulated results
- **QueryGenerationState**: Search query list with rationale
- **WebSearchState**: Individual search execution with unique IDs
- **ReflectionState**: Evaluation results and follow-up queries
- **Type Safety**: TypedDict schemas ensure type correctness across nodes

## 💎 Code Quality & Best Practices

### Architectural Improvements
- **Factory Pattern**: Centralized `create_llm()` function for consistent LLM instantiation
- **Dependency Injection**: Configuration passed through RunnableConfig
- **Single Responsibility**: Each node has a single, well-defined purpose
- **Comprehensive Documentation**: Detailed docstrings with Args, Returns, and Raises sections
- **Type Hints**: Full type annotations for better IDE support and type checking

### Production-Ready Features
- **Environment Validation**: API keys validated on startup with clear error messages
- **Structured Logging**: Hierarchical logging with timestamps and log levels
- **Error Context**: Exception stack traces captured for debugging
- **Retry Mechanisms**: Configurable retry logic with exponential backoff
- **Graceful Failures**: Workflow continues with partial results when possible
- **Resource Management**: Cached clients to reduce initialization overhead

## 🤝 Contributing

Contributions are welcome! Key areas for enhancement:
- Additional search providers (Bing, Brave, etc.)
- Enhanced citation formatting
- Multi-language support
- Custom embedding for relevance ranking

## 📄 License

MIT License - See [LICENSE](./LICENSE) for details

## 🔗 Resources

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [LangGraph Server Guide](https://langchain-ai.github.io/langgraph/concepts/langgraph_server/)
- [LangGraph Studio](https://langchain-ai.github.io/langgraph/concepts/langgraph_studio/)
- [Google Gemini API](https://ai.google.dev/)
- [LangSmith](https://smith.langchain.com/)

## 🐛 Troubleshooting

**Frontend returns 503 error on `/app`**
- Ensure frontend is built: `cd frontend && npm run build`

**GEMINI_API_KEY not set error**
- Verify `.env` file exists and contains `GEMINI_API_KEY`
- Check that the API key is valid and not expired
- Ensure no extra spaces or quotes around the API key

**LangSmith tracing not working**
- Set `LANGSMITH_TRACING=true` in `.env`
- Verify `LANGSMITH_API_KEY` is valid
- Check LangSmith dashboard for incoming traces

**Google API rate limit errors**
- Implement request throttling in your application
- Check your Google Cloud quota limits
- Consider upgrading your API plan
- The agent includes automatic retry logic with exponential backoff

**Web search returns no results**
- Verify `GOOGLE_API_KEY` is configured correctly
- Check Google Search API quota and billing status
- Review logs for specific error messages
- The agent will attempt up to 3 retries before failing

**Module import errors**
- Ensure all dependencies are installed: `pip install -e .`
- Check Python version is 3.12 or higher: `python --version`
- Verify virtual environment is activated

**Graph execution hangs**
- Check LangSmith traces for stuck nodes
- Review logs for timeout or API errors
- Consider reducing `max_research_loops` parameter
- Verify network connectivity to Google APIs

---

Built with ❤️ using [LangGraph](https://github.com/langchain-ai/langgraph) and [Google Gemini](https://ai.google.dev/)
