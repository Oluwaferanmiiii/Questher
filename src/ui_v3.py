#!/usr/bin/env python3
"""
Questher v3 UI - Enhanced with Code Generation Features
Gradio interface with multi-provider support and Python→C++ conversion
"""

import gradio as gr
import json
import time
from datetime import datetime, timedelta
from typing import Generator, Tuple, Dict, Any, List
import asyncio
import sys
import matplotlib.pyplot as plt
import pandas as pd
from collections import defaultdict, Counter

# Fix Windows asyncio issue
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from src.config import settings
from src.models import ModelManager
from src.core import ModelProvider
from src.factory import create_qa_tool, create_code_generator
from src.audio import audio_manager
from src.code_generator import CodeGenerator
from src.compiler import CppCompiler


class QuestherUI:
    """Enhanced Gradio UI for Questher v3 with code generation"""
    
    def __init__(self):
        self.qa_tools = {}
        self.conversation_history = []
        self.model_manager = ModelManager()
        self.code_generator = None
        self.compiler = CppCompiler()
        self.initialize_providers()
        
    def initialize_providers(self):
        """Initialize all available AI providers"""
        providers = ["openrouter", "openai", "anthropic", "google", "ollama"]
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
            print("[WARNING] No AI providers available. Some features will be disabled.")
            print("[INFO] Configure API keys in .env file to enable AI features")
        else:
            print(f"[INFO] Successfully initialized {available_count} provider(s)")
            
        # Print available providers
        available_providers = [p for p, tool in self.qa_tools.items() if tool is not None]
        print(f"[PROVIDERS] Available providers: {', '.join(available_providers)}")
    
    def get_code_generation_models(self) -> List[str]:
        """Get models available for code generation"""
        return [
            "gpt-5",
            "gpt-5-nano", 
            "claude-sonnet-4-5-20250929",
            "claude-haiku-4-5",
            "gemini-2.5-pro",
            "gemini-2.5-flash-lite",
            "grok-4",
            "grok-4-fast-non-reasoning"
        ]
    
    def create_code_generation_interface(self):
        """Create code generation tab"""
        with gr.Tab("🚀 Code Generation", elem_classes=["code-gen-tab"]):
            gr.Markdown("### Python → C++ Converter")
            gr.Markdown("Generate high-performance C++ code from Python using frontier AI models")
            
            with gr.Row():
                with gr.Column(scale=1):
                    python_input = gr.Code(
                        label="Python Code",
                        language="python",
                        lines=10,
                        value="# Enter your Python code here...\nprint('Hello, World!')"
                    )
                    
                    cpp_output = gr.Code(
                        label="Generated C++",
                        language="cpp",
                        lines=20,
                        interactive=True,
                        elem_classes=["cpp-out"]
                    )
                    
                    with gr.Accordion("📊 Compilation Results", open=False):
                        compile_status = gr.Textbox(
                            label="Compilation Status",
                            placeholder="Waiting for compilation...",
                            interactive=False,
                            elem_classes=["compile-status"]
                        )
                        
                        run_output = gr.Textbox(
                            label="Execution Output",
                            placeholder="Program output will appear here...",
                            interactive=False,
                            elem_classes=["run-output"]
                        )
                
                with gr.Column(scale=1):
                    # Provider selection (using Q&A template)
                    available_providers = self.get_available_providers()
                    provider_select = gr.Dropdown(
                        choices=available_providers,
                        value=available_providers[0] if available_providers else None,
                        label="AI Provider"
                    )
                    
                    # Get initial models
                    initial_provider = available_providers[0] if available_providers else "openrouter"
                    if not available_providers:
                        print("[WARNING] No AI providers available. Please configure API keys.")
                        initial_models = ["openrouter-default"]
                        initial_display = ["openrouter-default"]
                    else:
                        initial_models = self.get_models_for_provider(initial_provider)
                        initial_display = self.get_models_for_provider(initial_provider)
                    
                    model_select = gr.Dropdown(
                        choices=initial_models,
                        value=initial_display[0] if initial_display else None,
                        label="Model",
                        info=f"Showing {len(initial_display)} of {len(initial_models)} available models"
                    )
                    
                    with gr.Row():
                        generate_btn = gr.Button("🔄 Generate C++", variant="primary", elem_classes=["generate-btn"])
                        compile_btn = gr.Button("⚡ Compile & Run", variant="secondary", elem_classes=["compile-btn"])
            
            # Wire up the generation events
            provider_select.change(
                fn=self.update_model_choices,
                inputs=[provider_select],
                outputs=[model_select]
            )
            
            generate_btn.click(
                fn=self.generate_cpp_code,
                inputs=[python_input, model_select],
                outputs=[cpp_output]
            )
            
            compile_btn.click(
                fn=self.compile_and_run_cpp,
                inputs=[cpp_output],
                outputs=[compile_status, run_output]
            )
    
    def generate_cpp_code(self, python_code: str, model_name: str) -> str:
        """Generate C++ code from Python"""
        try:
            # Initialize code generator with selected model
            provider = self.model_manager.get_provider_for_model(model_name)
            if not provider:
                return f"Error: No provider available for model: {model_name}"
            
            self.code_generator = create_code_generator(provider, model_name)
            
            # Track generation time
            start_time = time.time()
            result = self.code_generator.generate_cpp_from_python(python_code)
            generation_time = time.time() - start_time
            
            # Add to analytics
            self.conversation_history.append({
                'timestamp': datetime.now().isoformat(),
                'type': 'code_generation',
                'provider': provider,
                'model': model_name,
                'python_code': python_code,
                'cpp_code': result["cpp_code"],
                'metrics': {
                    'generation_time': generation_time,
                    'code_length': len(result["cpp_code"]),
                    'response_time': generation_time,
                    'word_count': len(result["cpp_code"].split()),
                    'answer_length': len(result["cpp_code"]),
                    'words_per_second': len(result["cpp_code"].split()) / generation_time if generation_time > 0 else 0,
                    'characters_per_second': len(result["cpp_code"]) / generation_time if generation_time > 0 else 0
                }
            })
            
            return result["cpp_code"]
            
        except Exception as e:
            # Log failed generation
            self.conversation_history.append({
                'timestamp': datetime.now().isoformat(),
                'type': 'code_generation',
                'provider': provider if 'provider' in locals() else 'unknown',
                'model': model_name,
                'python_code': python_code,
                'cpp_code': '',
                'compilation_success': False,
                'error': str(e),
                'metrics': {
                    'generation_time': 0,
                    'code_length': 0,
                    'response_time': 0,
                    'word_count': 0,
                    'answer_length': 0,
                    'words_per_second': 0,
                    'characters_per_second': 0
                }
            })
            return f"Error generating C++ code: {str(e)}"
    
    def compile_and_run_cpp(self, cpp_code: str) -> Tuple[str, str]:
        """Compile and execute C++ code"""
        try:
            result = self.compiler.compile_and_run(cpp_code)
            
            # Update the last code generation entry with compilation results
            if self.conversation_history and self.conversation_history[-1].get('type') == 'code_generation':
                self.conversation_history[-1].update({
                    'compilation_success': result["success"],
                    'compilation_method': result.get("method", "unknown"),
                    'compile_output': result.get("compile_output", ""),
                    'run_output': result.get("run_output", ""),
                    'execution_time': result.get("execution_time", ""),
                    'compilation_error': result.get("error", "") if not result["success"] else ""
                })
            
            if result["success"]:
                return (
                    f"✅ Compilation successful ({result.get('method', 'unknown')} compilation)", 
                    result["run_output"]
                )
            else:
                return (
                    f"❌ Compilation failed: {result['error']}", 
                    result.get("error", "Compilation error occurred")
                )
                
        except Exception as e:
            # Update the last code generation entry with compilation error
            if self.conversation_history and self.conversation_history[-1].get('type') == 'code_generation':
                self.conversation_history[-1].update({
                    'compilation_success': False,
                    'compilation_method': 'error',
                    'compilation_error': str(e)
                })
            
            return (
                f"❌ Compilation error: {str(e)}", 
                str(e)
            )
    
    def _get_provider_for_model(self, model_name: str) -> str:
        """Determine provider for a given model"""
        if "gpt" in model_name:
            return "openai" if "openrouter" in self.qa_tools else "openrouter"
        elif "claude" in model_name:
            return "anthropic"
        elif "gemini" in model_name:
            return "google"
        elif "grok" in model_name:
            return "grok"
        else:
            return "openrouter"
    
    def create_qa_interface(self):
        """Create Q&A interface (existing functionality)"""
        with gr.Tab("💬 Q&A", elem_classes=["qa-tab"]):
            gr.Markdown("### Ask Technical Questions")
            gr.Markdown("Get answers from multiple AI providers with voice input/output support!")
            
            # Load audio models from OpenRouter
            audio_models_data = self.load_audio_models()
            
            with gr.Row():
                with gr.Column(scale=2):
                    # Audio input section
                    with gr.Row():
                        audio_input = gr.Audio(
                            label="Voice Input (Optional)",
                            type="filepath",
                            sources=["microphone", "upload"]
                        )
                        
                        # Add transcription status indicator
                        transcription_status = gr.Textbox(
                            label="Transcription Status",
                            placeholder="Click 'Record' to start transcribing...",
                            interactive=False
                        )
                        
                        # Add clear audio button
                        clear_audio_btn = gr.Button("Clear Audio", size="sm")
                    
                    question_input = gr.Textbox(
                        label="Ask a Technical Question",
                        placeholder="e.g., How do I implement a REST API in Python? (Type here or upload audio below)",
                        lines=4
                    )
                    
                with gr.Column(scale=1):
                    # Provider selection
                    available_providers = self.get_available_providers()
                    provider_select = gr.Dropdown(
                        choices=available_providers,
                        value=available_providers[0] if available_providers else None,
                        label="AI Provider"
                    )
                    
                    # Get initial models
                    initial_provider = available_providers[0] if available_providers else "openrouter"
                    if not available_providers:
                        print("[WARNING] No AI providers available. Please configure API keys.")
                        initial_models = ["openrouter-default"]
                        initial_display = ["openrouter-default"]
                    else:
                        initial_models = self.get_models_for_provider(initial_provider)
                        initial_display = self.get_models_for_provider(initial_provider)
                    
                    model_select = gr.Dropdown(
                        choices=initial_models,
                        value=initial_display[0] if initial_display else None,
                        label="Model",
                        info=f"Showing {len(initial_display)} of {len(initial_models)} available models"
                    )
                    
                    expertise_select = gr.Dropdown(
                        choices=list(self.get_system_prompts().keys()),
                        value="General Technical",
                        label="Expertise Area"
                    )
                    
                    # Action buttons
                    with gr.Row():
                        submit_btn = gr.Button("🚀 Get Answer", variant="primary", elem_classes=["submit-btn"])
                        clear_btn = gr.Button("🗑️ Clear", size="sm")
            
            # Event handlers
            provider_select.change(
                fn=self.update_model_choices,
                inputs=[provider_select],
                outputs=[model_select]
            )
            
            # Audio processing
            audio_input.change(
                fn=self.transcribe_audio,
                inputs=[audio_input, provider_select, model_select],
                outputs=[question_input, transcription_status]
            )
            
            clear_audio_btn.click(
                fn=self.clear_audio,
                outputs=[question_input, transcription_status]
            )
            
            # Question answering
            submit_btn.click(
                fn=self.process_question_stream,
                inputs=[question_input, provider_select, model_select, expertise_select],
                outputs=[question_input]
            )
            
            clear_btn.click(
                fn=self.clear_history,
                outputs=[question_input]
            )
    
    def create_interface(self) -> gr.Blocks:
        """Create the main Gradio interface"""
        with gr.Blocks(
            title=settings.ui_title
        ) as interface:
            gr.Markdown("# Questher Pro - Technical Q&A with Code Generation")
            gr.Markdown("Multi-provider AI assistance with Python→C++ conversion capabilities!")
            
            with gr.Tabs():
                self.create_qa_interface()
                self.create_code_generation_interface()
                
                with gr.Tab("📊 Analytics", elem_classes=["analytics-tab"]):
                    gr.Markdown("### Comprehensive Analytics Dashboard")
                    
                    with gr.Tabs():
                        # Overview Tab
                        with gr.Tab("📈 Overview"):
                            overview_display = gr.Markdown(self.get_overview_analytics())
                            
                        # Q&A Analytics Tab
                        with gr.Tab("💬 Q&A Analytics"):
                            qa_display = gr.Markdown(self.get_qa_analytics())
                            qa_chart = gr.Plot(label="Q&A Performance Charts")
                            
                            with gr.Row():
                                update_qa_btn = gr.Button("🔄 Update Q&A Analytics", size="sm")
                                update_qa_btn.click(
                                    fn=self.update_qa_analytics,
                                    outputs=[qa_display, qa_chart]
                                )
                        
                        # Code Generation Analytics Tab
                        with gr.Tab("🚀 Code Generation Analytics"):
                            code_display = gr.Markdown(self.get_code_generation_analytics())
                            code_chart = gr.Plot(label="Code Generation Charts")
                            
                            with gr.Row():
                                update_code_btn = gr.Button("🔄 Update Code Analytics", size="sm")
                                update_code_btn.click(
                                    fn=self.update_code_analytics,
                                    outputs=[code_display, code_chart]
                                )
                        
                        # Performance Metrics Tab
                        with gr.Tab("⚡ Performance Metrics"):
                            perf_display = gr.Markdown(self.get_performance_analytics())
                            perf_chart = gr.Plot(label="Performance Comparison")
                            
                            with gr.Row():
                                update_perf_btn = gr.Button("🔄 Update Performance", size="sm")
                                update_perf_btn.click(
                                    fn=self.update_performance_analytics,
                                    outputs=[perf_display, perf_chart]
                                )
                        
                        # Usage Trends Tab
                        with gr.Tab("📊 Usage Trends"):
                            trends_display = gr.Markdown(self.get_usage_trends())
                            trends_chart = gr.Plot(label="Usage Trends Over Time")
                            
                            with gr.Row():
                                update_trends_btn = gr.Button("🔄 Update Trends", size="sm")
                                update_trends_btn.click(
                                    fn=self.update_usage_trends,
                                    outputs=[trends_display, trends_chart]
                                )
                        
                        # Raw Data Tab
                        with gr.Tab("📋 Raw Data"):
                            raw_data_display = gr.Dataframe(
                                value=self.get_raw_analytics_data(),
                                label="Complete Conversation History",
                                interactive=False
                            )
                            
                            export_btn = gr.Button("📥 Export to JSON", size="sm")
                            export_btn.click(
                                fn=self.export_analytics,
                                outputs=[gr.File()]
                            )
                    
                    # Clear all analytics
                    with gr.Row():
                        clear_all_btn = gr.Button("🗑️ Clear All History", variant="stop", size="sm")
                        clear_all_btn.click(
                            fn=self.clear_all_history,
                            outputs=[overview_display, qa_display, code_display, perf_display, trends_display, raw_data_display]
                        )
        
        return interface
    
    def load_audio_models(self) -> Dict[str, Any]:
        """Load audio models from OpenRouter"""
        try:
            return audio_manager.get_available_models()
        except AttributeError:
            # Fallback if method doesn't exist
            return {"models": ["whisper-1"], "default": "whisper-1"}
    
    def transcribe_audio(self, audio_file, provider: str, model: str) -> Tuple[str, str]:
        try:
            qa_tool = self.qa_tools[provider]
            if not qa_tool:
                return "Provider not available", ""
            
            # Transcribe audio
            transcription = qa_tool.transcribe_audio(audio_file, model)
            return transcription, "✅ Transcription complete"
            
        except Exception as e:
            return f"❌ Transcription failed: {str(e)}", ""
    
    def process_question_stream(self, question: str, provider: str, model: str, 
                             expertise: str) -> Generator[str, None, None]:
        """Process question with streaming response"""
        try:
            qa_tool = self.qa_tools[provider]
            if not qa_tool:
                yield f"[ERROR] Provider {provider} not available"
                return
            
            # Update system prompt based on expertise
            system_prompts = self.get_system_prompts()
            system_prompt = system_prompts.get(expertise, system_prompts["General Technical"])
            
            start_time = time.time()
            
            # Stream response
            response_parts = []
            for part in qa_tool.stream_response(question, model, system_prompt):
                response_parts.append(part)
                yield part
            
            # Calculate metrics
            full_response = "".join(response_parts)
            response_time = time.time() - start_time
            
            metrics = {
                'response_time': response_time,
                'word_count': len(full_response.split()),
                'answer_length': len(full_response),
                'words_per_second': len(full_response.split()) / response_time if response_time > 0 else 0,
                'characters_per_second': len(full_response) / response_time if response_time > 0 else 0
            }
            
            # Add to conversation history
            self.conversation_history.append({
                'timestamp': datetime.now().isoformat(),
                'provider': provider,
                'model': model,
                'expertise': expertise,
                'question': question,
                'answer': full_response,
                'metrics': metrics
            })
            
            yield full_response
        
        except Exception as e:
            yield f"[ERROR] Processing failed: {str(e)}"
    
    def update_model_choices(self, provider: str) -> Dict[str, Any]:
        """Update model choices based on selected provider"""
        try:
            models = self.get_all_models_for_provider(provider)
            display_models = self.get_models_for_provider(provider)
            
            return {
                "choices": models,
                "value": display_models[0] if display_models else None,
                "info": f"Showing {len(display_models)} of {len(models)} available models"
            }
            
        except Exception as e:
            return {
                "choices": [f"{provider}-default"],
                "value": f"{provider}-default",
                "info": f"Error loading models: {str(e)}"
            }
    
    def clear_audio(self) -> str:
        """Clear audio input and transcription status"""
        return "", "Audio cleared"
    
    def clear_history(self) -> str:
        """Clear conversation history"""
        self.conversation_history = []
        return "[CLEARED] Conversation history cleared"
    
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
        """Get all models for a provider (for scrollable dropdown)"""
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
    
    # Enhanced Analytics Methods
    def get_overview_analytics(self) -> str:
        """Get comprehensive overview analytics"""
        if not self.conversation_history:
            return "📊 **No analytics data available yet. Start using the Q&A and Code Generation features!**"
        
        total_qa = len([c for c in self.conversation_history if 'question' in c])
        total_code = len([c for c in self.conversation_history if 'type' in c and c['type'] == 'code_generation'])
        
        provider_stats = Counter(c['provider'] for c in self.conversation_history)
        avg_response_time = sum(c['metrics']['response_time'] for c in self.conversation_history) / len(self.conversation_history)
        
        overview = f"""
## 📈 **Questher Analytics Overview**

### 🎯 **Usage Summary**
- **Total Q&A Sessions**: {total_qa}
- **Total Code Generation**: {total_code}
- **Total Interactions**: {len(self.conversation_history)}

### 🤖 **Provider Performance**
{chr(10).join([f"- **{provider}**: {count} uses ({count/len(self.conversation_history)*100:.1f}%)" for provider, count in provider_stats.most_common()])}

### ⚡ **Performance Metrics**
- **Average Response Time**: {avg_response_time:.2f}s
- **Total Tokens Processed**: {sum(c['metrics'].get('word_count', 0) for c in self.conversation_history):,}
- **Success Rate**: {self.calculate_success_rate():.1f}%

### 📅 **Activity Timeline**
- **First Interaction**: {self.conversation_history[0]['timestamp'][:10]}
- **Latest Interaction**: {self.conversation_history[-1]['timestamp'][:10]}
- **Active Days**: {self.calculate_active_days()}
        """
        return overview
    
    def get_qa_analytics(self) -> str:
        """Get Q&A specific analytics"""
        qa_sessions = [c for c in self.conversation_history if 'question' in c]
        
        if not qa_sessions:
            return "💬 **No Q&A sessions recorded yet.**"
        
        expertise_stats = Counter(c['expertise'] for c in qa_sessions)
        model_stats = Counter(c['model'] for c in qa_sessions)
        
        avg_response_length = sum(len(c['answer']) for c in qa_sessions) / len(qa_sessions)
        fastest_response = min(c['metrics']['response_time'] for c in qa_sessions)
        slowest_response = max(c['metrics']['response_time'] for c in qa_sessions)
        
        qa_analytics = f"""
## 💬 **Q&A Analytics**

### 🎯 **Expertise Areas Used**
{chr(10).join([f"- **{expertise}**: {count} questions" for expertise, count in expertise_stats.most_common()])}

### 🤖 **Model Performance**
{chr(10).join([f"- **{model}**: {count} uses" for model, count in model_stats.most_common(5)])}

### 📊 **Response Analytics**
- **Average Response Length**: {avg_response_length:.0f} characters
- **Fastest Response**: {fastest_response:.2f}s
- **Slowest Response**: {slowest_response:.2f}s
- **Questions per Session**: {len(qa_sessions)}

### 💡 **Insights**
- **Most Popular Expertise**: {expertise_stats.most_common(1)[0][0]}
- **Most Used Model**: {model_stats.most_common(1)[0][0]}
        """
        return qa_analytics
    
    def get_code_generation_analytics(self) -> str:
        """Get code generation specific analytics"""
        code_sessions = [c for c in self.conversation_history if 'type' in c and c['type'] == 'code_generation']
        
        if not code_sessions:
            return "🚀 **No code generation sessions recorded yet.**"
        
        compilation_success = sum(1 for c in code_sessions if c.get('compilation_success', False))
        compilation_methods = Counter(c.get('compilation_method', 'unknown') for c in code_sessions)
        
        avg_generation_time = sum(c['metrics'].get('generation_time', 0) for c in code_sessions) / len(code_sessions)
        
        code_analytics = f"""
## 🚀 **Code Generation Analytics**

### ⚡ **Compilation Success Rate**
- **Successful Compilations**: {compilation_success}/{len(code_sessions)} ({compilation_success/len(code_sessions)*100:.1f}%)
- **Failed Compilations**: {len(code_sessions) - compilation_success}

### 🔧 **Compilation Methods**
{chr(10).join([f"- **{method}**: {count} uses" for method, count in compilation_methods.most_common()])}

### 📊 **Generation Performance**
- **Average Generation Time**: {avg_generation_time:.2f}s
- **Total Code Generated**: {sum(c.get('code_length', 0) for c in code_sessions):,} characters
- **Code Sessions**: {len(code_sessions)}

### 💡 **Optimization Insights**
- **Most Efficient Method**: {compilation_methods.most_common(1)[0][0] if compilation_methods else 'N/A'}
- **Success Rate**: {compilation_success/len(code_sessions)*100:.1f}%
        """
        return code_analytics
    
    def get_performance_analytics(self) -> str:
        """Get performance comparison analytics"""
        if not self.conversation_history:
            return "⚡ **No performance data available yet.**"
        
        provider_performance = defaultdict(list)
        model_performance = defaultdict(list)
        
        for conv in self.conversation_history:
            provider = conv['provider']
            model = conv['model']
            response_time = conv['metrics']['response_time']
            
            provider_performance[provider].append(response_time)
            model_performance[model].append(response_time)
        
        # Calculate averages
        provider_avgs = {p: sum(times)/len(times) for p, times in provider_performance.items()}
        model_avgs = {m: sum(times)/len(times) for m, times in model_performance.items()}
        
        performance_text = f"""
## ⚡ **Performance Analytics**

### 🤖 **Provider Performance Comparison**
{chr(10).join([f"- **{provider}**: {avg_time:.2f}s average ({len(times)} requests)" for provider, avg_time in sorted(provider_avgs.items(), key=lambda x: x[1])])}

### 🧠 **Model Performance**
{chr(10).join([f"- **{model}**: {avg_time:.2f}s average ({len(times)} requests)" for model, avg_time in sorted(model_avgs.items(), key=lambda x: x[1])[:5]])}

### 📊 **Performance Insights**
- **Fastest Provider**: {min(provider_avgs, key=provider_avgs.get)} ({min(provider_avgs.values()):.2f}s)
- **Fastest Model**: {min(model_avgs, key=model_avgs.get)} ({min(model_avgs.values()):.2f}s)
- **Performance Variance**: {max(provider_avgs.values()) - min(provider_avgs.values()):.2f}s
        """
        return performance_text
    
    def get_usage_trends(self) -> str:
        """Get usage trends over time"""
        if not self.conversation_history:
            return "📊 **No usage trends available yet.**"
        
        # Group by date
        daily_usage = defaultdict(int)
        provider_trends = defaultdict(lambda: defaultdict(int))
        
        for conv in self.conversation_history:
            date = conv['timestamp'][:10]
            provider = conv['provider']
            
            daily_usage[date] += 1
            provider_trends[provider][date] += 1
        
        trends_text = f"""
## 📊 **Usage Trends**

### 📅 **Daily Activity**
{chr(10).join([f"- **{date}**: {count} interactions" for date, count in sorted(daily_usage.items())[-7:]])}

### 📈 **Provider Trends**
{chr(10).join([f"#### **{provider}**" + chr(10) + chr(10).join([f"- **{date}**: {count} uses" for date, count in sorted(daily.items())[-3:]]) for provider, daily in provider_trends.items()])}

### 🎯 **Usage Patterns**
- **Most Active Day**: {max(daily_usage, key=daily_usage.get)} ({max(daily_usage.values())} interactions)
- **Average Daily Usage**: {sum(daily_usage.values())/len(daily_usage):.1f} interactions
- **Usage Span**: {len(daily_usage)} days
        """
        return trends_text
    
    def update_qa_analytics(self) -> Tuple[str, plt.Figure]:
        """Update Q&A analytics with charts"""
        qa_sessions = [c for c in self.conversation_history if 'question' in c]
        
        if not qa_sessions:
            return "💬 **No Q&A data available for charts.**", plt.figure()
        
        # Create charts
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 8))
        fig.suptitle('Q&A Analytics Dashboard', fontsize=16)
        
        # Expertise distribution
        expertise_counts = Counter(c['expertise'] for c in qa_sessions)
        ax1.pie(expertise_counts.values(), labels=expertise_counts.keys(), autopct='%1.1f%%')
        ax1.set_title('Expertise Areas')
        
        # Response times
        response_times = [c['metrics']['response_time'] for c in qa_sessions]
        ax2.hist(response_times, bins=10, alpha=0.7, color='skyblue')
        ax2.set_title('Response Time Distribution')
        ax2.set_xlabel('Response Time (s)')
        
        # Provider usage
        provider_counts = Counter(c['provider'] for c in qa_sessions)
        ax3.bar(provider_counts.keys(), provider_counts.values(), color='lightgreen')
        ax3.set_title('Provider Usage')
        ax3.set_ylabel('Number of Questions')
        
        # Daily usage
        daily_counts = Counter(c['timestamp'][:10] for c in qa_sessions)
        ax4.plot(list(daily_counts.keys()), list(daily_counts.values()), marker='o', color='orange')
        ax4.set_title('Daily Q&A Usage')
        ax4.set_xlabel('Date')
        ax4.set_ylabel('Questions')
        ax4.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        return self.get_qa_analytics(), fig
    
    def update_code_analytics(self) -> Tuple[str, plt.Figure]:
        """Update code generation analytics with charts"""
        code_sessions = [c for c in self.conversation_history if 'type' in c and c['type'] == 'code_generation']
        
        if not code_sessions:
            return "🚀 **No code generation data available for charts.**", plt.figure()
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 8))
        fig.suptitle('Code Generation Analytics Dashboard', fontsize=16)
        
        # Compilation success rate
        success_count = sum(1 for c in code_sessions if c.get('compilation_success', False))
        ax1.pie([success_count, len(code_sessions) - success_count], 
                labels=['Success', 'Failed'], autopct='%1.1f%%', colors=['green', 'red'])
        ax1.set_title('Compilation Success Rate')
        
        # Generation times
        gen_times = [c['metrics'].get('generation_time', 0) for c in code_sessions if c['metrics'].get('generation_time', 0) > 0]
        if gen_times:
            ax2.hist(gen_times, bins=10, alpha=0.7, color='lightblue')
            ax2.set_title('Generation Time Distribution')
            ax2.set_xlabel('Generation Time (s)')
        
        # Compilation methods
        methods = Counter(c.get('compilation_method', 'unknown') for c in code_sessions)
        ax3.bar(methods.keys(), methods.values(), color='orange')
        ax3.set_title('Compilation Methods')
        ax3.set_ylabel('Usage Count')
        
        # Code length distribution
        code_lengths = [c.get('code_length', 0) for c in code_sessions if c.get('code_length', 0) > 0]
        if code_lengths:
            ax4.hist(code_lengths, bins=10, alpha=0.7, color='purple')
            ax4.set_title('Generated Code Length')
            ax4.set_xlabel('Characters')
        
        plt.tight_layout()
        return self.get_code_generation_analytics(), fig
    
    def update_performance_analytics(self) -> Tuple[str, plt.Figure]:
        """Update performance analytics with charts"""
        if not self.conversation_history:
            return "⚡ **No performance data available for charts.**", plt.figure()
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        fig.suptitle('Performance Comparison Dashboard', fontsize=16)
        
        # Provider performance comparison
        provider_times = defaultdict(list)
        for conv in self.conversation_history:
            provider_times[conv['provider']].append(conv['metrics']['response_time'])
        
        provider_avgs = {p: sum(times)/len(times) for p, times in provider_times.items()}
        ax1.bar(provider_avgs.keys(), provider_avgs.values(), color='skyblue')
        ax1.set_title('Average Response Time by Provider')
        ax1.set_ylabel('Response Time (s)')
        ax1.tick_params(axis='x', rotation=45)
        
        # Response time trend
        timestamps = [datetime.fromisoformat(c['timestamp']) for c in self.conversation_history]
        response_times = [c['metrics']['response_time'] for c in self.conversation_history]
        
        ax2.scatter(timestamps, response_times, alpha=0.6, color='orange')
        ax2.set_title('Response Time Trend')
        ax2.set_xlabel('Time')
        ax2.set_ylabel('Response Time (s)')
        ax2.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        return self.get_performance_analytics(), fig
    
    def update_usage_trends(self) -> Tuple[str, plt.Figure]:
        """Update usage trends with charts"""
        if not self.conversation_history:
            return "📊 **No usage data available for charts.**", plt.figure()
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        fig.suptitle('Usage Trends Dashboard', fontsize=16)
        
        # Daily usage trend
        daily_usage = defaultdict(int)
        for conv in self.conversation_history:
            daily_usage[conv['timestamp'][:10]] += 1
        
        dates = sorted(daily_usage.keys())
        counts = [daily_usage[date] for date in dates]
        
        ax1.plot(dates, counts, marker='o', linewidth=2, color='blue')
        ax1.set_title('Daily Usage Trend')
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Interactions')
        ax1.tick_params(axis='x', rotation=45)
        
        # Hourly usage pattern
        hourly_usage = defaultdict(int)
        for conv in self.conversation_history:
            hour = datetime.fromisoformat(conv['timestamp']).hour
            hourly_usage[hour] += 1
        
        hours = sorted(hourly_usage.keys())
        hour_counts = [hourly_usage[hour] for hour in hours]
        
        ax2.bar(hours, hour_counts, color='green', alpha=0.7)
        ax2.set_title('Hourly Usage Pattern')
        ax2.set_xlabel('Hour of Day')
        ax2.set_ylabel('Usage Count')
        
        plt.tight_layout()
        return self.get_usage_trends(), fig
    
    def get_raw_analytics_data(self) -> pd.DataFrame:
        """Get raw analytics data as DataFrame"""
        if not self.conversation_history:
            return pd.DataFrame(columns=['Timestamp', 'Provider', 'Model', 'Type', 'Response Time', 'Success'])
        
        data = []
        for conv in self.conversation_history:
            data.append({
                'Timestamp': conv['timestamp'],
                'Provider': conv['provider'],
                'Model': conv['model'],
                'Type': conv.get('type', 'qa'),
                'Response Time': conv['metrics']['response_time'],
                'Success': conv.get('compilation_success', True),
                'Word Count': conv['metrics'].get('word_count', 0),
                'Expertise': conv.get('expertise', 'N/A')
            })
        
        return pd.DataFrame(data)
    
    def export_analytics(self) -> str:
        """Export analytics data to JSON"""
        export_data = {
            'conversation_history': self.conversation_history,
            'export_timestamp': datetime.now().isoformat(),
            'total_interactions': len(self.conversation_history),
            'analytics_summary': {
                'qa_sessions': len([c for c in self.conversation_history if 'question' in c]),
                'code_sessions': len([c for c in self.conversation_history if 'type' in c and c['type'] == 'code_generation']),
                'providers_used': list(set(c['provider'] for c in self.conversation_history)),
                'models_used': list(set(c['model'] for c in self.conversation_history))
            }
        }
        
        filename = f"questher_analytics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        return filename
    
    def clear_all_history(self) -> Tuple[str, str, str, str, str, pd.DataFrame]:
        """Clear all conversation history and reset analytics"""
        self.conversation_history = []
        return (
            "📊 **All analytics data cleared.**",
            "💬 **Q&A analytics cleared.**", 
            "🚀 **Code generation analytics cleared.**",
            "⚡ **Performance analytics cleared.**",
            "📊 **Usage trends cleared.**",
            pd.DataFrame()
        )
    
    # Helper methods for analytics calculations
    def calculate_success_rate(self) -> float:
        """Calculate overall success rate"""
        if not self.conversation_history:
            return 0.0
        
        successful = sum(1 for c in self.conversation_history if c.get('compilation_success', True))
        return (successful / len(self.conversation_history)) * 100
    
    def calculate_active_days(self) -> int:
        """Calculate number of active days"""
        if not self.conversation_history:
            return 0
        
        dates = set(c['timestamp'][:10] for c in self.conversation_history)
        return len(dates)
