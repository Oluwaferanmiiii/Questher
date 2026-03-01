#!/usr/bin/env python3
"""
CLI interface for Technical QA tool
Enterprise command-line interface
"""

import argparse
import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src import create_qa_tool
from src.utils import setup_logging, calculate_metrics, format_response_time

def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(
        description="Technical Question Answering Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli.py "What is a Python generator?"
  python cli.py --provider openai "Explain async/await"
  python cli.py --provider ollama --stream "What is REST API?"
  python cli.py --compare "Difference between list and tuple"
        """
    )
    
    parser.add_argument(
        "question",
        help="Technical question to answer"
    )
    
    parser.add_argument(
        "--provider",
        choices=["auto", "openai", "ollama", "openrouter"],
        default="auto",
        help="LLM provider to use (default: auto)"
    )
    
    parser.add_argument(
        "--model",
        help="Specific model name to use"
    )
    
    parser.add_argument(
        "--stream",
        action="store_true",
        help="Stream the response in real-time"
    )
    
    parser.add_argument(
        "--compare",
        action="store_true",
        help="Compare responses from different models"
    )
    
    parser.add_argument(
        "--metrics",
        action="store_true",
        help="Show performance metrics"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = "DEBUG" if args.verbose else "INFO"
    logger = setup_logging(log_level)
    
    try:
        # Create QA tool
        qa = create_qa_tool(provider=args.provider, model_name=args.model)
        
        # Display model info
        info = qa.get_model_info()
        print(f"Using: {info['model_name']} ({info['provider']})")
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

def print_metrics(metrics):
    """Print performance metrics"""
    print("\nPerformance Metrics:")
    print("-" * 30)
    print(f"Response time: {format_response_time(metrics['response_time'])}")
    print(f"Answer length: {metrics['answer_length']} chars")
    print(f"Word count: {metrics['word_count']} words")
    print(f"Speed: {metrics['words_per_second']:.1f} words/sec")
    print(f"Throughput: {metrics['characters_per_second']:.1f} chars/sec")

if __name__ == "__main__":
    main()
