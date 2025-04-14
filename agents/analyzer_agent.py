"""
PRD Analyzer Agent for extracting structured information from Product Requirement Documents.
"""
import json
import os
import yaml
from typing import Dict, Any, List, Optional

import openai

from utils.file_loader import extract_text_from_pdf, extract_text_from_docx


class AnalyzerAgent:
    """
    Agent responsible for analyzing Product Requirement Documents and extracting
    structured information for downstream processing.
    """

    def __init__(self, config_path: str = "configs/config.yaml"):
        """
        Initialize the AnalyzerAgent with configuration.
        
        Args:
            config_path: Path to the configuration file
        """
        # Load configuration
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)
        
        # Initialize OpenAI client
        self.client = openai.OpenAI(api_key=self.config["openai"]["api_key"])
        
        # Load analyzer prompt
        with open(self.config["prompts"]["analyzer"], "r") as f:
            self.prompt_template = f.read()
    
    def extract_document_text(self, document_path: str) -> str:
        """
        Extract text from a document file (PDF or DOCX).
        
        Args:
            document_path: Path to the document
            
        Returns:
            Extracted text content
        """
        if document_path.endswith('.pdf'):
            return extract_text_from_pdf(document_path)
        elif document_path.endswith('.docx'):
            return extract_text_from_docx(document_path)
        else:
            with open(document_path, 'r') as f:
                return f.read()
    
    def analyze_prd(self, document_path: str) -> Dict[str, Any]:
        """
        Analyze a Product Requirements Document and extract structured information.
        
        Args:
            document_path: Path to the PRD document
            
        Returns:
            Dictionary of structured information extracted from the PRD
        """
        # Extract text from document
        document_text = self.extract_document_text(document_path)
        
        # Prepare prompt for LLM
        prompt = self.prompt_template.format(document_text=document_text)
        
        # Call LLM for analysis
        response = self.client.chat.completions.create(
            model=self.config["openai"]["model"],
            messages=[
                {"role": "system", "content": "You are a PRD analysis specialist."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            response_format={"type": "json_object"}
        )
        
        # Extract and parse the response
        analysis_result = json.loads(response.choices[0].message.content)
        
        # Save the result
        output_path = self.config["output_paths"]["structured_output"]
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, "w") as f:
            json.dump(analysis_result, f, indent=2)
        
        return analysis_result 