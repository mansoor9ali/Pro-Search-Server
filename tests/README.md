# Pro-Search Agent Tests

Comprehensive test suite for the Pro-Search Agent with multiple testing modes and detailed reporting.

## 📁 Test Files

- **`test-pro-search-agent.py`** - Main test suite with interactive mode
- **`test_runner.py`** - Advanced test runner with benchmarking and JSON reports
- **`test_config.py`** - Test configuration, queries, and validation logic

## 🚀 Running Tests

### Quick Start - Basic Tests

Run the default tests (euro 2024 + follow-up):

```bash
python tests/test-pro-search-agent.py
```

### Run All Tests

Execute the complete test suite:

```bash
python tests/test-pro-search-agent.py all
```

### Run Specific Test

Run individual tests:

```bash
python tests/test-pro-search-agent.py test1  # Basic factual query
python tests/test-pro-search-agent.py test2  # Follow-up query
python tests/test-pro-search-agent.py test3  # Complex research
python tests/test-pro-search-agent.py test4  # Comparative analysis
python tests/test-pro-search-agent.py test5  # Technical query
python tests/test-pro-search-agent.py test6  # Minimal research
```

### Interactive Mode

Test with custom queries interactively:

```bash
python tests/test-pro-search-agent.py interactive
```

Commands in interactive mode:
- Type any query to search
- Type `new` to start a fresh conversation
- Type `exit` or `quit` to stop

## 🧪 Advanced Test Runner

### Run All Test Categories

```bash
python tests/test_runner.py all
```

### Run Specific Category

```bash
python tests/test_runner.py factual       # Simple factual queries
python tests/test_runner.py comparative   # Comparison queries
python tests/test_runner.py technical     # Technical documentation
python tests/test_runner.py complex       # Complex research
python tests/test_runner.py conversational # Multi-turn conversations
python tests/test_runner.py edge_case     # Edge cases and error handling
```

### Options

```bash
# Custom output directory
python tests/test_runner.py all --output-dir my_results

# Don't save JSON report
python tests/test_runner.py all --no-report

# Verbose logging
python tests/test_runner.py all --verbose
```

## 📊 Test Categories

### 1. Factual Tests
Simple, straightforward queries with clear answers:
- "Who won the euro 2024"
- "What is the capital of Japan?"
- "When was Python created?"

### 2. Comparative Tests
Queries requiring comparison of multiple items:
- "Compare Python and JavaScript performance"
- "Differences between GPT-4 and Claude 3"
- "Compare React, Vue, and Angular"

### 3. Technical Tests
Technical documentation and how-to queries:
- "How to implement async/await in Python?"
- "Best practices for Docker containerization"
- "LangGraph streaming API documentation"

### 4. Complex Tests
Multi-faceted research requiring deep analysis:
- "Latest AI developments in 2025 and their impact"
- "Quantum computing breakthroughs and companies"
- "Electric vehicles market analysis"

### 5. Conversational Tests
Multi-turn conversations with follow-up questions:
- Initial: "Who is Elon Musk?"
  - Follow-up: "What companies does he own?"
  - Follow-up: "Which is the most valuable?"

### 6. Edge Case Tests
Error handling and unusual inputs:
- Empty queries
- Nonsensical text
- Philosophical questions

## 📈 Test Reports

The advanced test runner generates comprehensive JSON reports in the `test_results/` directory:

```json
{
  "summary": {
    "total_tests": 20,
    "passed": 18,
    "failed": 2,
    "success_rate": 90.0,
    "total_execution_time": 245.67,
    "average_execution_time": 12.28
  },
  "by_category": {
    "factual": {
      "total": 3,
      "passed": 3,
      "failed": 0,
      "success_rate": 100.0
    }
  },
  "environment": {
    "python_version": "3.12.0",
    "platform": "win32",
    "timestamp": "2026-01-01T12:00:00",
    "gemini_api_configured": true,
    "langsmith_enabled": true
  },
  "detailed_results": [...]
}
```

## 🎯 Test Metrics

Each test collects the following metrics:

- **Execution Time** - Time taken to complete the query
- **Search Queries** - Number of search queries generated
- **Sources Gathered** - Number of unique sources cited
- **Research Loops** - Number of reflection iterations
- **Answer Length** - Character count of final answer

## ✅ Validation Checks

Tests automatically validate:

1. **State Completeness** - All required keys present
2. **Message Content** - Non-empty answer generated
3. **Answer Length** - Meets minimum length threshold (50 chars)
4. **Source Count** - At least 1 source cited
5. **Research Loops** - Within configured maximum (3)

## 🔧 Configuration

### Modifying Test Parameters

Edit `test_config.py` to adjust:

```python
# Execution parameters
DEFAULT_MAX_RESEARCH_LOOPS = 2
DEFAULT_INITIAL_QUERIES = 3
DEFAULT_TIMEOUT_SECONDS = 120

# Validation thresholds
THRESHOLDS = {
    "min_sources": 1,
    "max_execution_time": 60,
    "min_answer_length": 50,
    "max_research_loops": 3
}
```

### Adding New Test Queries

Add to `TEST_QUERIES` dictionary in `test_config.py`:

```python
TEST_QUERIES = {
    "factual": [
        {
            "query": "Your new query here",
            "description": "Description of test",
            "expected_sources_min": 1,
            "max_loops": 1
        }
    ]
}
```

## 🐛 Debugging Failed Tests

### View Detailed Logs

1. Check console output for error messages
2. Review JSON report in `test_results/` directory
3. Enable verbose logging: `--verbose` flag

### Common Issues

**Test times out**
- Increase `DEFAULT_TIMEOUT_SECONDS` in config
- Check network connectivity
- Verify API keys are valid

**No sources gathered**
- Query may be too vague or nonsensical
- Google Search API quota may be exceeded
- Check for API errors in logs

**Validation errors**
- Review specific validation failure in output
- Adjust thresholds in `test_config.py` if needed
- Check if answer meets quality standards

## 📝 Writing Custom Tests

### Basic Test Structure

```python
def test_my_custom_query():
    """Test description."""
    return run_test(
        query="My query here",
        test_name="My Test Name",
        max_research_loops=2,
        initial_search_query_count=3
    )
```

### Conversational Test

```python
def test_conversation():
    """Multi-turn conversation."""
    state = run_test(
        query="Initial question",
        test_name="Initial Query"
    )
    
    if state:
        state = run_test(
            query="Follow-up question",
            test_name="Follow-up Query",
            previous_state=state
        )
```

## 🔍 Test Results Interpretation

### Success Criteria

✅ **PASS** - All conditions met:
- Test executed without exceptions
- State contains all required keys
- Answer length >= 50 characters
- At least 1 source cited
- Research loops <= maximum

❌ **FAIL** - Any condition not met:
- Exception raised during execution
- Missing required state keys
- Answer too short or empty
- No sources gathered (where expected)
- Too many research loops

### Performance Benchmarks

Expected execution times (approximate):
- **Factual queries**: 5-15 seconds
- **Comparative queries**: 15-30 seconds
- **Complex research**: 30-60 seconds
- **Conversational (per turn)**: 10-20 seconds

## 🤝 Contributing New Tests

When adding tests:

1. **Categorize properly** - Use existing categories or propose new ones
2. **Set expectations** - Define expected sources, loops, etc.
3. **Document purpose** - Clear description of what's being tested
4. **Consider edge cases** - Test error conditions and unusual inputs
5. **Update README** - Document new test types

## 📚 Related Documentation

- [Main README](../README.md) - Project overview and setup
- [IMPROVEMENTS.md](../IMPROVEMENTS.md) - Code enhancements documentation
- [LangGraph Testing Guide](https://langchain-ai.github.io/langgraph/concepts/testing/)

---

**Last Updated**: January 1, 2026  
**Maintainer**: Development Team

