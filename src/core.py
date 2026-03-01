"""
Core module for Technical Question Answering Tool
Contains the main TechnicalQA class and related components
"""

import os
import sys
from typing import Optional, List, Dict, Any, Generator
from dataclasses import dataclass
from enum import Enum
import json
from dotenv import load_dotenv
from openai import OpenAI
import requests

class ModelProvider(Enum):
    """Supported LLM providers"""
    OPENAI = "openai"
    OLLAMA = "ollama"
    OPENROUTER = "openrouter"

@dataclass
class ModelConfig:
    """Configuration for model providers"""
    provider: ModelProvider
    model_name: str
    base_url: Optional[str] = None
    api_key: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 2000

class TechnicalQA:
    """
    Enterprise-grade technical question answering tool that supports
    multiple LLM providers with streaming capabilities.
    """
    
    def __init__(self, config: Optional[ModelConfig] = None):
        """Initialize the Technical QA tool with model configuration."""
        load_dotenv(override=True)
        
        if config is None:
            config = self._detect_default_config()
        
        self.config = config
        self.client = self._initialize_client()
        self.system_prompt = self._get_system_prompt()
    
    def _detect_default_config(self) -> ModelConfig:
        """Auto-detect the best available model configuration."""
        # Check for Ollama first (free, local option)
        if self._check_ollama_available():
            return ModelConfig(
                provider=ModelProvider.OLLAMA,
                model_name="llama3.2",
                base_url="http://localhost:11434/v1",
                api_key="ollama"
            )
        
        # Check for OpenRouter (multi-provider, cost-effective)
        openrouter_key = os.getenv('OPENROUTER_API_KEY')
        if openrouter_key and openrouter_key.startswith("sk-or-"):
            return ModelConfig(
                provider=ModelProvider.OPENROUTER,
                model_name="anthropic/claude-3.5-haiku",
                base_url="https://openrouter.ai/api/v1",
                api_key=openrouter_key
            )
        
        # Fall back to OpenAI
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key and api_key.startswith("sk-proj-"):
            return ModelConfig(
                provider=ModelProvider.OPENAI,
                model_name="gpt-4o-mini",
                api_key=api_key
            )
        
        raise ValueError("No valid model configuration found. Please set up OpenAI API key, OpenRouter API key, or install Ollama.")
    
    def _check_ollama_available(self) -> bool:
        """Check if Ollama is running and accessible."""
        try:
            response = requests.get("http://localhost:11434", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def _initialize_client(self) -> OpenAI:
        """Initialize the appropriate OpenAI client based on provider."""
        if self.config.provider == ModelProvider.OLLAMA:
            return OpenAI(
                base_url=self.config.base_url,
                api_key=self.config.api_key
            )
        elif self.config.provider == ModelProvider.OPENROUTER:
            return OpenAI(
                base_url=self.config.base_url,
                api_key=self.config.api_key,
                default_headers={
                    "HTTP-Referer": "https://github.com/week1-solution",
                    "X-Title": "Week 1 Technical QA Tool"
                }
            )
        else:
            return OpenAI(api_key=self.config.api_key)
    
    def _get_system_prompt(self) -> str:
        """Get the optimized system prompt for technical explanations."""
        return """You are an expert Software Developer Assistant. Your role is to:

1. Provide clear, accurate technical explanations
2. Include practical code examples when relevant
3. Explain concepts in a way that's easy to understand
4. Use proper markdown formatting with code blocks
5. Include best practices and common pitfalls when applicable
6. Be thorough but concise

Always format your responses in markdown with:
- Clear headings for different sections
- Syntax-highlighted code blocks using appropriate language tags
- Bullet points for key concepts
- Examples that can be directly copied and tested

If the user asks about specific code, explain:
- What the code does step by step
- Why it works that way
- Potential improvements or alternatives
- Common use cases"""

    def ask_question(self, question: str, stream: bool = False) -> str:
        """
        Ask a technical question and get an explanation.
        
        Args:
            question: The technical question to answer
            stream: Whether to stream the response
            
        Returns:
            The technical explanation as a string
        """
        if stream:
            return "".join(self.ask_question_stream(question))
        
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": question}
        ]
        
        try:
            response = self.client.chat.completions.create(
                model=self.config.model_name,
                messages=messages,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error generating response: {str(e)}"
    
    def ask_question_stream(self, question: str) -> Generator[str, None, None]:
        """
        Ask a technical question and stream the response.
        
        Args:
            question: The technical question to answer
            
        Yields:
            Chunks of the response as they're generated
        """
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": question}
        ]
        
        try:
            stream = self.client.chat.completions.create(
                model=self.config.model_name,
                messages=messages,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                stream=True
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            yield f"Error generating response: {str(e)}"
    
    def compare_models(self, question: str) -> Dict[str, str]:
        """
        Compare responses from different models if available.
        
        Args:
            question: The technical question to answer
            
        Returns:
            Dictionary with model names as keys and responses as values
        """
        results = {}
        
        # Try current model
        results[self.config.model_name] = self.ask_question(question)
        
        # Try alternative model if available
        if self.config.provider == ModelProvider.OPENAI:
            # Try to use Ollama if available
            if self._check_ollama_available():
                try:
                    ollama_config = ModelConfig(
                        provider=ModelProvider.OLLAMA,
                        model_name="llama3.2",
                        base_url="http://localhost:11434/v1",
                        api_key="ollama"
                    )
                    ollama_qa = TechnicalQA(ollama_config)
                    results["llama3.2 (Ollama)"] = ollama_qa.ask_question(question)
                except:
                    pass
        else:
            # Try to use OpenAI if API key is available
            api_key = os.getenv('OPENAI_API_KEY')
            if api_key and api_key.startswith("sk-proj-"):
                try:
                    openai_config = ModelConfig(
                        provider=ModelProvider.OPENAI,
                        model_name="gpt-4o-mini",
                        api_key=api_key
                    )
                    openai_qa = TechnicalQA(openai_config)
                    results["gpt-4o-mini (OpenAI)"] = openai_qa.ask_question(question)
                except:
                    pass
        
        return results
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model configuration."""
        return {
            "provider": self.config.provider.value,
            "model_name": self.config.model_name,
            "base_url": self.config.base_url,
            "api_key_set": bool(self.config.api_key),
            "ollama_available": self._check_ollama_available(),
            "openai_available": bool(os.getenv('OPENAI_API_KEY') and os.getenv('OPENAI_API_KEY').startswith("sk-proj-"))
        }
