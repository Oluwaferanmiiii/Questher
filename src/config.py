"""
Configuration management for the Technical QA tool
Handles environment variables and settings
"""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass
from dotenv import load_dotenv

@dataclass
class Settings:
    """Application settings"""
    # OpenAI settings
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4o-mini"
    
    # Ollama settings
    ollama_base_url: str = "http://localhost:11434/v1"
    ollama_model: str = "llama3.2"
    
    # OpenRouter settings
    openrouter_api_key: Optional[str] = None
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    openrouter_model: str = "anthropic/claude-3.5-haiku"
    
    # General settings
    default_temperature: float = 0.7
    default_max_tokens: int = 2000
    request_timeout: int = 30
    
    def __post_init__(self):
        """Load settings from environment variables"""
        load_dotenv(override=True)
        
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.openai_model = os.getenv('OPENAI_MODEL', self.openai_model)
        self.ollama_base_url = os.getenv('OLLAMA_BASE_URL', self.ollama_base_url)
        self.ollama_model = os.getenv('OLLAMA_MODEL', self.ollama_model)
        self.openrouter_api_key = os.getenv('OPENROUTER_API_KEY')
        self.openrouter_base_url = os.getenv('OPENROUTER_BASE_URL', self.openrouter_base_url)
        self.openrouter_model = os.getenv('OPENROUTER_MODEL', self.openrouter_model)
        self.default_temperature = float(os.getenv('DEFAULT_TEMPERATURE', str(self.default_temperature)))
        self.default_max_tokens = int(os.getenv('DEFAULT_MAX_TOKENS', str(self.default_max_tokens)))
        self.request_timeout = int(os.getenv('REQUEST_TIMEOUT', str(self.request_timeout)))
    
    def validate(self) -> Dict[str, Any]:
        """Validate settings and return status"""
        status = {
            "openai_configured": bool(self.openai_api_key and self.openai_api_key.startswith("sk-proj-")),
            "openrouter_configured": bool(self.openrouter_api_key and self.openrouter_api_key.startswith("sk-or-")),
            "ollama_available": False,
            "issues": []
        }
        
        # Check Ollama availability
        try:
            import requests
            response = requests.get("http://localhost:11434", timeout=2)
            status["ollama_available"] = response.status_code == 200
        except:
            status["ollama_available"] = False
        
        # Add validation issues
        if not status["openai_configured"] and not status["openrouter_configured"] and not status["ollama_available"]:
            status["issues"].append("No valid model provider configured")
        
        return status

# Global settings instance
settings = Settings()
