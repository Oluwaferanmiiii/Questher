#!/usr/bin/env python3
"""
Development server for Technical QA tool
FastAPI web interface for enterprise deployment
"""

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src import create_qa_tool
from src.utils import setup_logging, calculate_metrics
from src.exceptions import TechnicalQAError

# Setup logging
logger = setup_logging()

# Initialize FastAPI app
app = FastAPI(
    title="Technical QA API",
    description="Enterprise-grade technical question answering API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/response models
class QuestionRequest(BaseModel):
    question: str
    provider: Optional[str] = "auto"
    model: Optional[str] = None
    stream: Optional[bool] = False

class QuestionResponse(BaseModel):
    answer: str
    provider: str
    model: str
    response_time: float
    metrics: Dict[str, Any]

class ModelInfo(BaseModel):
    provider: str
    model: str
    ollama_available: bool
    openai_available: bool

# Global QA tool instance
qa_tool = None

@app.on_event("startup")
async def startup_event():
    """Initialize the QA tool on startup"""
    global qa_tool
    try:
        qa_tool = create_qa_tool()
        logger.info("Technical QA tool initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize QA tool: {e}")
        qa_tool = None

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Technical QA API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy" if qa_tool else "unhealthy",
        "timestamp": time.time()
    }

@app.get("/models", response_model=ModelInfo)
async def get_models():
    """Get available model information"""
    if not qa_tool:
        raise HTTPException(status_code=503, detail="QA tool not initialized")
    
    info = qa_tool.get_model_info()
    return ModelInfo(
        provider=info["provider"],
        model=info["model_name"],
        ollama_available=info["ollama_available"],
        openai_available=info["openai_available"]
    )

@app.post("/ask", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest):
    """Ask a technical question"""
    if not qa_tool:
        raise HTTPException(status_code=503, detail="QA tool not initialized")
    
    try:
        # Create new QA tool if different provider/model requested
        if request.provider != "auto" or request.model:
            qa = create_qa_tool(provider=request.provider, model_name=request.model)
        else:
            qa = qa_tool
        
        start_time = time.time()
        answer = qa.ask_question(request.question, stream=request.stream)
        response_time = time.time() - start_time
        
        metrics = calculate_metrics(request.question, answer, response_time)
        
        info = qa.get_model_info()
        
        return QuestionResponse(
            answer=answer,
            provider=info["provider"],
            model=info["model_name"],
            response_time=response_time,
            metrics=metrics
        )
        
    except TechnicalQAError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/compare")
async def compare_models(question: str):
    """Compare responses from different models"""
    if not qa_tool:
        raise HTTPException(status_code=503, detail="QA tool not initialized")
    
    try:
        responses = qa_tool.compare_models(question)
        return {
            "question": question,
            "responses": responses
        }
    except Exception as e:
        logger.error(f"Comparison error: {e}")
        raise HTTPException(status_code=500, detail="Comparison failed")

if __name__ == "__main__":
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
