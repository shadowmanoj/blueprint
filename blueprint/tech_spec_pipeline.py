#!/usr/bin/env python3
"""Technical Specification Generation Pipeline."""

import os
import argparse
import logging
import yaml
import json
from datetime import datetime

from helpers.file_reader import read_file
from helpers.utils import get_timestamp, load_json, save_json
from services.analyzer import Analyzer
from services.planner import Planner
from services.spec_generator import SpecGenerator
from services.llm_service import LLMService
from services.context_retriever import ContextRetriever


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TechSpecPipeline:
    """Pipeline for generating technical specifications from PRD documents."""
    
    def __init__(self, config=None):
        """Initialize the pipeline with configuration.
        
        Args:
            config (dict, optional): Pipeline configuration. Defaults to None.
        """
        self.config = config or {}
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Configure paths
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.input_dir = self.config.get('input_dir') or os.path.join(self.base_dir, 'input')
        self.output_dir = self.config.get('output_dir') or os.path.join(self.base_dir, 'output')
        self.context_dir = self.config.get('context_dir') or os.path.join(self.base_dir, 'context')
        self.repo_context_dir = self.config.get('repo_context_dir') or os.path.join(self.base_dir, 'repo_context')
        
        # Ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Initialize components
        self._init_components()
    
    def _init_components(self):
        """Initialize pipeline components."""
        # Load paths for components
        repo_rules_path = self.config.get('repo_rules_path') or os.path.join(self.context_dir, 'repo_rules.yaml')
        guidelines_path = self.config.get('guidelines_path') or os.path.join(self.context_dir, 'guidelines.md')
        
        # Initialize services
        self.analyzer = Analyzer(self.config.get('analyzer_config'))
        self.planner = Planner(repo_rules_path)
        self.spec_generator = SpecGenerator(guidelines_path)
        self.context_retriever = ContextRetriever(self.repo_context_dir)
        
        # Initialize LLM service if API key is available
        api_key = self.config.get('openai_api_key') or os.environ.get('OPENAI_API_KEY')
        if api_key:
            self.llm_service = LLMService(api_key=api_key, context_base_path=self.repo_context_dir)
            logger.info("LLM service initialized.")
        else:
            self.llm_service = None
            logger.warning("No OpenAI API key found. LLM-enhanced processing will be unavailable.")
    
    def process_document(self, input_path, output_path=None):
        """Process a PRD document to generate a technical specification.
        
        Args:
            input_path (str): Path to the input document
            output_path (str, optional): Path for the output spec. Defaults to None.
            
        Returns:
            dict: Results of the pipeline execution
        """
        # Generate output path if not provided
        if not output_path:
            filename = os.path.splitext(os.path.basename(input_path))[0]
            output_path = os.path.join(self.output_dir, f"{filename}_spec_{self.timestamp}")
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        logger.info(f"Processing document: {input_path}")
        logger.info(f"Output will be saved to: {output_path}")
        
        try:
            # Step 1: Read the document
            document_text = read_file(input_path)
            logger.info(f"Document read successfully: {len(document_text)} characters")
            
            # Step 2: Analyze the document
            if self.llm_service:
                # Use LLM for analysis
                extracted_info = self.llm_service.analyze_document(document_text)
                logger.info("Document analyzed using LLM")
            else:
                # Use rule-based analyzer
                extracted_info = self.analyzer.analyze(document_text)
                logger.info("Document analyzed using rule-based analyzer")
            
            # Save the extracted information
            analysis_output_path = f"{output_path}_analysis.json"
            save_json(extracted_info, analysis_output_path)
            logger.info(f"Analysis saved to: {analysis_output_path}")
            
            # Step 3: Plan the architecture
            # Load repository rules
            repo_rules = self.planner.repo_rules
            
            if self.llm_service:
                # Use LLM for planning
                architecture_plan = self.llm_service.plan_architecture(extracted_info, repo_rules)
                logger.info("Architecture planned using LLM with domain context")
            else:
                # Use rule-based planner
                architecture_plan = self.planner.plan(extracted_info)
                logger.info("Architecture planned using rule-based planner")
            
            # Save the architecture plan
            plan_output_path = f"{output_path}_plan.json"
            save_json(architecture_plan, plan_output_path)
            logger.info(f"Architecture plan saved to: {plan_output_path}")
            
            # Step 4: Generate the technical specification
            guidelines = self.spec_generator.guidelines
            
            if self.llm_service:
                # Use LLM for spec generation
                spec = self.llm_service.generate_tech_spec(architecture_plan, extracted_info, guidelines)
                logger.info("Technical specification generated using LLM with domain context")
            else:
                # Use template-based generator
                spec = self.spec_generator.generate_spec(architecture_plan, extracted_info)
                logger.info("Technical specification generated using template")
            
            # Save the specification
            spec_output_path = f"{output_path}.md"
            with open(spec_output_path, 'w', encoding='utf-8') as f:
                f.write(spec)
            logger.info(f"Technical specification saved to: {spec_output_path}")
            
            # Step 5: Generate code examples if requested
            if self.config.get('generate_code_examples', False) and self.llm_service:
                code_examples = self.llm_service.generate_code_examples(spec)
                code_examples_path = f"{output_path}_code_examples.md"
                
                # Format code examples as a markdown document
                code_md = "# Code Examples\n\n"
                for category, code in code_examples.items():
                    code_md += f"## {category}\n\n{code}\n\n"
                
                with open(code_examples_path, 'w', encoding='utf-8') as f:
                    f.write(code_md)
                logger.info(f"Code examples saved to: {code_examples_path}")
            
            # Generate HTML version if requested
            if self.config.get('generate_html', False):
                html_output_path = self.spec_generator.save_output(spec, spec_output_path, format="html")
                logger.info(f"HTML version saved to: {html_output_path}")
            
            # Prepare result summary
            results = {
                "input_document": input_path,
                "analysis_output": analysis_output_path,
                "plan_output": plan_output_path,
                "spec_output": spec_output_path,
                "timestamp": get_timestamp(),
                "success": True,
                "domain_context_used": True if self.llm_service else False
            }
            
            if self.config.get('generate_code_examples', False) and self.llm_service:
                results["code_examples_output"] = code_examples_path
            
            return results
            
        except Exception as e:
            logger.error(f"Error processing document: {str(e)}", exc_info=True)
            return {
                "input_document": input_path,
                "error": str(e),
                "timestamp": get_timestamp(),
                "success": False
            }
    
    def process_directory(self, input_dir=None, output_dir=None):
        """Process all documents in a directory.
        
        Args:
            input_dir (str, optional): Input directory. Defaults to None.
            output_dir (str, optional): Output directory. Defaults to None.
            
        Returns:
            list: Results for each processed document
        """
        input_dir = input_dir or self.input_dir
        output_dir = output_dir or self.output_dir
        
        results = []
        
        # Get all files in input directory
        valid_extensions = ['.pdf', '.docx', '.txt', '.md']
        files = [f for f in os.listdir(input_dir) 
                if os.path.isfile(os.path.join(input_dir, f)) and 
                any(f.endswith(ext) for ext in valid_extensions)]
        
        logger.info(f"Found {len(files)} documents to process in {input_dir}")
        
        for file in files:
            input_path = os.path.join(input_dir, file)
            filename = os.path.splitext(file)[0]
            output_path = os.path.join(output_dir, filename)
            
            result = self.process_document(input_path, output_path)
            results.append(result)
        
        return results


def main():
    """Main function for running the pipeline from command line."""
    parser = argparse.ArgumentParser(description="Technical Specification Generator Pipeline")
    parser.add_argument("--input", "-i", help="Input document path or directory")
    parser.add_argument("--output", "-o", help="Output path or directory")
    parser.add_argument("--config", "-c", help="Configuration file path")
    parser.add_argument("--openai-key", help="OpenAI API key (overrides env var and config)")
    parser.add_argument("--html", action="store_true", help="Generate HTML output in addition to Markdown")
    parser.add_argument("--code-examples", action="store_true", help="Generate code examples for the technical spec")
    parser.add_argument("--repo-context", help="Path to repository context directory")
    
    args = parser.parse_args()
    
    # Load configuration
    config = {}
    if args.config and os.path.exists(args.config):
        with open(args.config, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
    
    # Override config with command line arguments
    if args.openai_key:
        config['openai_api_key'] = args.openai_key
    
    if args.html:
        config['generate_html'] = True
    
    if args.code_examples:
        config['generate_code_examples'] = True
    
    if args.repo_context:
        config['repo_context_dir'] = args.repo_context
    
    # Initialize pipeline
    pipeline = TechSpecPipeline(config)
    
    # Process input
    if args.input:
        if os.path.isdir(args.input):
            # Process directory
            output_dir = args.output if args.output else None
            results = pipeline.process_directory(args.input, output_dir)
            
            # Save results summary
            summary_path = os.path.join(pipeline.output_dir, f"summary_{pipeline.timestamp}.json")
            save_json(results, summary_path)
            logger.info(f"Processing summary saved to: {summary_path}")
            
            # Print summary
            success_count = sum(1 for r in results if r['success'])
            logger.info(f"Processed {len(results)} documents. {success_count} successful, {len(results) - success_count} failed.")
        
        elif os.path.isfile(args.input):
            # Process single file
            result = pipeline.process_document(args.input, args.output)
            
            # Print result
            if result['success']:
                logger.info(f"Document processed successfully. Output: {result['spec_output']}")
            else:
                logger.error(f"Document processing failed: {result['error']}")
        
        else:
            logger.error(f"Input path does not exist: {args.input}")
    
    else:
        # No input specified, process all files in input directory
        results = pipeline.process_directory()
        
        # Save results summary
        summary_path = os.path.join(pipeline.output_dir, f"summary_{pipeline.timestamp}.json")
        save_json(results, summary_path)
        logger.info(f"Processing summary saved to: {summary_path}")
        
        # Print summary
        success_count = sum(1 for r in results if r['success'])
        logger.info(f"Processed {len(results)} documents. {success_count} successful, {len(results) - success_count} failed.")


if __name__ == "__main__":
    main() 