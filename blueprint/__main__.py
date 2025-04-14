"""Main entry point for the blueprint package."""

import argparse
import sys
from blueprint import Blueprint, Reviewer, Generator, TextProcessor


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Blueprint - A text processing and generation framework")
    parser.add_argument("--mode", choices=["review", "generate", "process"], default="review",
                        help="Operating mode (review, generate, or process)")
    parser.add_argument("--text", type=str, help="Text to process")
    parser.add_argument("--input-file", type=str, help="Input file path")
    parser.add_argument("--output-file", type=str, help="Output file path")
    return parser.parse_args()


def main():
    """Run the main function of the blueprint package."""
    args = parse_args()
    
    # Get input text
    input_text = args.text
    if args.input_file:
        try:
            with open(args.input_file, 'r', encoding='utf-8') as f:
                input_text = f.read()
        except IOError as e:
            print(f"Error reading input file: {e}", file=sys.stderr)
            sys.exit(1)
    
    if not input_text:
        print("No input text provided. Use --text or --input-file", file=sys.stderr)
        sys.exit(1)
    
    # Process according to mode
    result = None
    if args.mode == "review":
        reviewer = Reviewer()
        result = reviewer.review(input_text)
        print(f"Review results: {result}")
    
    elif args.mode == "generate":
        generator = Generator()
        result = generator.generate(input_text)
        print(f"Generated text: {result}")
    
    elif args.mode == "process":
        processor = TextProcessor()
        tokens = processor.tokenize(input_text)
        summary = processor.summarize(input_text)
        result = {
            "tokens": tokens,
            "summary": summary,
            "token_count": len(tokens)
        }
        print(f"Processing results: {result}")
    
    # Output to file if requested
    if args.output_file and result:
        try:
            with open(args.output_file, 'w', encoding='utf-8') as f:
                if isinstance(result, str):
                    f.write(result)
                else:
                    import json
                    json.dump(result, f, indent=2)
            print(f"Results written to {args.output_file}")
        except IOError as e:
            print(f"Error writing to output file: {e}", file=sys.stderr)


if __name__ == "__main__":
    main() 