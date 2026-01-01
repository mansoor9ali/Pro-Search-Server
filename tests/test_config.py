"""
Test configuration and constants for Pro-Search Agent tests
Centralized configuration for test scenarios and parameters
"""

from typing import Dict, List, Any

# Test execution parameters
DEFAULT_MAX_RESEARCH_LOOPS = 2
DEFAULT_INITIAL_QUERIES = 3
DEFAULT_TIMEOUT_SECONDS = 120

# Test categories
TEST_CATEGORIES = {
    "factual": "Tests for simple factual queries",
    "comparative": "Tests for comparative analysis",
    "technical": "Tests for technical documentation",
    "complex": "Tests for complex multi-step research",
    "conversational": "Tests for follow-up questions",
    "edge_case": "Tests for edge cases and error handling"
}

# Expected behavior thresholds
THRESHOLDS = {
    "min_sources": 1,
    "max_execution_time": 60,  # seconds
    "min_answer_length": 50,  # characters
    "max_research_loops": 3
}

# Test queries by category
TEST_QUERIES = {
    "factual": [
        {
            "query": "Who won the euro 2024",
            "description": "Simple factual query about recent event",
            "expected_sources_min": 1,
            "max_loops": 1
        },
        {
            "query": "What is the capital of Japan?",
            "description": "Basic geography question",
            "expected_sources_min": 1,
            "max_loops": 1
        },
        {
            "query": "When was Python programming language created?",
            "description": "Historical fact about technology",
            "expected_sources_min": 1,
            "max_loops": 1
        }
    ],
    "comparative": [
        {
            "query": "Compare Python and JavaScript performance",
            "description": "Technical comparison requiring multiple sources",
            "expected_sources_min": 2,
            "max_loops": 2
        },
        {
            "query": "Differences between GPT-4 and Claude 3",
            "description": "AI model comparison",
            "expected_sources_min": 2,
            "max_loops": 2
        },
        {
            "query": "Compare React, Vue, and Angular frameworks",
            "description": "Multi-way framework comparison",
            "expected_sources_min": 3,
            "max_loops": 2
        }
    ],
    "technical": [
        {
            "query": "How to implement async/await in Python?",
            "description": "Technical how-to query",
            "expected_sources_min": 1,
            "max_loops": 2
        },
        {
            "query": "Best practices for Docker containerization",
            "description": "Technical best practices",
            "expected_sources_min": 2,
            "max_loops": 2
        },
        {
            "query": "LangGraph streaming API documentation",
            "description": "Specific API documentation",
            "expected_sources_min": 1,
            "max_loops": 2
        }
    ],
    "complex": [
        {
            "query": "What are the latest AI developments in 2025 and their impact on software engineering?",
            "description": "Complex multi-faceted research",
            "expected_sources_min": 3,
            "max_loops": 3
        },
        {
            "query": "Explain quantum computing breakthroughs and list companies working on it",
            "description": "Complex query with multiple aspects",
            "expected_sources_min": 3,
            "max_loops": 2
        },
        {
            "query": "Analyze the state of electric vehicles market, key players, and future predictions",
            "description": "Market analysis with predictions",
            "expected_sources_min": 3,
            "max_loops": 2
        }
    ],
    "conversational": [
        {
            "initial": "Who is Elon Musk?",
            "follow_ups": [
                "What companies does he own?",
                "Which is the most valuable?"
            ],
            "description": "Multi-turn conversation"
        },
        {
            "initial": "What is machine learning?",
            "follow_ups": [
                "What are the main types?",
                "Give examples of supervised learning"
            ],
            "description": "Educational conversation"
        }
    ],
    "edge_case": [
        {
            "query": "",
            "description": "Empty query",
            "should_fail": True
        },
        {
            "query": "asdfghjkl qwertyuiop",
            "description": "Nonsensical query",
            "expected_sources_min": 0
        },
        {
            "query": "What is the meaning of life, universe, and everything?",
            "description": "Philosophical/ambiguous query",
            "expected_sources_min": 1
        }
    ]
}

# Validation functions
def validate_state(state: Dict[str, Any]) -> List[str]:
    """
    Validate the state returned by the graph execution.

    Args:
        state: The state dictionary to validate

    Returns:
        List of validation errors (empty if valid)
    """
    errors = []

    if not state:
        errors.append("State is None or empty")
        return errors

    # Check for required keys
    required_keys = ["messages", "search_query", "sources_gathered"]
    for key in required_keys:
        if key not in state:
            errors.append(f"Missing required key: {key}")

    # Validate messages
    if "messages" in state:
        if not state["messages"]:
            errors.append("Messages list is empty")
        elif not hasattr(state["messages"][-1], "content"):
            errors.append("Last message has no content attribute")
        elif not state["messages"][-1].content:
            errors.append("Last message content is empty")
        elif len(state["messages"][-1].content) < THRESHOLDS["min_answer_length"]:
            errors.append(f"Answer too short: {len(state['messages'][-1].content)} chars")

    # Validate sources
    if "sources_gathered" in state:
        if not isinstance(state["sources_gathered"], list):
            errors.append("sources_gathered is not a list")
        elif len(state["sources_gathered"]) < THRESHOLDS["min_sources"]:
            errors.append(f"Too few sources: {len(state['sources_gathered'])}")

    # Validate research loops
    if "research_loop_count" in state:
        if state["research_loop_count"] > THRESHOLDS["max_research_loops"]:
            errors.append(f"Too many research loops: {state['research_loop_count']}")

    return errors


def get_test_summary(test_results: List[tuple]) -> Dict[str, Any]:
    """
    Generate a summary of test results.

    Args:
        test_results: List of (test_name, success, execution_time) tuples

    Returns:
        Dictionary with summary statistics
    """
    total = len(test_results)
    passed = sum(1 for _, success, _ in test_results if success)
    failed = total - passed

    total_time = sum(time for _, _, time in test_results if time)
    avg_time = total_time / total if total > 0 else 0

    return {
        "total": total,
        "passed": passed,
        "failed": failed,
        "success_rate": (passed / total * 100) if total > 0 else 0,
        "total_time": total_time,
        "average_time": avg_time
    }


# Model configuration presets
MODEL_CONFIGS = {
    "fast": {
        "query_generator_model": "gemini-2.0-flash",
        "reflection_model": "gemini-2.0-flash",
        "answer_model": "gemini-2.5-flash",
        "description": "Fast execution with lighter models"
    },
    "balanced": {
        "query_generator_model": "gemini-2.0-flash",
        "reflection_model": "gemini-2.5-flash",
        "answer_model": "gemini-2.5-pro",
        "description": "Balanced speed and quality (default)"
    },
    "quality": {
        "query_generator_model": "gemini-2.5-flash",
        "reflection_model": "gemini-2.5-pro",
        "answer_model": "gemini-2.5-pro",
        "description": "Maximum quality with slower execution"
    }
}

# Test environment info
def get_test_environment() -> Dict[str, str]:
    """Get information about the test environment."""
    import os
    import sys
    from datetime import datetime

    return {
        "python_version": sys.version,
        "platform": sys.platform,
        "timestamp": datetime.now().isoformat(),
        "gemini_api_configured": "GEMINI_API_KEY" in os.environ,
        "langsmith_enabled": os.getenv("LANGSMITH_TRACING", "false").lower() == "true"
    }

