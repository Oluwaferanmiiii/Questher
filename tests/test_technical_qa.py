"""
Test suite for Technical QA tool
Enterprise-grade testing with pytest
"""

import pytest
import os
from unittest.mock import Mock, patch, MagicMock
from src.core import TechnicalQA, ModelProvider, ModelConfig
from src.factory import create_qa_tool, create_openai_qa, create_ollama_qa
from src.exceptions import ModelNotAvailableError, ConfigurationError
from src.config import settings

class TestModelConfig:
    """Test ModelConfig dataclass"""
    
    def test_model_config_creation(self):
        """Test creating ModelConfig with minimal parameters"""
        config = ModelConfig(
            provider=ModelProvider.OPENAI,
            model_name="gpt-4o-mini"
        )
        assert config.provider == ModelProvider.OPENAI
        assert config.model_name == "gpt-4o-mini"
        assert config.temperature == 0.7
        assert config.max_tokens == 2000
    
    def test_model_config_with_all_parameters(self):
        """Test creating ModelConfig with all parameters"""
        config = ModelConfig(
            provider=ModelProvider.OLLAMA,
            model_name="llama3.2",
            base_url="http://localhost:11434/v1",
            api_key="ollama",
            temperature=0.5,
            max_tokens=1500
        )
        assert config.provider == ModelProvider.OLLAMA
        assert config.model_name == "llama3.2"
        assert config.base_url == "http://localhost:11434/v1"
        assert config.api_key == "ollama"
        assert config.temperature == 0.5
        assert config.max_tokens == 1500

class TestTechnicalQA:
    """Test TechnicalQA class"""
    
    @patch('src.core.requests.get')
    def test_detect_ollama_available(self, mock_get):
        """Test Ollama availability detection"""
        # Test when Ollama is available
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        with patch.dict(os.environ, {'OPENAI_API_KEY': ''}):
            qa = TechnicalQA()
            assert qa.config.provider == ModelProvider.OLLAMA
            assert qa.config.model_name == "llama3.2"
    
    @patch('src.core.requests.get')
    def test_detect_openai_fallback(self, mock_get):
        """Test OpenAI fallback when Ollama is not available"""
        # Test when Ollama is not available
        mock_get.side_effect = Exception("Connection failed")
        
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'sk-proj-test-key'}):
            qa = TechnicalQA()
            assert qa.config.provider == ModelProvider.OPENAI
            assert qa.config.model_name == "gpt-4o-mini"
    
    def test_no_valid_configuration(self):
        """Test error when no valid configuration is found"""
        with patch.dict(os.environ, {'OPENAI_API_KEY': ''}, clear=False):
            with patch('src.core.requests.get', side_effect=Exception("Connection failed")):
                with pytest.raises(ValueError, match="No valid model configuration found"):
                    TechnicalQA()
    
    @patch('src.core.OpenAI')
    def test_openai_client_initialization(self, mock_openai):
        """Test OpenAI client initialization"""
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'sk-proj-test-key'}):
            with patch('src.core.requests.get', side_effect=Exception("Connection failed")):
                qa = TechnicalQA()
                mock_openai.assert_called_once_with(api_key='sk-proj-test-key')
    
    @patch('src.core.OpenAI')
    def test_ollama_client_initialization(self, mock_openai):
        """Test Ollama client initialization"""
        mock_response = Mock()
        mock_response.status_code = 200
        
        with patch('src.core.requests.get', return_value=mock_response):
            with patch.dict(os.environ, {'OPENAI_API_KEY': ''}):
                qa = TechnicalQA()
                mock_openai.assert_called_once_with(
                    base_url="http://localhost:11434/v1",
                    api_key="ollama"
                )
    
    def test_system_prompt_content(self):
        """Test system prompt content"""
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'sk-proj-test-key'}):
            with patch('src.core.requests.get', side_effect=Exception("Connection failed")):
                qa = TechnicalQA()
                prompt = qa.system_prompt
                assert "Software Developer Assistant" in prompt
                assert "markdown" in prompt
                assert "code examples" in prompt

class TestFactory:
    """Test factory functions"""
    
    def test_create_qa_tool_auto(self):
        """Test auto-detection in factory"""
        with patch('src.core.TechnicalQA') as mock_tech_qa:
            create_qa_tool()
            mock_tech_qa.assert_called_once()
    
    def test_create_qa_tool_openai(self):
        """Test creating OpenAI QA tool"""
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'sk-proj-test-key'}):
            with patch('src.core.requests.get', side_effect=Exception("Connection failed")):
                qa = create_qa_tool(provider="openai")
                assert qa.config.provider == ModelProvider.OPENAI
                assert qa.config.model_name == "gpt-4o-mini"
    
    def test_create_qa_tool_openai_invalid_key(self):
        """Test error with invalid OpenAI key"""
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'invalid-key'}):
            with pytest.raises(ValueError, match="Valid OpenAI API key not found"):
                create_qa_tool(provider="openai")
    
    def test_create_qa_tool_ollama(self):
        """Test creating Ollama QA tool"""
        mock_response = Mock()
        mock_response.status_code = 200
        
        with patch('src.core.requests.get', return_value=mock_response):
            qa = create_qa_tool(provider="ollama")
            assert qa.config.provider == ModelProvider.OLLAMA
            assert qa.config.model_name == "llama3.2"
    
    def test_create_qa_tool_ollama_not_running(self):
        """Test error when Ollama is not running"""
        with patch('src.core.requests.get', side_effect=Exception("Connection failed")):
            with pytest.raises(ValueError, match="Ollama is not running"):
                create_qa_tool(provider="ollama")
    
    def test_create_qa_tool_invalid_provider(self):
        """Test error with invalid provider"""
        with pytest.raises(ValueError, match="Unknown provider"):
            create_qa_tool(provider="invalid")
    
    def test_create_openai_qa(self):
        """Test create_openai_qa convenience function"""
        with patch('src.factory.create_qa_tool') as mock_create:
            create_openai_qa("gpt-4")
            mock_create.assert_called_once_with(provider="openai", model_name="gpt-4")
    
    def test_create_ollama_qa(self):
        """Test create_ollama_qa convenience function"""
        with patch('src.factory.create_qa_tool') as mock_create:
            create_ollama_qa("llama3.1")
            mock_create.assert_called_once_with(provider="ollama", model_name="llama3.1")

class TestIntegration:
    """Integration tests (these would require actual API keys in CI/CD)"""
    
    @pytest.mark.integration
    def test_openai_integration(self):
        """Integration test with OpenAI (requires API key)"""
        if not os.getenv('OPENAI_API_KEY') or not os.getenv('OPENAI_API_KEY').startswith("sk-proj-"):
            pytest.skip("OpenAI API key not available")
        
        qa = create_qa_tool(provider="openai")
        response = qa.ask_question("What is a Python function?")
        assert len(response) > 0
        assert "Python" in response or "function" in response.lower()
    
    @pytest.mark.integration
    def test_ollama_integration(self):
        """Integration test with Ollama (requires Ollama running)"""
        try:
            import requests
            response = requests.get("http://localhost:11434", timeout=2)
            if response.status_code != 200:
                pytest.skip("Ollama not running")
        except:
            pytest.skip("Ollama not available")
        
        qa = create_qa_tool(provider="ollama")
        response = qa.ask_question("What is a Python function?")
        assert len(response) > 0

if __name__ == "__main__":
    pytest.main([__file__])
