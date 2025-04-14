"""
Tech Spec Generator Agent for creating technical specification documents based
on PRD analysis and architecture plans.
"""
import json
import os
import yaml
from typing import Dict, Any, List, Optional

import openai


class SpecGeneratorAgent:
    """
    Agent responsible for generating comprehensive technical specifications
    based on PRD analysis and architecture plans.
    """

    def __init__(self, config_path: str = "configs/config.yaml"):
        """
        Initialize the SpecGeneratorAgent with configuration.
        
        Args:
            config_path: Path to the configuration file
        """
        # Load configuration
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)
        
        # Initialize OpenAI client
        self.client = openai.OpenAI(api_key=self.config["openai"]["api_key"])
        
        # Load spec generator prompt
        with open(self.config["prompts"]["spec_generator"], "r") as f:
            self.prompt_template = f.read()
        
        # Load spec guidelines
        with open(self.config["guidelines"]["spec_format"], "r") as f:
            self.spec_guidelines = f.read()
    
    def load_analysis_result(self) -> Dict[str, Any]:
        """
        Load the analysis result from the PRD analyzer.
        
        Returns:
            Dictionary of structured information from the PRD analysis
        """
        analysis_path = self.config["output_paths"]["structured_output"]
        with open(analysis_path, "r") as f:
            return json.load(f)
    
    def load_architecture_plan(self) -> str:
        """
        Load the architecture plan from the Planner Agent.
        
        Returns:
            Architecture plan as text
        """
        plan_path = self.config["output_paths"]["architecture_plan"]
        with open(plan_path, "r") as f:
            return f.read()
    
    def generate_tech_spec(self) -> str:
        """
        Generate a comprehensive technical specification document.
        
        Returns:
            Technical specification document as text
        """
        # Load PRD analysis and architecture plan
        analysis_result = self.load_analysis_result()
        architecture_plan = self.load_architecture_plan()
        
        # Prepare prompt for LLM
        prompt = self.prompt_template.format(
            prd_analysis=json.dumps(analysis_result, indent=2),
            architecture_plan=architecture_plan,
            spec_guidelines=self.spec_guidelines
        )
        
        # Call LLM for spec generation
        response = self.client.chat.completions.create(
            model=self.config["openai"]["model"],
            messages=[
                {"role": "system", "content": "You are an expert technical specification writer."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=8000
        )
        
        # Extract the response
        tech_spec = response.choices[0].message.content
        
        # Save the result
        output_path = self.config["output_paths"]["final_spec"]
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, "w") as f:
            f.write(tech_spec)
        
        return tech_spec 