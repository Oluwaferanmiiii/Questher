#!/usr/bin/env python3
"""
Questher - Technical Question Answering CLI Tool
A custom CLI for Questher project
"""

import sys
import os
import time
import argparse
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

try:
    from src import create_qa_tool
    from src.utils import setup_logging
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure you're running this from the project root directory")
    sys.exit(1)


def format_response_time(seconds):
    """Format response time in human readable format"""
    if seconds < 1:
        return f"{seconds*1000:.0f}ms"
    elif seconds < 60:
        return f"{seconds:.1f}s"
    else:
        return f"{seconds/60:.1f}min"


def calculate_metrics(question, answer, response_time):
    """Calculate performance metrics"""
    word_count = len(answer.split())
    char_count = len(answer)
    return {
        'response_time': response_time,
        'word_count': word_count,
        'answer_length': char_count,
        'words_per_second': word_count / response_time if response_time > 0 else 0,
        'characters_per_second': char_count / response_time if response_time > 0 else 0
    }


def print_metrics(metrics):
    """Print performance metrics"""
    print("\nPerformance Metrics:")
    print("-" * 30)
    print(f"Response time: {format_response_time(metrics['response_time'])}")
    print(f"Answer length: {metrics['answer_length']} chars")
    print(f"Word count: {metrics['word_count']} words")
    print(f"Speed: {metrics['words_per_second']:.1f} words/sec")
    print(f"Throughput: {metrics['characters_per_second']:.1f} chars/sec")


def main():
    """Main Questher CLI function"""
    parser = argparse.ArgumentParser(
        prog='questher',
        description='Questher - Technical Question Answering Tool',
        epilog='Ask technical questions and get detailed explanations from AI models'
    )
    
    parser.add_argument(
        'question',
        help='Your technical question to be answered'
    )
    
    parser.add_argument(
        '--provider',
        choices=['openai', 'ollama', 'openrouter', 'auto'],
        default='auto',
        help='LLM provider to use (default: auto-detect)'
    )
    
    parser.add_argument(
        '--model',
        help='Specific model to use (provider-specific)'
    )
    
    parser.add_argument(
        '--stream',
        action='store_true',
        help='Stream the response in real-time'
    )
    
    parser.add_argument(
        '--compare',
        action='store_true',
        help='Compare responses from all available providers'
    )
    
    parser.add_argument(
        '--metrics',
        action='store_true',
        help='Show performance metrics'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='Questher 1.0.0'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = "DEBUG" if args.verbose else "INFO"
    logger = setup_logging(log_level)
    
    try:
        # Create QA tool
        if args.provider == 'auto':
            qa = create_qa_tool()
        else:
            qa = create_qa_tool(provider=args.provider, model_name=args.model)
        
        # Display model info
        info = qa.get_model_info()
        print(f"Questher - Using: {info['model_name']} ({info['provider']})")
        print(f"Question: {args.question}")
        print()
        
        start_time = time.time()
        
        if args.compare:
            # Compare models
            print("Comparing models:")
            print("=" * 50)
            
            responses = qa.compare_models(args.question)
            for model_name, response in responses.items():
                print(f"\n {model_name}:")
                print("-" * 30)
                print(response)
                print()
            
            total_time = time.time() - start_time
            print(f"Total time: {format_response_time(total_time)}")
            
        elif args.stream:
            # Stream response
            print("Answer (streaming):")
            print("-" * 50)
            
            answer_chunks = []
            for chunk in qa.ask_question_stream(args.question):
                print(chunk, end='', flush=True)
                answer_chunks.append(chunk)
            
            answer = ''.join(answer_chunks)
            print("\n" + "-" * 50)
            
            if args.metrics:
                response_time = time.time() - start_time
                metrics = calculate_metrics(args.question, answer, response_time)
                print_metrics(metrics)
                
        else:
            # Regular response
            answer = qa.ask_question(args.question)
            response_time = time.time() - start_time
            
            print("Answer:")
            print("-" * 50)
            print(answer)
            print("-" * 50)
            
            if args.metrics:
                metrics = calculate_metrics(args.question, answer, response_time)
                print_metrics(metrics)
        
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
