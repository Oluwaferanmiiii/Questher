#!/usr/bin/env python3
"""
Questher Installation and Configuration Script
Production-ready setup for the Questher technical question answering tool
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"{description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"{description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"{description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def check_python_version():
    """Check Python version compatibility"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("Python 3.8 or higher is required")
        return False
    print(f"Python {version.major}.{version.minor}.{version.micro} detected")
    return True

def setup_environment():
    """Setup environment and dependencies"""
    print("Setting up Questher Technical QA Tool Environment")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Install dependencies
    if not run_command(
        "pip install -r requirements.txt",
        "Installing Python dependencies"
    ):
        return False
    
    # Create .env file if it doesn't exist
    env_file = Path(".env")
    if not env_file.exists():
        print("Creating .env file from template...")
        try:
            with open(".env.example", "r") as template:
                content = template.read()
            with open(".env", "w") as env:
                env.write(content)
            print(".env file created")
            print("Please edit .env file with your API keys")
        except FileNotFoundError:
            print(".env.example not found, creating basic .env file")
            with open(".env", "w") as env:
                env.write("# OpenAI API Key (get from https://platform.openai.com/api-keys)\n")
                env.write("OPENAI_API_KEY=\n\n")
                env.write("# Optional: Google AI Studio API Key\n")
                env.write("GOOGLE_API_KEY=\n")
    
    # Check Ollama availability
    print("\nChecking Ollama availability...")
    try:
        import requests
        response = requests.get("http://localhost:11434", timeout=2)
        if response.status_code == 200:
            print("Ollama is running")
        else:
            print("Ollama responded with unexpected status")
    except:
        print("Ollama is not running")
        print("To install Ollama: visit https://ollama.com")
        print("To start Ollama: run 'ollama serve'")
    
    # Run tests
    print("\nRunning tests...")
    if run_command("python -m pytest tests/ -v", "Running test suite"):
        print("All tests passed")
    else:
        print("Some tests failed - this may be normal if API keys are not configured")
    
    return True

def main():
    """Main setup function"""
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    if setup_environment():
        print("\nSetup completed successfully!")
        print("Next steps:")
        print("1. Edit .env file with your API keys")
        print("2. Run 'python questher.py \"What is Python?\"' to test")
        print("3. Open 'notebooks/demo.ipynb' for interactive demo")
        print("4. Read 'README.md' for full documentation")
    else:
        print("\nSetup failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
