# Pro-Search-Server

[![LangGraph](https://img.shields.io/badge/LangGraph-Powered-blue)](https://github.com/langchain-ai/langgraph)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Google Gemini](https://img.shields.io/badge/Gemini-2.0%20%7C%202.5-orange)](https://ai.google.dev/)

An advanced AI-powered research agent built with LangGraph that generates optimized search queries, performs comprehensive web research with Google Search API, and delivers well-cited, accurate answers through an iterative reflection process.

<div align="center">
  <img src="./static/studio_ui.png" alt="Graph view in LangGraph Studio UI" width="75%" />
</div>

## 🚀 Features

- **Intelligent Query Generation**: Uses Gemini 2.0 Flash to generate optimized, diverse search queries
- **Native Google Search Integration**: Leverages Google's native Search API with grounding metadata
- **Iterative Reflection Loop**: Self-evaluates research quality and identifies knowledge gaps
- **Automatic Citation Management**: Tracks and inserts citations with URL resolution
- **Multi-Model Architecture**: Strategically uses different Gemini models for specific tasks
- **FastAPI Backend**: Production-ready API with React frontend integration
- **LangSmith Integration**: Built-in tracing and observability

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

### Citation System
- Automatic source tracking via grounding metadata
- URL resolution for token efficiency
- Inline citation markers (e.g., `[1]`, `[2]`)
- Deduplication of sources in final output

### State Management
- `OverallState`: Main graph state with message history
- `QueryGenerationState`: Search query list
- `WebSearchState`: Individual search execution
- `ReflectionState`: Evaluation and follow-up queries

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

**LangSmith tracing not working**
- Set `LANGSMITH_TRACING=true` in `.env`
- Verify `LANGSMITH_API_KEY` is valid

---

Built with ❤️ using [LangGraph](https://github.com/langchain-ai/langgraph) and [Google Gemini](https://ai.google.dev/)
