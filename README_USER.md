# Questher - Technical Question Answering Tool

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/questher/questher)
[![Python](https://img.shields.io/badge/python-3.8+-green.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-purple.svg)](LICENSE)

**Questher** is a powerful technical question answering tool that leverages multiple AI providers to deliver accurate, detailed explanations for programming and technical concepts.

## Quick Start

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd Questher

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate

# Install Questher as a package
pip install -e .

# Set up your API keys in .env file
cp .env.example .env
# Edit .env with your API keys
```

### Basic Usage

```bash
# Ask a technical question
questher "What is Python?"

# Or use module syntax
python -m questher "What is a generator?"

# Windows batch file
questher.bat "Explain decorators"
```

## Features

### Streaming Responses
Get real-time answers as they're being generated:
```bash
python -m questher --stream "Explain async programming"
```

### Performance Metrics
Track response time and speed:
```bash
python -m questher --metrics "What are list comprehensions?"
```

### Provider Comparison
Compare answers from different AI models:
```bash
python -m questher --compare "List vs Tuple"
```

### Provider Selection
Choose your preferred AI provider:
```bash
python -m questher --provider openrouter "What is OOP?"
python -m questher --provider openai "Explain recursion"
python -m questher --provider ollama "What is a decorator?"
```

### Debug Mode
Get detailed logging for troubleshooting:
```bash
python -m questher --verbose "Debug this code"
```

## Command Reference

| Option | Description | Example |
|--------|-------------|---------|
| `--provider` | Choose AI provider (auto/openai/ollama/openrouter) | `--provider openrouter` |
| `--model` | Specific model to use | `--model "anthropic/claude-3.5-haiku"` |
| `--stream` | Real-time response streaming | `--stream` |
| `--compare` | Compare all available providers | `--compare` |
| `--metrics` | Show performance statistics | `--metrics` |
| `--verbose` | Enable debug logging | `--verbose` |
| `--version` | Show version information | `--version` |
| `--help` | Display help message | `--help` |

## Configuration

### Environment Variables
Create a `.env` file with your API keys:

```bash
# OpenAI API Key
OPENAI_API_KEY=sk-proj-your-openai-key-here

# OpenRouter API Key  
OPENROUTER_API_KEY=sk-or-your-openrouter-key-here

# Optional: Custom model settings
OPENAI_MODEL=gpt-4o-mini
OLLAMA_MODEL=llama3.2
DEFAULT_TEMPERATURE=0.7
DEFAULT_MAX_TOKENS=2000
```

### Provider Priority
Questher automatically detects and prioritizes providers:
1. **Ollama** (free, local) - if available
2. **OpenRouter** (cost-effective) - if API key configured  
3. **OpenAI** (premium) - if API key configured

## Use Cases

### Learning & Education
- Get detailed explanations of programming concepts
- Compare different AI teaching styles
- Learn with real-time streaming responses

### Development Support
- Debug code issues with AI assistance
- Get best practices and optimization tips
- Understand complex algorithms and patterns

### Documentation & Research
- Generate technical documentation
- Research programming topics
- Create educational content

### Testing & Quality Assurance
- Compare AI model responses
- Test different providers for quality
- Benchmark performance metrics

## Architecture

Questher is built with a clean, modular architecture:

```
Questher/
├── questher/           # Main package
│   ├── __init__.py    # Package initialization
│   ├── __main__.py    # Entry point
│   └── cli.py         # CLI functionality
├── src/               # Core application
│   ├── core.py        # Main QA engine
│   ├── config.py      # Configuration management
│   ├── factory.py     # Provider factory
│   └── utils.py       # Utilities
├── scripts/           # Supporting scripts
├── tests/             # Test suite
└── docs/              # Documentation
```

## Advanced Usage

### Combining Features
```bash
# Streaming with performance metrics
python -m questher --stream --metrics "Explain decorators"

# Verbose provider comparison
python -m questher --verbose --compare "List vs Tuple"

# Specific provider with metrics
python -m questher --provider openrouter --metrics "What is async?"
```

### Python API
```python
from src import create_qa_tool

# Create QA tool with auto-detection
qa = create_qa_tool()

# Ask a question
answer = qa.ask_question("What is Python?")
print(answer)

# Stream response
for chunk in qa.ask_question_stream("Explain generators"):
    print(chunk, end='', flush=True)

# Compare providers
responses = qa.compare_models("List vs Tuple")
for provider, response in responses.items():
    print(f"{provider}: {response}")
```

## Troubleshooting

### Common Issues

**Module Import Error**
```bash
# Make sure you're in the Questher directory
cd Questher
python -m questher "test question"
```

**API Key Issues**
```bash
# Check your .env file
cat .env

# Test with verbose mode
python -m questher --verbose "test question"
```

**Virtual Environment Issues**
```bash
# Recreate virtual environment
python -m venv .venv
.venv\Scripts\activate
pip install -e .
```

### Getting Help

```bash
# Show all options
python -m questher --help

# Check version
python -m questher --version

# Enable debug logging
python -m questher --verbose "test question"
```

## Performance Tips

- **Use Ollama** for free, local processing
- **Use OpenRouter** for cost-effective multi-model access
- **Enable metrics** to track response times
- **Use streaming** for better user experience with long answers
- **Compare providers** to find best responses for your needs

## Contributing

Questher is open to contributions! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Links

- [Repository](https://github.com/questher/questher)
- [Documentation](https://github.com/questher/questher/blob/main/docs/)
- [Issues](https://github.com/questher/questher/issues)
- [Discussions](https://github.com/questher/questher/discussions)

---

**Questher** - Your intelligent technical question answering companion!

*Built with care for developers, students, and technical professionals.*
