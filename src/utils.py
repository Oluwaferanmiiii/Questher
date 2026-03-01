"""
Utilities module for Technical QA tool
Helper functions and utilities
"""

import time
import logging
from typing import Dict, Any, Generator
from functools import wraps

def setup_logging(level: str = "INFO") -> logging.Logger:
    """Setup logging configuration"""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

def timing_decorator(func):
    """Decorator to measure execution time"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        if hasattr(result, '__iter__') and not isinstance(result, str):
            # Handle generators
            def timed_generator():
                for item in result:
                    yield item
                print(f"{func.__name__} took {end_time - start_time:.2f} seconds")
            return timed_generator()
        else:
            print(f"{func.__name__} took {end_time - start_time:.2f} seconds")
            return result
    
    return wrapper

def calculate_metrics(question: str, answer: str, response_time: float) -> Dict[str, Any]:
    """Calculate performance metrics for a Q&A interaction"""
    return {
        "question_length": len(question),
        "answer_length": len(answer),
        "word_count": len(answer.split()),
        "response_time": response_time,
        "words_per_second": len(answer.split()) / response_time if response_time > 0 else 0,
        "characters_per_second": len(answer) / response_time if response_time > 0 else 0
    }

def format_response_time(seconds: float) -> str:
    """Format response time in human readable format"""
    if seconds < 1:
        return f"{seconds * 1000:.0f}ms"
    else:
        return f"{seconds:.2f}s"

def validate_question(question: str) -> bool:
    """Validate if a question is appropriate for technical Q&A"""
    if not question or not question.strip():
        return False
    
    question = question.strip().lower()
    
    # Basic checks
    if len(question) < 10:
        return False
    
    # Check if it's a technical question (simple heuristic)
    technical_keywords = [
        'code', 'function', 'class', 'method', 'algorithm', 'data structure',
        'programming', 'software', 'development', 'api', 'database', 'web',
        'python', 'javascript', 'java', 'c++', 'html', 'css', 'sql',
        'how to', 'what is', 'explain', 'difference', 'implement',
        'debug', 'error', 'bug', 'fix', 'solve', 'optimize'
    ]
    
    return any(keyword in question for keyword in technical_keywords)
