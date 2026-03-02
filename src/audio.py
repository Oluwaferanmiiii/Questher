"""
Audio Manager for Questher
Handles speech-to-text and text-to-speech using OpenRouter
"""

import requests
import base64
import json
from typing import Optional, Dict, Any
from src.config import settings

class AudioManager:
    """Manages audio processing using OpenRouter APIs"""
    
    def __init__(self):
        self.openrouter_api_key = settings.openrouter_api_key
        self.base_url = "https://openrouter.ai/api/v1"
        
    def speech_to_text(self, audio_data: bytes, sample_rate: int = 16000, format_hint: str = "wav", model: str = "openai/gpt-4o-audio-preview") -> Optional[str]:
        """
        Convert speech audio to text using OpenRouter with selectable model
        
        Args:
            audio_data: Raw audio bytes
            sample_rate: Audio sample rate
            format_hint: Audio format hint (wav, webm, mp3, m4a)
            model: Audio transcription model to use
            
        Returns:
            Transcribed text or None if failed
        """
        if not self.openrouter_api_key:
            print("[AUDIO] No OpenRouter API key configured")
            return None
        
        if not model:
            print("[AUDIO] No model provided, using default")
            model = "openai/gpt-4o-audio-preview"
        
        # Validate model parameter
        if not model or model.strip() == "":
            print("[AUDIO] Invalid model provided, using default")
            model = "openai/gpt-4o-audio-preview"
        
        print(f"[AUDIO] Using model: '{model}'")
        
        try:
            # Encode audio to base64
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')
            
            # Use OpenRouter's audio-capable models
            headers = {
                'Authorization': f'Bearer {self.openrouter_api_key}',
                'Content-Type': 'application/json',
                'HTTP-Referer': 'https://github.com/Oluwaferanmiiii/Questher',
                'X-Title': 'Questher Technical QA Tool'
            }
            
            data = {
                'model': model,  # Use selected audio model
                'messages': [
                    {
                        'role': 'user',
                        'content': [
                            {
                                'type': 'text',
                                'text': 'Please transcribe the audio content accurately.'
                            },
                            {
                                'type': 'input_audio',
                                'input_audio': {
                                    'data': audio_base64,
                                    'format': format_hint
                                }
                            }
                        ]
                    }
                ],
                'max_tokens': 1000,
                'temperature': 0.1
            }
            
            print(f"[AUDIO] API Request Data: {json.dumps(data, indent=2)}")
            print(f"[AUDIO] Audio data length: {len(audio_base64)} characters")
            
            print(f"[AUDIO] Transcribing with model: {model}")
            print(f"[AUDIO] Audio format: {format_hint}, Size: {len(audio_data)} bytes")
            
            # Use session for better connection handling
            with requests.Session() as session:
                session.headers.update(headers)
                response = session.post(
                    f"{self.base_url}/chat/completions",
                    json=data,
                    timeout=30
                )
            
            if response.status_code == 200:
                result = response.json()
                transcribed_text = result['choices'][0]['message']['content'].strip()
                print(f"[AUDIO] Transcription successful: {len(transcribed_text)} characters")
                return transcribed_text
            else:
                print(f"[AUDIO] STT Error: {response.status_code} - {response.text}")
                print(f"[AUDIO] Request URL: {self.base_url}/chat/completions")
                print(f"[AUDIO] Request headers: {headers}")
                print(f"[AUDIO] Request model: {model}")
                return None
                
        except requests.exceptions.ConnectionError as e:
            print(f"[AUDIO] STT Connection Error: {e}")
            return None
        except requests.exceptions.Timeout as e:
            print(f"[AUDIO] STT Timeout Error: {e}")
            return None
        except Exception as e:
            print(f"[AUDIO] Speech-to-text error: {e}")
            return None
    
    def text_to_speech(self, text: str, voice: str = "alloy", model: str = "openai/tts-1") -> Optional[bytes]:
        """
        Convert text to speech using OpenRouter
        
        Args:
            text: Text to convert to speech
            voice: Voice type (alloy, echo, fable, onyx, nova, shimmer)
            model: TTS model to use
            
        Returns:
            Audio bytes or None if failed
        """
        if not self.openrouter_api_key:
            return None
            
        try:
            headers = {
                'Authorization': f'Bearer {self.openrouter_api_key}',
                'Content-Type': 'application/json',
                'HTTP-Referer': 'https://github.com/Oluwaferanmiiii/Questher',
                'X-Title': 'Questher Technical QA Tool'
            }
            
            # Use OpenRouter's TTS-capable models
            data = {
                'model': model,  # Use selected TTS model
                'input': text,
                'voice': voice,
                'response_format': 'wav'
            }
            
            print(f"[AUDIO] Generating speech with model: {model}, voice: {voice}")
            
            # Use session for better connection handling
            with requests.Session() as session:
                session.headers.update(headers)
                response = session.post(
                    f"{self.base_url}/audio/speech",
                    json=data,
                    timeout=30
                )
            
            if response.status_code == 200:
                print(f"[AUDIO] TTS successful: {len(response.content)} bytes")
                return response.content
            else:
                print(f"[AUDIO] TTS Error: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.ConnectionError as e:
            print(f"[AUDIO] TTS Connection Error: {e}")
            return None
        except requests.exceptions.Timeout as e:
            print(f"[AUDIO] TTS Timeout Error: {e}")
            return None
        except Exception as e:
            print(f"[AUDIO] Text-to-speech error: {e}")
            return None
    
    def get_available_transcription_models(self) -> list:
        """Get list of available transcription models from OpenRouter API"""
        try:
            headers = {
                'Authorization': f'Bearer {self.openrouter_api_key}',
                'Content-Type': 'application/json'
            }
            
            # Fetch models from OpenRouter
            response = requests.get(
                f"{self.base_url}/models",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                models_data = response.json()
                transcription_models = []
                
                # Filter for audio-capable models
                for model in models_data.get('data', []):
                    model_id = model.get('id', '')
                    
                    # Check if model is known to support audio input
                    if any(keyword in model_id.lower() for keyword in [
                        'gpt-4o-audio-preview'  # Only OpenAI model actually supports audio
                    ]):
                        transcription_models.append(model_id)
                        print(f"[AUDIO] Found transcription model: {model_id}")
                
                print(f"[AUDIO] Found {len(transcription_models)} transcription models from OpenRouter")
                return sorted(transcription_models)
            else:
                print(f"[AUDIO] Failed to fetch models: {response.status_code}")
                return self._get_fallback_transcription_models()
                
        except Exception as e:
            print(f"[AUDIO] Error fetching transcription models: {e}")
            return self._get_fallback_transcription_models()
    
    def _get_fallback_transcription_models(self) -> list:
        """Fallback list of known transcription models"""
        return [
            "openai/gpt-4o-audio-preview",      # Only OpenAI model actually supports audio
        ]
    
    def get_available_tts_models(self) -> list:
        """Get list of available TTS models from OpenRouter API"""
        try:
            headers = {
                'Authorization': f'Bearer {self.openrouter_api_key}',
                'Content-Type': 'application/json'
            }
            
            # Fetch models from OpenRouter
            response = requests.get(
                f"{self.base_url}/models",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                models_data = response.json()
                tts_models = []
                
                # Filter for TTS-capable models
                for model in models_data.get('data', []):
                    model_id = model.get('id', '')
                    
                    # Check if model is known to support TTS
                    if any(keyword in model_id.lower() for keyword in [
                        'tts-1', 'tts-1-hd'
                    ]):
                        tts_models.append(model_id)
                        print(f"[AUDIO] Found TTS model: {model_id}")
                
                print(f"[AUDIO] Found {len(tts_models)} TTS models from OpenRouter")
                return sorted(tts_models)
            else:
                print(f"[AUDIO] Failed to fetch TTS models: {response.status_code}")
                return self._get_fallback_tts_models()
                
        except Exception as e:
            print(f"[AUDIO] Error fetching TTS models: {e}")
            return self._get_fallback_tts_models()
    
    def _get_fallback_tts_models(self) -> list:
        """Fallback list of known TTS models"""
        return [
            "openai/tts-1",                     # Standard TTS
            "openai/tts-1-hd",                  # High-quality TTS
        ]
    
    def get_available_voices(self) -> list:
        """Get list of available TTS voices"""
        return [
            "alloy", "echo", "fable", "onyx", 
            "nova", "shimmer"
        ]
    
    def get_all_audio_models_with_info(self) -> Dict[str, list]:
        """Get all available audio models with their capabilities from OpenRouter"""
        try:
            headers = {
                'Authorization': f'Bearer {self.openrouter_api_key}',
                'Content-Type': 'application/json'
            }
            
            # Fetch models from OpenRouter
            response = requests.get(
                f"{self.base_url}/models",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                models_data = response.json()
                transcription_models = []
                tts_models = []
                
                # Categorize models by capabilities
                for model in models_data.get('data', []):
                    model_id = model.get('id', '')
                    capabilities = model.get('capabilities', [])
                    
                    # Check for transcription models (audio input)
                    if any(keyword in model_id.lower() for keyword in [
                        'claude-3.5-sonnet', 'claude-3.5-haiku',
                        'gpt-4o-audio', 'gemini-1.5'
                    ]) and 'audio' in str(capabilities).lower():
                        transcription_models.append({
                            'id': model_id,
                            'name': model.get('name', model_id),
                            'description': model.get('description', ''),
                            'pricing': model.get('pricing', {})
                        })
                    
                    # Check for TTS models (text to speech)
                    elif any(keyword in model_id.lower() for keyword in [
                        'tts-1', 'tts-1-hd', 'speech'
                    ]) and 'text' in str(capabilities).lower():
                        tts_models.append({
                            'id': model_id,
                            'name': model.get('name', model_id),
                            'description': model.get('description', ''),
                            'pricing': model.get('pricing', {})
                        })
                
                print(f"[AUDIO] Found {len(transcription_models)} transcription and {len(tts_models)} TTS models")
                return {
                    'transcription': transcription_models,
                    'tts': tts_models
                }
            else:
                print(f"[AUDIO] Failed to fetch models: {response.status_code}")
                return self._get_fallback_models_with_info()
                
        except Exception as e:
            print(f"[AUDIO] Error fetching audio models: {e}")
            return self._get_fallback_models_with_info()
    
    def _get_fallback_models_with_info(self) -> Dict[str, list]:
        """Fallback list of known audio models with info"""
        return {
            'transcription': [
                {
                    'id': 'anthropic/claude-3.5-sonnet',
                    'name': 'Claude 3.5 Sonnet',
                    'description': 'Best accuracy for transcription'
                },
                {
                    'id': 'anthropic/claude-3.5-haiku',
                    'name': 'Claude 3.5 Haiku',
                    'description': 'Faster transcription'
                },
                {
                    'id': 'openai/gpt-4o-audio-preview',
                    'name': 'GPT-4o Audio Preview',
                    'description': 'OpenAI audio model'
                }
            ],
            'tts': [
                {
                    'id': 'openai/tts-1',
                    'name': 'OpenAI TTS-1',
                    'description': 'Standard text-to-speech'
                },
                {
                    'id': 'openai/tts-1-hd',
                    'name': 'OpenAI TTS-1 HD',
                    'description': 'High-quality text-to-speech'
                }
            ]
        }
    
    def get_available_models(self) -> list:
        """Get list of available audio models on OpenRouter (legacy method)"""
        return self.get_available_transcription_models() + self.get_available_tts_models()
    
    def is_configured(self) -> bool:
        """Check if OpenRouter is configured for audio"""
        return bool(self.openrouter_api_key and self.openrouter_api_key.startswith("sk-or-"))
    
    def get_configuration_status(self) -> Dict[str, Any]:
        """Get configuration status"""
        return {
            "configured": self.is_configured(),
            "api_key_set": bool(self.openrouter_api_key),
            "voices": self.get_available_voices(),
            "models": self.get_available_models(),
            "features": ["speech_to_text", "text_to_speech"],
            "provider": "OpenRouter"
        }

# Global instance
audio_manager = AudioManager()
