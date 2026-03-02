"""
Week 2 Gradio UI for Questher
Interactive web interface with streaming and multi-provider support
"""

import gradio as gr
import json
import time
from datetime import datetime
from typing import Generator, Tuple, Dict, Any, List
import asyncio
import sys

# Fix Windows asyncio issue
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from src.config import settings
from src.models import ModelManager
from src.core import ModelProvider
from src.factory import create_qa_tool
from src.audio import audio_manager

class QuestherUI:
    """Gradio-based web interface for Questher"""
    
    def __init__(self):
        self.qa_tools = {}
        self.conversation_history = []
        self.model_manager = ModelManager()  # Add model manager instance
        self.initialize_providers()
    
    def initialize_providers(self):
        """Initialize all available AI providers"""
        providers = ["openrouter", "openai", "anthropic", "google", "ollama"]  # OpenRouter first since it has real key
        available_count = 0
        
        for provider in providers:
            try:
                self.qa_tools[provider] = create_qa_tool(provider=provider)
                print(f"[OK] Initialized {provider} provider")
                available_count += 1
            except Exception as e:
                print(f"[ERROR] Failed to initialize {provider}: {e}")
                self.qa_tools[provider] = None
        
        if available_count == 0:
            print("[WARNING] No AI providers available. Please configure API keys in .env file")
            print("[INFO] Copy .env.example to .env and add your API keys")
            raise ValueError("At least one AI provider must be configured to use Questher")
        else:
            print(f"[INFO] Successfully initialized {available_count} provider(s)")
        
        # Print available providers
        available_providers = [p for p, tool in self.qa_tools.items() if tool is not None]
        print(f"[PROVIDERS] Available providers: {', '.join(available_providers)}")
    
    def get_available_providers(self) -> List[str]:
        """Get list of available providers"""
        return [p for p, tool in self.qa_tools.items() if tool is not None]
    
    def get_models_for_provider(self, provider: str) -> List[str]:
        """Get available models for a provider"""
        try:
            return self.model_manager.get_display_models(provider, limit=5)
        except Exception as e:
            print(f"[ERROR] Failed to get models for {provider}: {e}")
            return [f"{provider}-default"]
    
    def get_all_models_for_provider(self, provider: str) -> List[str]:
        """Get all models for scrollable dropdown"""
        try:
            return self.model_manager.get_all_models_for_scroll(provider)
        except Exception as e:
            print(f"[ERROR] Failed to get all models for {provider}: {e}")
            return [f"{provider}-default"]
    
    def get_system_prompts(self) -> Dict[str, str]:
        """Get available system prompts for expertise"""
        return {
            "General Technical": "You are a helpful technical assistant that provides clear, accurate answers to technical questions.",
            "Software Development": "You are an expert software engineer with deep knowledge of programming languages, frameworks, and best practices.",
            "DevOps & Cloud": "You are a DevOps specialist with expertise in cloud platforms, containerization, and infrastructure automation.",
            "Data Science": "You are a data science expert with knowledge of machine learning, statistics, and data analysis.",
            "Cybersecurity": "You are a cybersecurity professional specializing in security best practices and threat analysis.",
            "Database": "You are a database architect with expertise in SQL, NoSQL, and database optimization."
        }
    
    def process_question_stream(self, question: str, provider: str, model: str, 
                               expertise: str) -> Generator[Tuple[str, str], None, None]:
        """Process question with streaming response"""
        start_time = time.time()
        
        try:
            qa_tool = self.qa_tools[provider]
            if not qa_tool:
                yield f"[ERROR] Provider {provider} not available", "{}"
                return
            
            # Update system prompt based on expertise
            system_prompts = self.get_system_prompts()
            qa_tool.system_prompt = system_prompts.get(expertise, system_prompts["General Technical"])
            
            # Get streaming response
            full_response = ""
            for chunk in qa_tool.ask_question_stream(question):
                full_response += chunk
                yield full_response, "{}"
            
            # Convert response to speech if audio is configured
            if audio_manager.is_configured():
                audio_bytes = audio_manager.text_to_speech(full_response)
                if audio_bytes:
                    yield full_response, json.dumps({
                        "audio_ready": True,
                        "provider": provider,
                        "model": model,
                        "expertise": expertise,
                        "response_time": round(time.time() - start_time, 2),
                        "word_count": len(full_response.split()),
                        "char_count": len(full_response),
                        "timestamp": datetime.now().isoformat()
                    }, indent=2)
                    return
            
            # Calculate metrics
            response_time = time.time() - start_time
            metrics = {
                "provider": provider,
                "model": model,
                "expertise": expertise,
                "response_time": round(response_time, 2),
                "word_count": len(full_response.split()),
                "char_count": len(full_response),
                "timestamp": datetime.now().isoformat()
            }
            
            yield full_response, json.dumps(metrics, indent=2)
            
            # Store in conversation history
            self.conversation_history.append({
                "question": question,
                "answer": full_response,
                "provider": provider,
                "model": model,
                "expertise": expertise,
                "metrics": metrics
            })
            
        except Exception as e:
            error_msg = f"[ERROR] {str(e)}"
            error_metrics = {"error": str(e), "timestamp": datetime.now().isoformat()}
            yield error_msg, json.dumps(error_metrics, indent=2)
    
    def load_audio_models(self):
        """Load audio models from OpenRouter API"""
        try:
            print("[UI] Loading audio models from OpenRouter...")
            
            # Get transcription models
            transcription_models = audio_manager.get_available_transcription_models()
            print(f"[UI] Found transcription models: {transcription_models}")
            transcription_choices = [(model, model) for model in transcription_models]
            
            # Get TTS models
            tts_models = audio_manager.get_available_tts_models()
            print(f"[UI] Found TTS models: {tts_models}")
            tts_choices = [(model, model) for model in tts_models]
            
            result = {
                "transcription_choices": transcription_choices,
                "tts_choices": tts_choices,
                "transcription_default": transcription_models[0] if transcription_models else "openai/gpt-4o-audio-preview",
                "tts_default": tts_models[0] if tts_models else "openai/tts-1"
            }
            
            print(f"[UI] Audio models data: {result}")
            print(f"[UI] Loaded {len(transcription_models)} transcription and {len(tts_models)} TTS models")
            return result
        except Exception as e:
            print(f"[UI] Error loading audio models: {e}")
            # Return fallback choices
            fallback_transcription = ["openai/gpt-4o-audio-preview"]
            fallback_tts = ["openai/tts-1"]
            return {
                "transcription_choices": [(m, m) for m in fallback_transcription],
                "tts_choices": [(m, m) for m in fallback_tts],
                "transcription_default": fallback_transcription[0],
                "tts_default": fallback_tts[0]
            }
    
    def update_audio_models(self):
        """Update audio model dropdowns"""
        return self.load_audio_models()
    
    def update_models(self, provider: str):
        """Update model choices when provider changes"""
        all_models = self.get_all_models_for_provider(provider)
        display_models = self.get_models_for_provider(provider)
        
        # Return updated choices and info
        return {
            "choices": all_models,
            "value": display_models[0] if display_models else None,
            "info": f"Showing {len(display_models)} of {len(all_models)} available models"
        }
    
    def clear_history(self) -> str:
        """Clear conversation history"""
        self.conversation_history = []
        return "[CLEARED] Conversation history cleared"
    
    def get_conversation_summary(self) -> str:
        """Get summary of conversation history"""
        if not self.conversation_history:
            return "No conversation history yet."
        
        summary = f"**Conversation Summary**\n\n"
        summary += f"**Total Exchanges:** {len(self.conversation_history)}\n\n"
        
        # Provider usage
        provider_counts = {}
        for conv in self.conversation_history:
            provider_counts[conv["provider"]] = provider_counts.get(conv["provider"], 0) + 1
        
        summary += "**Provider Usage:**\n"
        for provider, count in provider_counts.items():
            summary += f"- {provider}: {count} times\n"
        
        # Average response time
        avg_time = sum(conv["metrics"]["response_time"] for conv in self.conversation_history) / len(self.conversation_history)
        summary += f"\n**Average Response Time:** {avg_time:.2f}s\n"
        
        return summary
    
    def create_interface(self) -> gr.Blocks:
        """Create the Gradio interface"""
        
        available_providers = self.get_available_providers()
        
        # Load audio models from OpenRouter
        audio_models_data = self.load_audio_models()
        
        with gr.Blocks(title=settings.ui_title) as interface:
            gr.Markdown(f"# Questher Pro - Technical Q&A")
            gr.Markdown("Ask technical questions with AI-powered assistance from multiple providers. Supports voice input/output!")
            
            with gr.Row():
                with gr.Column(scale=2):
                    # Audio input section
                    with gr.Row():
                        audio_input = gr.Audio(
                            label="Voice Input (Optional)",
                            type="filepath",
                            sources=["microphone"]  # Only microphone for recording
                        )
                        
                        # Add transcription status indicator
                        transcription_status = gr.Textbox(
                            label="Transcription Status",
                            placeholder="Click 'Record' to start transcribing...",
                            interactive=False,
                            visible=True
                        )
                        
                        # Add clear audio button
                        clear_audio_btn = gr.Button("Clear Audio", size="sm")
                    
                    question_input = gr.Textbox(
                        label="Ask a Technical Question",
                        placeholder="e.g., How do I implement a REST API in Python? (Type here or upload audio below)",
                        lines=4,  # Increased lines for better editing
                        interactive=True
                    )
                    
                    with gr.Row():
                        provider_select = gr.Dropdown(
                            choices=available_providers,
                            value=available_providers[0] if available_providers else None,
                            label="AI Provider"
                        )
                        
                        # Get initial models
                        initial_provider = available_providers[0] if available_providers else None
                        if not initial_provider:
                            raise ValueError("No AI providers available. Please configure API keys.")
                        
                        initial_models = self.get_all_models_for_provider(initial_provider)
                        initial_display = self.get_models_for_provider(initial_provider)
                        
                        model_select = gr.Dropdown(
                            choices=initial_models,
                            value=initial_display[0] if initial_display else None,
                            label="Model",
                            info=f"Showing {len(initial_display)} of {len(initial_models)} available models"
                        )
                    
                    # Add audio model selection with enhanced info
                    with gr.Row():
                        with gr.Column(scale=2):
                            transcription_model_select = gr.Dropdown(
                                choices=audio_models_data["transcription_choices"],
                                value=audio_models_data["transcription_default"],
                                label="Audio Transcription Model",
                                info="Model used for speech-to-text transcription (fetched from OpenRouter)"
                            )
                        
                        with gr.Column(scale=1):
                            gr.Markdown("**Transcription Models**\nFetched from OpenRouter API")
                    
                    with gr.Row():
                        with gr.Column(scale=2):
                            tts_model_select = gr.Dropdown(
                                choices=audio_models_data["tts_choices"],
                                value=audio_models_data["tts_default"],
                                label="TTS Model",
                                info="Text-to-speech model (fetched from OpenRouter)"
                            )
                        
                        with gr.Column(scale=1):
                            tts_voice_select = gr.Dropdown(
                                choices=audio_manager.get_available_voices(),
                                value="alloy",
                                label="TTS Voice",
                                info="Voice for text-to-speech output"
                            )
                    
                    expertise_select = gr.Dropdown(
                        choices=list(self.get_system_prompts().keys()),
                        value="General Technical",
                        label="Expertise Area"
                    )
                    
                    with gr.Row():
                        submit_btn = gr.Button("Get Answer", variant="primary")
                        clear_btn = gr.Button("Clear")
                        # Voice output button
                        voice_btn = gr.Button("🔊 Speak Answer", variant="secondary")
                
                with gr.Column(scale=1):
                    gr.Markdown("### Performance Metrics")
                    metrics_display = gr.JSON(label="Metrics")
                    
                    gr.Markdown("### Tips")
                    gr.Markdown("""
                    - **OpenAI**: Best for general technical questions
                    - **Claude**: Excellent for detailed explanations  
                    - **Gemini**: Great for code examples
                    - **OpenRouter**: Access to 100+ models + Audio processing
                    - **Ollama**: Free local option
                    - **Voice Input**: Click record → Speak → Stop → Auto-transcribe (Claude Sonnet) → Edit → Submit
                    - **Voice Output**: Click speaker to hear the answer (OpenAI TTS)
                    - **Audio Models**: Claude 3.5 Sonnet for transcription, OpenAI TTS for speech
                    """)
            
            answer_output = gr.Markdown(label="Answer")
            
            # Audio output
            audio_output = gr.Audio(label="Voice Output", visible=False)
            
            # Conversation controls
            with gr.Row():
                summary_btn = gr.Button("Show Summary")
                history_btn = gr.Button("Show History")
                clear_history_btn = gr.Button("Clear History")
            
            conversation_display = gr.Markdown(label="Conversation")
            
            # Event handlers
            def update_models_wrapper(provider):
                """Wrapper to handle model updates"""
                try:
                    all_models = self.get_all_models_for_provider(provider)
                    display_models = self.get_models_for_provider(provider)
                    
                    return gr.Dropdown(
                        choices=all_models,
                        value=display_models[0] if display_models else None,
                        info=f"Showing {len(display_models)} of {len(all_models)} available models"
                    )
                except Exception as e:
                    print(f"Error updating models: {e}")
                    return gr.Dropdown(choices=[], value=None, info="Error loading models")
            
            def transcribe_audio(audio_file, transcription_model):
                """Transcribe audio and put text in question box for editing"""
                print(f"[DEBUG] transcribe_audio called with: {audio_file}, model: {transcription_model}")
                
                if audio_file is None:
                    print("[DEBUG] No audio file provided")
                    return None, "No audio recorded"
                
                try:
                    print(f"[DEBUG] Starting transcription for: {audio_file}")
                    # Update status immediately
                    transcription_status = "Transcribing audio..."
                    
                    # Read audio file
                    with open(audio_file, 'rb') as f:
                        audio_data = f.read()
                    
                    print(f"[DEBUG] Audio data size: {len(audio_data)} bytes")
                    
                    # Detect audio format from file extension
                    format_hint = "wav"
                    if audio_file.lower().endswith('.webm'):
                        format_hint = "webm"
                    elif audio_file.lower().endswith('.mp3'):
                        format_hint = "mp3"
                    elif audio_file.lower().endswith('.m4a'):
                        format_hint = "m4a"
                    
                    print(f"[DEBUG] Audio format detected: {format_hint}")
                    
                    # Transcribe using selected model
                    print(f"[DEBUG] Calling audio_manager.speech_to_text with model: {transcription_model}")
                    transcribed_text = audio_manager.speech_to_text(
                        audio_data, 
                        format_hint=format_hint,
                        model=transcription_model
                    )
                    
                    if transcribed_text:
                        print(f"[DEBUG] Transcription successful: {transcribed_text[:100]}...")
                        transcription_status = f"Transcription complete! ({len(transcribed_text)} characters)"
                        return transcribed_text, transcription_status
                    else:
                        print("[DEBUG] Transcription failed - no text returned")
                        transcription_status = "Transcription failed - please try again"
                        return None, transcription_status
                        
                except Exception as e:
                    print(f"[DEBUG] Transcription error: {e}")
                    transcription_status = f"Transcription error: {str(e)}"
                    return None, transcription_status
            
            def speak_answer(answer_text, tts_voice, tts_model):
                """Convert answer text to speech"""
                if not answer_text or not audio_manager.is_configured():
                    return None, gr.Audio.update(visible=False)
                
                try:
                    audio_bytes = audio_manager.text_to_speech(answer_text, voice=tts_voice, model=tts_model)
                    if audio_bytes:
                        return audio_bytes, gr.Audio.update(visible=True, value=(16000, audio_bytes))
                    return None, gr.Audio.update(visible=False)
                except Exception as e:
                    print(f"Error generating speech: {e}")
                    return None, gr.Audio.update(visible=False)
            
            # Audio transcription handler
            audio_input.change(
                fn=transcribe_audio,
                inputs=[audio_input, transcription_model_select],
                outputs=[question_input, transcription_status]
            )
            
            # Clear audio button handler
            clear_audio_btn.click(
                fn=lambda: (None, "", "Click 'Record' to start transcribing..."),
                outputs=[audio_input, question_input, transcription_status]
            )
            
            provider_select.change(
                fn=update_models_wrapper,
                inputs=[provider_select],
                outputs=[model_select]
            )
            
            submit_btn.click(
                fn=self.process_question_stream,
                inputs=[question_input, provider_select, model_select, expertise_select],
                outputs=[answer_output, metrics_display]
            )
            
            # Voice button handler
            voice_btn.click(
                fn=speak_answer,
                inputs=[answer_output, tts_voice_select, tts_model_select],
                outputs=[audio_output, audio_output]
            )
            
            clear_btn.click(
                fn=lambda: ("", "", "Click 'Record' to start transcribing..."),
                outputs=[question_input, answer_output, transcription_status]
            )
            
            summary_btn.click(
                fn=self.get_conversation_summary,
                outputs=[conversation_display]
            )
            
            history_btn.click(
                fn=lambda: json.dumps(self.conversation_history[-5:], indent=2) if self.conversation_history else "No history yet.",
                outputs=[conversation_display]
            )
            
            clear_history_btn.click(
                fn=self.clear_history,
                outputs=[conversation_display]
            )
        
        return interface

def launch_ui(host: str = "127.0.0.1", port: int = 7860, share: bool = False):
    """Launch the Questher Gradio interface"""
    ui = QuestherUI()
    interface = ui.create_interface()
    
    print(f"[LAUNCH] Launching Questher UI on http://{host}:{port}")
    print(f"[PROVIDERS] Available providers: {', '.join(ui.get_available_providers())}")
    
    interface.launch(
        server_name=host,
        server_port=port,
        share=share
    )

if __name__ == "__main__":
    launch_ui(share=True)  # Set share=True for public URL
