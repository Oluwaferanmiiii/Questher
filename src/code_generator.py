#!/usr/bin/env python3
"""
Code Generator Module for Questher v3
Converts Python code to optimized C++ using frontier AI models
"""

import time
from typing import Dict, List, Optional
from openai import OpenAI


class CodeGenerator:
    """Generates optimized C++ code from Python using frontier models"""
    
    def __init__(self, client: OpenAI, model_name: str):
        self.client = client
        self.model_name = model_name
        
    def generate_cpp_from_python(self, python_code: str) -> str:
        """Convert Python code to high-performance C++"""
        system_prompt = """
        Convert Python code to high-performance C++ code.
        Focus on optimization, speed, and native compilation.
        The C++ response needs to produce an identical output in the fastest possible time.
        Respond only with C++ code. Do not provide any explanation other than occasional comments.
        The C++ response needs to produce an identical output in the least time.
        """
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Port this Python code to C++:\n{python_code}"}
        ]
        
        reasoning_effort = "high" if "gpt" in self.model_name else None
        
        start_time = time.time()
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            reasoning_effort=reasoning_effort
        )
        
        cpp_code = response.choices[0].message.content
        # Clean up code blocks
        cpp_code = cpp_code.replace('```cpp','').replace('```','')
        
        execution_time = time.time() - start_time
        
        return {
            'cpp_code': cpp_code,
            'execution_time': execution_time,
            'model_used': self.model_name,
            'reasoning_effort': reasoning_effort
        }
        
    def get_supported_models(self) -> List[str]:
        """Get list of supported models for code generation"""
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
