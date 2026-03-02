"""
Factory module for creating TechnicalQA instances
Provides convenient factory functions for different use cases
"""

import os
from typing import Optional
from .core import TechnicalQA, ModelProvider, ModelConfig

def create_qa_tool(provider: str = "auto", model_name: Optional[str] = None) -> TechnicalQA:
    """
    Factory function to create a TechnicalQA instance.
    
    Args:
        provider: "auto", "openai", "anthropic", "google", "ollama", "openrouter", or "auto" (default)
        model_name: Specific model name to use
        
    Returns:
        Configured TechnicalQA instance
    """
    if provider == "auto":
        return TechnicalQA()
    
    if provider == "openai":
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key or not api_key.startswith("sk-proj-") or "your-key-here" in api_key:
            raise ValueError("Valid OpenAI API key not found")
        
        config = ModelConfig(
            provider=ModelProvider.OPENAI,
            model_name=model_name or "gpt-4o-mini",
            api_key=api_key
        )
    elif provider == "anthropic":
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key or not api_key.startswith("sk-ant-") or "your-key-here" in api_key:
            raise ValueError("Valid Anthropic API key not found")
        
        config = ModelConfig(
            provider=ModelProvider.ANTHROPIC,
            model_name=model_name or "claude-3.5-haiku",
            api_key=api_key
        )
    elif provider == "google":
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key or not api_key.startswith("AIza") or "your-key-here" in api_key:
            raise ValueError("Valid Google API key not found")
        
        config = ModelConfig(
            provider=ModelProvider.GOOGLE,
            model_name=model_name or "gemini-1.5-flash",
            api_key=api_key
        )
    elif provider == "ollama":
        if not TechnicalQA._check_ollama_available(None):
            raise ValueError("Ollama is not running. Please start Ollama with 'ollama serve'")
        
        config = ModelConfig(
            provider=ModelProvider.OLLAMA,
            model_name=model_name or "llama3.2",
            base_url="http://localhost:11434/v1",
            api_key="ollama"
        )
    elif provider == "openrouter":
        api_key = os.getenv('OPENROUTER_API_KEY')
        if not api_key or not api_key.startswith("sk-or-") or "your-key-here" in api_key:
            raise ValueError("Valid OpenRouter API key not found")
        
        config = ModelConfig(
            provider=ModelProvider.OPENROUTER,
            model_name=model_name or "anthropic/claude-3.5-haiku",
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key
        )
    else:
        raise ValueError(f"Unknown provider: {provider}")
    
    return TechnicalQA(config)

def create_openai_qa(model_name: str = "gpt-4o-mini") -> TechnicalQA:
    """Create a TechnicalQA instance configured for OpenAI."""
    return create_qa_tool(provider="openai", model_name=model_name)

def create_anthropic_qa(model_name: str = "claude-3.5-haiku") -> TechnicalQA:
    """Create a TechnicalQA instance configured for Anthropic Claude."""
    return create_qa_tool(provider="anthropic", model_name=model_name)

def create_google_qa(model_name: str = "gemini-1.5-flash") -> TechnicalQA:
    """Create a TechnicalQA instance configured for Google Gemini."""
    return create_qa_tool(provider="google", model_name=model_name)

def create_ollama_qa(model_name: str = "llama3.2") -> TechnicalQA:
    """Create a TechnicalQA instance configured for Ollama."""
    return create_qa_tool(provider="ollama", model_name=model_name)

def create_openrouter_qa(model_name: str = "anthropic/claude-3.5-haiku") -> TechnicalQA:
    """Create a TechnicalQA instance configured for OpenRouter."""
    return create_qa_tool(provider="openrouter", model_name=model_name)
