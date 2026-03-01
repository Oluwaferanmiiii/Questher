"""
Exceptions module for Technical QA tool
Custom exceptions for better error handling
"""

class TechnicalQAError(Exception):
    """Base exception for Technical QA tool"""
    pass

class ModelNotAvailableError(TechnicalQAError):
    """Raised when requested model is not available"""
    pass

class ConfigurationError(TechnicalQAError):
    """Raised when configuration is invalid"""
    pass

class APIError(TechnicalQAError):
    """Raised when API call fails"""
    pass

class OllamaNotRunningError(TechnicalQAError):
    """Raised when Ollama is not running"""
    pass

class InvalidAPIKeyError(TechnicalQAError):
    """Raised when API key is invalid"""
    pass
