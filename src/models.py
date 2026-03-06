#!/usr/bin/env python3
"""
Models Module for Questher v3
Contains ModelManager class for handling AI model operations
"""

from typing import List, Dict, Any
from src.core import ModelProvider


class ModelManager:
    """Manages AI models for different providers"""
    
    def __init__(self):
        self.models = {}
        self.initialize_models()
    
    def initialize_models(self):
        """Initialize models for all providers"""
        # OpenRouter models
        self.models["openrouter"] = [
            "openai/gpt-5",
            "openai/gpt-4o-audio-preview", 
            "anthropic/claude-3.5-sonnet",
            "anthropic/claude-3.5-haiku",
            "google/gemini-2.0-flash-exp",
            "google/gemini-2.5-pro",
            "xai/grok-4",
            "meta-llama/llama-3.1-405b-instruct"
        ]
        
        # OpenAI models
        self.models["openai"] = [
            "gpt-5",
            "gpt-4o",
            "gpt-4o-audio-preview",
            "gpt-4-turbo",
            "gpt-3.5-turbo"
        ]
        
        # Anthropic models
        self.models["anthropic"] = [
            "claude-3.5-sonnet",
            "claude-3.5-haiku",
            "claude-3-opus"
        ]
        
        # Google models
        self.models["google"] = [
            "gemini-2.0-flash-exp",
            "gemini-2.5-pro",
            "gemini-1.5-pro",
            "gemini-1.5-flash"
        ]
        
        # Ollama models
        self.models["ollama"] = [
            "llama3.1:405b",
            "llama3.1:70b",
            "llama3.1:8b",
            "qwen2.5-coder:32b",
            "deepseek-coder-v2:16b"
        ]
    
    def get_display_models(self, provider: str, limit: int = 5) -> List[str]:
        """Get display models for a provider (limited list)"""
        if provider not in self.models:
            return [f"{provider}-default"]
        
        models = self.models[provider]
        return models[:limit] if limit > 0 else models
    
    def get_all_models_for_scroll(self, provider: str) -> List[str]:
        """Get all models for scrollable dropdown"""
        if provider not in self.models:
            return [f"{provider}-default"]
        
        return self.models[provider]
    
    def get_code_generation_models(self) -> List[str]:
        """Get models suitable for code generation"""
        code_models = [
            "openai/gpt-5",
            "anthropic/claude-3.5-sonnet",
            "google/gemini-2.5-pro",
            "xai/grok-4",
            "meta-llama/llama-3.1-405b-instruct"
        ]
        return code_models
    
    def get_provider_for_model(self, model_name: str) -> str:
        """Determine provider for a given model"""
        # Check for OpenRouter prefixed models first
        if "/" in model_name:
            return "openrouter"
        
        # Then check for specific model patterns
        if "gpt" in model_name.lower():
            return "openai"
        elif "claude" in model_name.lower():
            return "anthropic"
        elif "gemini" in model_name.lower():
            return "google"
        elif "grok" in model_name.lower():
            return "grok"
        elif "llama" in model_name.lower() or "qwen" in model_name.lower():
            return "ollama"
        else:
            return "openrouter"  # Default to OpenRouter
