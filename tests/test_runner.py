"""
Advanced Test Runner for Pro-Search Agent
Comprehensive testing with benchmarks, validation, and reporting
"""

import logging
import time
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

from agent import graph
from test_config import (
    TEST_QUERIES,
    TEST_CATEGORIES,
    THRESHOLDS,
    validate_state,
    get_test_summary,
    get_test_environment,
    DEFAULT_MAX_RESEARCH_LOOPS,
    DEFAULT_INITIAL_QUERIES
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TestResult:
    """Container for test execution results."""

    def __init__(self, test_name: str, query: str, category: str):
        self.test_name = test_name
        self.query = query
        self.category = category
        self.success = False
        self.execution_time = 0.0
        self.error_message = None
        self.state = None
        self.validation_errors = []
        self.metrics = {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "test_name": self.test_name,
            "query": self.query,
            "category": self.category,
            "success": self.success,
            "execution_time": self.execution_time,
            "error_message": self.error_message,
            "validation_errors": self.validation_errors,
            "metrics": self.metrics
        }


class TestRunner:
    """Advanced test runner with benchmarking and reporting."""

    def __init__(self, output_dir: str = "test_results"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.results: List[TestResult] = []
        self.start_time = None

    def run_single_test(
        self,
        query: str,
        test_name: str,
        category: str,
        max_research_loops: int = DEFAULT_MAX_RESEARCH_LOOPS,
        initial_queries: int = DEFAULT_INITIAL_QUERIES,
        previous_state: Optional[Dict[str, Any]] = None
    ) -> TestResult:
        """
        Execute a single test case.

        Args:
            query: The query to test
            test_name: Name of the test
            category: Test category
            max_research_loops: Maximum research iterations
            initial_queries: Number of initial queries
            previous_state: Previous state for follow-up queries

        Returns:
            TestResult object with execution details
        """
        result = TestResult(test_name, query, category)

        try:
            logger.info(f"Running test: {test_name}")
            logger.info(f"Query: {query}")

            start = time.time()

            # Prepare input
            if previous_state and previous_state.get("messages"):
                input_data = {
                    "messages": previous_state["messages"] + [{"role": "user", "content": query}]
                }
            else:
                input_data = {
                    "messages": [{"role": "user", "content": query}],
                    "max_research_loops": max_research_loops,
                    "initial_search_query_count": initial_queries
                }

            # Execute
            state = graph.invoke(input_data)
            result.execution_time = time.time() - start
            result.state = state

            # Validate
            result.validation_errors = validate_state(state)
            result.success = len(result.validation_errors) == 0

            # Extract metrics
            result.metrics = {
                "search_queries": len(state.get("search_query", [])),
                "sources_gathered": len(state.get("sources_gathered", [])),
                "research_loops": state.get("research_loop_count", 0),
                "answer_length": len(state["messages"][-1].content) if state.get("messages") else 0
            }

            logger.info(f"Test completed: {test_name} - {'PASS' if result.success else 'FAIL'}")

        except Exception as e:
            result.success = False
            result.error_message = str(e)
            logger.error(f"Test failed: {test_name} - {e}", exc_info=True)

        self.results.append(result)
        return result

    def run_category_tests(self, category: str) -> List[TestResult]:
        """Run all tests in a specific category."""
        if category not in TEST_QUERIES:
            logger.error(f"Unknown category: {category}")
            return []

        logger.info(f"Running {category} tests")
        results = []

        for idx, test_data in enumerate(TEST_QUERIES[category], 1):
            if category == "conversational":
                # Handle conversational tests
                state = None
                initial_query = test_data["initial"]
                test_name = f"{category.title()} Test {idx}: {test_data['description']}"

                # Run initial query
                result = self.run_single_test(
                    initial_query,
                    f"{test_name} - Initial",
                    category
                )
                results.append(result)
                state = result.state

                # Run follow-ups
                for follow_idx, follow_up in enumerate(test_data["follow_ups"], 1):
                    result = self.run_single_test(
                        follow_up,
                        f"{test_name} - Follow-up {follow_idx}",
                        category,
                        previous_state=state
                    )
                    results.append(result)
                    state = result.state
            else:
                # Handle regular tests
                query = test_data["query"]
                test_name = f"{category.title()} Test {idx}: {test_data['description']}"
                max_loops = test_data.get("max_loops", DEFAULT_MAX_RESEARCH_LOOPS)

                result = self.run_single_test(
                    query,
                    test_name,
                    category,
                    max_research_loops=max_loops
                )
                results.append(result)

        return results

    def run_all_tests(self):
        """Run all test categories."""
        self.start_time = time.time()
        logger.info("Starting comprehensive test suite")

        for category in TEST_QUERIES.keys():
            self.run_category_tests(category)

        total_time = time.time() - self.start_time
        logger.info(f"All tests completed in {total_time:.2f} seconds")

    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report."""
        total = len(self.results)
        passed = sum(1 for r in self.results if r.success)
        failed = total - passed

        # Calculate metrics
        total_time = sum(r.execution_time for r in self.results)
        avg_time = total_time / total if total > 0 else 0

        # Group by category
        by_category = {}
        for result in self.results:
            if result.category not in by_category:
                by_category[result.category] = []
            by_category[result.category].append(result)

        category_summary = {}
        for category, results in by_category.items():
            cat_passed = sum(1 for r in results if r.success)
            category_summary[category] = {
                "total": len(results),
                "passed": cat_passed,
                "failed": len(results) - cat_passed,
                "success_rate": (cat_passed / len(results) * 100) if results else 0
            }

        report = {
            "summary": {
                "total_tests": total,
                "passed": passed,
                "failed": failed,
                "success_rate": (passed / total * 100) if total > 0 else 0,
                "total_execution_time": total_time,
                "average_execution_time": avg_time
            },
            "by_category": category_summary,
            "environment": get_test_environment(),
            "thresholds": THRESHOLDS,
            "detailed_results": [r.to_dict() for r in self.results]
        }

        return report

    def save_report(self, filename: Optional[str] = None):
        """Save test report to JSON file."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"test_report_{timestamp}.json"

        filepath = self.output_dir / filename
        report = self.generate_report()

        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)

        logger.info(f"Report saved to {filepath}")
        return filepath

    def print_summary(self):
        """Print formatted test summary to console."""
        report = self.generate_report()
        summary = report["summary"]

        print("\n" + "=" * 80)
        print(" TEST SUMMARY ".center(80, "="))
        print("=" * 80)
        print(f"\nTotal Tests:     {summary['total_tests']}")
        print(f"✅ Passed:       {summary['passed']}")
        print(f"❌ Failed:       {summary['failed']}")
        print(f"Success Rate:   {summary['success_rate']:.1f}%")
        print(f"Total Time:     {summary['total_execution_time']:.2f}s")
        print(f"Average Time:   {summary['average_execution_time']:.2f}s")

        print("\n" + "-" * 80)
        print(" BY CATEGORY ".center(80, "-"))
        print("-" * 80)

        for category, stats in report["by_category"].items():
            print(f"\n{category.upper()}:")
            print(f"  Total: {stats['total']}, Passed: {stats['passed']}, "
                  f"Failed: {stats['failed']}, Success: {stats['success_rate']:.1f}%")

        print("\n" + "=" * 80)

        # Print failures
        failures = [r for r in self.results if not r.success]
        if failures:
            print("\n" + "!" * 80)
            print(" FAILED TESTS ".center(80, "!"))
            print("!" * 80)
            for result in failures:
                print(f"\n❌ {result.test_name}")
                print(f"   Query: {result.query}")
                if result.error_message:
                    print(f"   Error: {result.error_message}")
                if result.validation_errors:
                    print(f"   Validation Errors: {', '.join(result.validation_errors)}")
            print("\n" + "!" * 80)


def main():
    """Main entry point for advanced test runner."""
    import argparse

    parser = argparse.ArgumentParser(description="Pro-Search Agent Advanced Test Runner")
    parser.add_argument(
        "category",
        nargs="?",
        choices=list(TEST_QUERIES.keys()) + ["all"],
        default="all",
        help="Test category to run (default: all)"
    )
    parser.add_argument(
        "--output-dir",
        default="test_results",
        help="Directory for test results (default: test_results)"
    )
    parser.add_argument(
        "--no-report",
        action="store_true",
        help="Don't save JSON report"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Create test runner
    runner = TestRunner(output_dir=args.output_dir)

    # Run tests
    if args.category == "all":
        runner.run_all_tests()
    else:
        runner.run_category_tests(args.category)

    # Print summary
    runner.print_summary()

    # Save report
    if not args.no_report:
        report_path = runner.save_report()
        print(f"\n📄 Full report saved to: {report_path}")

    # Exit code
    report = runner.generate_report()
    sys.exit(0 if report["summary"]["failed"] == 0 else 1)


if __name__ == "__main__":
    main()

