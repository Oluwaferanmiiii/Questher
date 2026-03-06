#!/usr/bin/env python3
"""
Questher v3 CLI - Enhanced with Code Generation Commands
Command-line interface with Python→C++ conversion capabilities
"""

import sys
import argparse
from pathlib import Path
from typing import Optional

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

try:
    from src.ui_v3 import QuestherUI
    from src.factory import create_code_generator
    from src.config import settings
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure you're running this from project root directory")
    sys.exit(1)


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description="Questher v3 - Technical Q&A with Code Generation")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # UI command (existing functionality)
    ui_parser = subparsers.add_parser("ui", help="Launch web interface with Q&A and code generation")
    ui_parser.add_argument("--share", action="store_true", help="Share interface publicly")
    
    # Code generation command (new functionality)
    code_parser = subparsers.add_parser("generate", help="Generate C++ code from Python")
    code_parser.add_argument("--python", required=True, help="Python code file to convert")
    code_parser.add_argument("--model", default="gpt-5", help="AI model to use for code generation")
    code_parser.add_argument("--compile", action="store_true", help="Compile and run generated C++ code")
    code_parser.add_argument("--provider", default="openrouter", help="AI provider for code generation")
    
    args = parser.parse_args()
    
    if args.command == "ui":
        # Launch UI with code generation features
        ui = QuestherUI()
        interface = ui.create_interface()
        interface.launch(share=args.share)
        
    elif args.command == "generate":
        # Code generation mode
        print("🚀 Questher v3 - Code Generation Mode")
        print(f"📁 Python file: {args.python}")
        print(f"🤖 AI model: {args.model}")
        print(f"🔧 Provider: {args.provider}")
        
        # Read Python code from file
        try:
            with open(args.python, 'r', encoding='utf-8') as f:
                python_code = f.read()
        except FileNotFoundError:
            print(f"❌ Error: File '{args.python}' not found")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Error reading file: {e}")
            sys.exit(1)
        
        # Initialize code generator
        try:
            generator = create_code_generator(args.provider, args.model)
            result = generator.generate_cpp_from_python(python_code)
            
            print("✅ Code Generation Results:")
            print(f"📝 Model used: {result['model_used']}")
            print(f"⏱️  Execution time: {result['execution_time']:.2f}s")
            print(f"🧠 Reasoning effort: {result['reasoning_effort']}")
            print("\n🔧 Generated C++ Code:")
            print("-" * 50)
            print(result['cpp_code'])
            print("-" * 50)
            
            if args.compile:
                print("\n⚡ Compiling and running C++ code...")
                from src.compiler import CppCompiler
                compiler = CppCompiler()
                compile_result = compiler.compile_and_run(result['cpp_code'])
                
                if compile_result['success']:
                    print("✅ Compilation successful!")
                    print(f"📊 Performance: {compile_result['performance']}")
                    print(f"🏃️  Output:\n{compile_result['run_output']}")
                else:
                    print(f"❌ Compilation failed: {compile_result['error']}")
            
        except Exception as e:
            print(f"❌ Code generation failed: {e}")
            sys.exit(1)
    
    else:
        print("❌ Unknown command")
        parser.print_help()


if __name__ == "__main__":
    main()
