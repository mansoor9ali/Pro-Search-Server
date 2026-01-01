"""
Test suite for Pro-Search Agent
Tests various research scenarios and validates agent functionality
"""

import logging
import time
from datetime import datetime
from typing import Dict, Any, List

from agent import graph

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def print_separator(title: str = "", char: str = "=", width: int = 80):
    """Print a formatted separator line."""
    if title:
        title_str = f" {title} "
        padding = (width - len(title_str)) // 2
        print(f"\n{char * padding}{title_str}{char * padding}")
    else:
        print(f"\n{char * width}")


def print_result(state: Dict[str, Any], test_name: str, execution_time: float):
    """Print formatted test results."""
    print_separator(test_name, "=")
    print(f"⏱️  Execution Time: {execution_time:.2f} seconds")
    print(f"🔍 Search Queries: {len(state.get('search_query', []))}")
    print(f"📚 Sources Gathered: {len(state.get('sources_gathered', []))}")
    print(f"🔄 Research Loops: {state.get('research_loop_count', 0)}")
    print_separator("Answer", "-")
    print(state["messages"][-1].content)

    # Print sources if available
    if state.get('sources_gathered'):
        print_separator("Sources", "-")
        for idx, source in enumerate(state['sources_gathered'][:5], 1):  # Show first 5
            print(f"{idx}. {source.get('label', 'Source')}: {source.get('value', 'N/A')}")
        if len(state['sources_gathered']) > 5:
            print(f"... and {len(state['sources_gathered']) - 5} more sources")
    print_separator()


def run_test(
    query: str,
    test_name: str,
    max_research_loops: int = 2,
    initial_search_query_count: int = 3,
    previous_state: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Run a single test case with the Pro-Search agent.

    Args:
        query: The user query to test
        test_name: Name of the test for logging
        max_research_loops: Maximum research iterations
        initial_search_query_count: Number of initial search queries
        previous_state: Previous conversation state for follow-up queries

    Returns:
        The resulting state after graph execution
    """
    try:
        logger.info(f"Starting test: {test_name}")
        logger.info(f"Query: {query}")

        start_time = time.time()

        # Prepare input
        if previous_state and previous_state.get("messages"):
            # Follow-up question
            input_data = {
                "messages": previous_state["messages"] + [{"role": "user", "content": query}]
            }
        else:
            # New conversation
            input_data = {
                "messages": [{"role": "user", "content": query}],
                "max_research_loops": max_research_loops,
                "initial_search_query_count": initial_search_query_count
            }

        # Invoke the graph
        state = graph.invoke(input_data)

        execution_time = time.time() - start_time

        # Print results
        print_result(state, test_name, execution_time)

        logger.info(f"Test completed: {test_name} in {execution_time:.2f}s")
        return state

    except Exception as e:
        logger.error(f"Test failed: {test_name}")
        logger.error(f"Error: {e}", exc_info=True)
        print_separator(f"❌ TEST FAILED: {test_name}", "!")
        print(f"Error: {str(e)}")
        print_separator()
        return None


def test_basic_factual_query():
    """Test 1: Basic factual query with current events."""
    return run_test(
        query="Who won the euro 2024",
        test_name="Test 1: Basic Factual Query",
        max_research_loops=3,
        initial_search_query_count=3
    )


def test_follow_up_query(previous_state: Dict[str, Any]):
    """Test 2: Follow-up question with context."""
    if not previous_state:
        logger.warning("Skipping follow-up test due to previous test failure")
        return None

    return run_test(
        query="Who has the most titles? List the top 5",
        test_name="Test 2: Follow-up Query with Context",
        previous_state=previous_state
    )


def test_complex_research_query():
    """Test 3: Complex multi-faceted research query."""
    return run_test(
        query="What are the latest developments in quantum computing in 2025? Include key breakthroughs and companies involved.",
        test_name="Test 3: Complex Research Query",
        max_research_loops=2,
        initial_search_query_count=3
    )


def test_comparative_analysis():
    """Test 4: Comparative analysis requiring multiple sources."""
    return run_test(
        query="Compare the features and pricing of ChatGPT Plus, Claude Pro, and Gemini Advanced",
        test_name="Test 4: Comparative Analysis",
        max_research_loops=2,
        initial_search_query_count=3
    )


def test_technical_query():
    """Test 5: Technical documentation query."""
    return run_test(
        query="How do I implement streaming responses in LangGraph?",
        test_name="Test 5: Technical Documentation Query",
        max_research_loops=2,
        initial_search_query_count=2
    )


def test_minimal_research():
    """Test 6: Simple query with minimal research loops."""
    return run_test(
        query="What is the capital of France?",
        test_name="Test 6: Minimal Research Query",
        max_research_loops=1,
        initial_search_query_count=1
    )


def run_all_tests():
    """Run all test cases."""
    print_separator("PRO-SEARCH AGENT TEST SUITE", "=")
    print(f"Test Run Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print_separator()

    total_start = time.time()
    test_results = []

    # Test 1: Basic factual query
    state1 = test_basic_factual_query()
    test_results.append(("Basic Factual Query", state1 is not None))

    # Test 2: Follow-up query (depends on Test 1)
    state2 = test_follow_up_query(state1)
    test_results.append(("Follow-up Query", state2 is not None))

    # Test 3: Complex research
    state3 = test_complex_research_query()
    test_results.append(("Complex Research", state3 is not None))

    # Test 4: Comparative analysis
    state4 = test_comparative_analysis()
    test_results.append(("Comparative Analysis", state4 is not None))

    # Test 5: Technical query
    state5 = test_technical_query()
    test_results.append(("Technical Query", state5 is not None))

    # Test 6: Minimal research
    state6 = test_minimal_research()
    test_results.append(("Minimal Research", state6 is not None))

    # Summary
    total_time = time.time() - total_start
    passed = sum(1 for _, success in test_results if success)
    failed = len(test_results) - passed

    print_separator("TEST SUMMARY", "=")
    print(f"Total Tests: {len(test_results)}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"⏱️  Total Execution Time: {total_time:.2f} seconds")
    print_separator()

    # Detailed results
    print("Detailed Results:")
    for test_name, success in test_results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {status} - {test_name}")

    print_separator("TEST RUN COMPLETED", "=")

    return passed == len(test_results)


def run_interactive_mode():
    """Run in interactive mode for manual testing."""
    print_separator("INTERACTIVE MODE", "=")
    print("Enter your queries (type 'exit' or 'quit' to stop)")
    print("Type 'new' to start a new conversation")
    print_separator()

    state = None
    conversation_count = 0

    while True:
        try:
            query = input("\n🔍 Your query: ").strip()

            if query.lower() in ['exit', 'quit']:
                print("👋 Goodbye!")
                break

            if query.lower() == 'new':
                state = None
                conversation_count += 1
                print(f"🆕 Started new conversation #{conversation_count}")
                continue

            if not query:
                print("⚠️  Please enter a query")
                continue

            # Run the query
            state = run_test(
                query=query,
                test_name=f"Interactive Query #{conversation_count + 1}",
                max_research_loops=2,
                initial_search_query_count=3,
                previous_state=state
            )

        except KeyboardInterrupt:
            print("\n\n👋 Interrupted. Goodbye!")
            break
        except Exception as e:
            logger.error(f"Error in interactive mode: {e}", exc_info=True)
            print(f"❌ Error: {e}")


if __name__ == '__main__':
    import sys

    # Check command line arguments
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()

        if mode == 'interactive':
            run_interactive_mode()
        elif mode == 'all':
            success = run_all_tests()
            sys.exit(0 if success else 1)
        elif mode.startswith('test'):
            # Run specific test
            test_map = {
                'test1': test_basic_factual_query,
                'test2': lambda: test_follow_up_query(test_basic_factual_query()),
                'test3': test_complex_research_query,
                'test4': test_comparative_analysis,
                'test5': test_technical_query,
                'test6': test_minimal_research,
            }

            if mode in test_map:
                test_map[mode]()
            else:
                print(f"Unknown test: {mode}")
                print(f"Available tests: {', '.join(test_map.keys())}")
        else:
            print("Usage: python test-pro-search-agent.py [mode]")
            print("Modes:")
            print("  all          - Run all tests")
            print("  interactive  - Interactive query mode")
            print("  test1-test6  - Run specific test")
            print("  (no args)    - Run default tests")
    else:
        # Default: Run the original two tests
        print_separator("RUNNING DEFAULT TESTS", "=")
        state1 = test_basic_factual_query()
        if state1:
            test_follow_up_query(state1)
