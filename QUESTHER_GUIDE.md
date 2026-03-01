# Questher - Technical Question Answering CLI

## 🎯 Overview

Questher is a custom CLI tool for your week1-solution project that allows you to ask technical questions and get detailed AI-powered answers.

## 🚀 Quick Start

### Method 1: Direct Python (Recommended)
```bash
.venv\Scripts\python.exe questher.py "Your question here"
```

### Method 2: Batch File (CMD only)
```cmd
questher.bat "Your question here"
```

### Method 3: Using cmd in PowerShell
```powershell
cmd /c "questher.bat \"Your question here\""
```

## 📋 Command Options

### Basic Usage
```bash
# Simple question
.venv\Scripts\python.exe questher.py "What is Python?"

# With specific provider
.venv\Scripts\python.exe questher.py --provider openai "Explain decorators"

# With specific model
.venv\Scripts\python.exe questher.py --provider openrouter --model "anthropic/claude-3.5-sonnet" "What is async?"
```

### Advanced Options
```bash
# Streaming response
.venv\Scripts\python.exe questher.py --stream "Explain generators"

# With performance metrics
.venv\Scripts\python.exe questher.py --metrics "What is OOP?"

# Compare all providers
.venv\Scripts\python.exe questher.py --compare "List vs Tuple"

# Verbose logging
.venv\Scripts\python.exe questher.py --verbose "Debug this code"

# Combined options
.venv\Scripts\python.exe questher.py --stream --metrics --verbose "Explain decorators"
```

### Help and Version
```bash
# Show help
.venv\Scripts\python.exe questher.py --help

# Show version
.venv\Scripts\python.exe questher.py --version
```

## 🎨 Features

### ✅ Core Features
- **Auto-detection**: Automatically finds the best available provider
- **Multiple Providers**: OpenAI, OpenRouter, Ollama support
- **Streaming**: Real-time response streaming
- **Metrics**: Performance analysis and timing
- **Comparison**: Side-by-side provider comparison
- **Clean Output**: Emoji-free, professional interface

### 📊 Performance Metrics
When using `--metrics`, you'll see:
- Response time
- Answer length (characters)
- Word count
- Processing speed (words/sec)
- Throughput (chars/sec)

## 🔧 Provider Options

| Provider | Command | Notes |
|----------|---------|-------|
| Auto-detect | `--provider auto` (default) | Finds best available |
| OpenRouter | `--provider openrouter` | Cost-effective multi-model |
| OpenAI | `--provider openai` | Requires API key |
| Ollama | `--provider ollama` | Free local models |

## 💡 Usage Examples

### Web Development Questions
```bash
.venv\Scripts\python.exe questher.py "What is REST API design?"
.venv\Scripts\python.exe questher.py --stream "Explain JWT authentication"
.venv\Scripts\python.exe questher.py --metrics "Compare SQL vs NoSQL"
```

### Python Programming
```bash
.venv\Scripts\python.exe questher.py "What are Python decorators?"
.venv\Scripts\python.exe questher.py --stream "Explain async/await"
.venv\Scripts\python.exe questher.py --compare "List comprehension vs generator"
```

### Code Debugging
```bash
.venv\Scripts\python.exe questher.py --verbose "Debug this Python error"
.venv\Scripts\python.exe questher.py --metrics "Optimize this code"
```

## 🛠️ Troubleshooting

### Common Issues

1. **Module Import Error**
   ```bash
   # Make sure you're in the project directory
   cd week1-solution
   .venv\Scripts\python.exe questher.py "test"
   ```

2. **Virtual Environment Issues**
   ```bash
   # Recreate if needed
   python -m venv .venv
   .venv\Scripts\python.exe -m pip install -r requirements.txt
   ```

3. **API Key Issues**
   ```bash
   # Check your .env file
   type .env
   ```

### PowerShell Issues
If PowerShell gives execution policy errors:
```powershell
# Allow script execution (run once)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then use direct Python instead of batch file
.venv\Scripts\python.exe questher.py "Your question"
```

## 🎯 Pro Tips

1. **Use quotes for questions with spaces**
2. **Add `--metrics` for performance analysis**
3. **Use `--stream` for long answers**
4. **Try `--compare` to see different provider responses**
5. **Use `--verbose` for debugging connection issues**

## 📝 Example Session

```bash
# Start with a simple question
.venv\Scripts\python.exe questher.py "What is Python?"

# Get detailed explanation with metrics
.venv\Scripts\python.exe questher.py --metrics "Explain decorators"

# Compare providers
.venv\Scripts\python.exe questher.py --compare "List vs Tuple"

# Stream a complex topic
.venv\Scripts\python.exe questher.py --stream "How does async work in Python?"
```

Questher is now ready to help with all your technical questions! 🚀
