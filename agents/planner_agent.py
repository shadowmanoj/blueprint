"""
Codebase-Aware Planner Agent for generating architecture plans based on PRD analysis
and existing repository context.
"""
import json
import os
import yaml
from typing import Dict, Any, List, Optional

import openai

from utils.repo_loader import load_repository_context


class PlannerAgent:
    """
    Agent responsible for generating architecture plans based on PRD analysis
    and existing repository context.
    """

    def __init__(self, config_path: str = "configs/config.yaml"):
        """
        Initialize the PlannerAgent with configuration.
        
        Args:
            config_path: Path to the configuration file
        """
        # Load configuration
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)
        
        # Initialize OpenAI client
        self.client = openai.OpenAI(api_key=self.config["openai"]["api_key"])
        
        # Load planner prompt
        with open(self.config["prompts"]["planner"], "r") as f:
            self.prompt_template = f.read()
    
    def load_analysis_result(self) -> Dict[str, Any]:
        """
        Load the analysis result from the PRD analyzer.
        
        Returns:
            Dictionary of structured information from the PRD analysis
        """
        analysis_path = self.config["output_paths"]["structured_output"]
        with open(analysis_path, "r") as f:
            return json.load(f)
    
    def generate_architecture_plan(self) -> str:
        """
        Generate architecture plan based on PRD analysis and repository context.
        
        Returns:
            Architecture plan document as text
        """
        # Load PRD analysis
        analysis_result = self.load_analysis_result()
        
        # Load repository contexts
        repo_contexts = {}
        for service, repo_path in self.config["repo_contexts"].items():
            repo_contexts[service] = load_repository_context(repo_path)
        
        # Combine contexts
        combined_contexts = "\n\n===== REPOSITORY CONTEXTS =====\n\n"
        for service, context in repo_contexts.items():
            combined_contexts += f"# {service}\n{context}\n\n"
        
        # Prepare prompt for LLM
        prompt = self.prompt_template.format(
            prd_analysis=json.dumps(analysis_result, indent=2),
            repo_contexts=combined_contexts
        )
        
        # Call LLM for planning
        response = self.client.chat.completions.create(
            model=self.config["openai"]["model"],
            messages=[
                {"role": "system", "content": "You are an expert architecture planner."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=4000
        )
        
        # Extract the response
        architecture_plan = response.choices[0].message.content
        
        # Save the result
        output_path = self.config["output_paths"]["architecture_plan"]
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, "w") as f:
            f.write(architecture_plan)
        
        return architecture_plan 