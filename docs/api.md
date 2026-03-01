# API Documentation

## Overview

The Technical QA Tool provides a RESTful API for technical question answering with support for multiple LLM providers.

## Base URL

```
http://localhost:8000
```

## Authentication

Currently no authentication is required (for development). In production, implement appropriate authentication mechanisms.

## Endpoints

### GET /

Root endpoint with basic information.

**Response:**
```json
{
  "message": "Technical QA API",
  "version": "1.0.0",
  "docs": "/docs"
}
```

### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": 1640995200.0
}
```

### GET /models

Get information about available models.

**Response:**
```json
{
  "provider": "openai",
  "model": "gpt-4o-mini",
  "ollama_available": true,
  "openai_available": true
}
```

### POST /ask

Ask a technical question.

**Request Body:**
```json
{
  "question": "What is a Python generator?",
  "provider": "auto",
  "model": null,
  "stream": false
}
```

**Response:**
```json
{
  "answer": "A Python generator is a special type of iterator...",
  "provider": "openai",
  "model": "gpt-4o-mini",
  "response_time": 1.23,
  "metrics": {
    "question_length": 25,
    "answer_length": 500,
    "word_count": 85,
    "response_time": 1.23,
    "words_per_second": 69.1,
    "characters_per_second": 406.5
  }
}
```

### POST /compare

Compare responses from different models.

**Request Body:**
```json
"What is the difference between list and tuple in Python?"
```

**Response:**
```json
{
  "question": "What is the difference between list and tuple in Python?",
  "responses": {
    "gpt-4o-mini": "Lists are mutable...",
    "llama3.2 (Ollama)": "Lists and tuples are both sequence types..."
  }
}
```

## Error Responses

All endpoints return appropriate HTTP status codes and error messages:

```json
{
  "detail": "Error description"
}
```

Common status codes:
- 400: Bad Request (invalid input)
- 500: Internal Server Error
- 503: Service Unavailable (QA tool not initialized)

## Interactive Documentation

Visit `/docs` for interactive Swagger UI documentation.
Visit `/redoc` for ReDoc documentation.
