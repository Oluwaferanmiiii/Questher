"""
Test configuration and utilities
"""

import pytest
import sys
import os
from pathlib import Path

# Add src directory to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

@pytest.fixture
def mock_openai_key():
    """Fixture to provide mock OpenAI API key"""
    return "sk-proj-mock-key-for-testing"

@pytest.fixture
def mock_ollama_response():
    """Mock Ollama health check response"""
    class MockResponse:
        def __init__(self):
            self.status_code = 200
        @property
        def content(self):
            return b"Ollama is running"
    return MockResponse()

@pytest.fixture
def sample_technical_questions():
    """Sample technical questions for testing"""
    return [
        "What is a Python generator?",
        "How does async/await work in JavaScript?",
        "Explain the difference between list and tuple in Python",
        "What is a REST API?",
        "How do you implement a binary search tree?"
    ]
