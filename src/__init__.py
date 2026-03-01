"""
Week 1 Technical Question Answering Tool
Enterprise-grade LLM application for technical question answering
"""

__version__ = "1.0.0"
__author__ = "Week 1 Solution Team"
__email__ = "team@week1-solution.com"

from .core import TechnicalQA, ModelProvider, ModelConfig
from .factory import create_qa_tool

__all__ = [
    "TechnicalQA",
    "ModelProvider", 
    "ModelConfig",
    "create_qa_tool"
]
