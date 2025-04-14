"""LLM Service for GPT-4o integration."""

import os
import json
import requests
from typing import Dict, List, Any, Optional


class LLMService:
    """Service for interacting with OpenAI GPT-4o API."""
    
    def __init__(self, api_key=None, model="gpt-4o"):
        """Initialize the LLM service.
        
        Args:
            api_key (str, optional): OpenAI API key. Defaults to None.
            model (str, optional): Model to use. Defaults to "gpt-4o".
        """
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Provide it directly or set OPENAI_API_KEY environment variable.")
        
        self.model = model
        self.api_url = "https://api.openai.com/v1/chat/completions"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
    
    def chat(self, 
             system_message: str, 
             user_message: str, 
             temperature: float = 0.4, 
             max_tokens: Optional[int] = None) -> str:
        """Call OpenAI API with system and user messages.
        
        Args:
            system_message (str): System message
            user_message (str): User message
            temperature (float, optional): Temperature parameter. Defaults to 0.4.
            max_tokens (int, optional): Maximum tokens in response. Defaults to None.
            
        Returns:
            str: Model response
        """
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ]
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature
        }
        
        if max_tokens:
            payload["max_tokens"] = max_tokens
        
        try:
            response = requests.post(self.api_url, headers=self.headers, json=payload)
            response.raise_for_status()
            
            response_data = response.json()
            return response_data["choices"][0]["message"]["content"]
        
        except requests.exceptions.RequestException as e:
            error_message = f"Error calling OpenAI API: {str(e)}"
            try:
                error_data = response.json()
                if "error" in error_data:
                    error_message += f" - {error_data['error']['message']}"
            except:
                pass
            
            raise Exception(error_message)
    
    def analyze_document(self, document_text: str) -> Dict[str, Any]:
        """Analyze document text using GPT-4o to extract structured information.
        
        Args:
            document_text (str): Document text to analyze
            
        Returns:
            Dict[str, Any]: Structured extraction results
        """
        system_message = """
You are an expert analyzer that extracts structured information from product requirements documents.
Extract the following information:
1. Domain/business context
2. Features being implemented
3. Engineering goals (APIs, workflows, storage, integrations)

Provide your response as a JSON object with the following structure:
{
    "domain": "Brief description of the domain/business context",
    "features": ["Feature 1", "Feature 2", ...],
    "engineering_goals": {
        "apis": ["API 1", "API 2", ...],
        "workflows": ["Workflow 1", ...],
        "storage": ["Storage requirement 1", ...],
        "integrations": ["Integration 1", ...]
    }
}
"""
        
        user_message = f"Here is the document to analyze:\n\n{document_text}"
        
        try:
            response = self.chat(system_message, user_message)
            # Parse the JSON response
            return json.loads(response)
        except json.JSONDecodeError:
            # If response isn't valid JSON, create a structured response anyway
            return {
                "domain": "Error: Could not extract domain",
                "features": ["Error: Could not extract features"],
                "engineering_goals": {
                    "apis": [],
                    "workflows": [],
                    "storage": [],
                    "integrations": []
                },
                "error": "Failed to parse LLM response as JSON"
            }
    
    def plan_architecture(self, extracted_info: Dict[str, Any], repo_rules: Dict[str, Any]) -> Dict[str, Any]:
        """Plan architecture based on extracted info and repository rules.
        
        Args:
            extracted_info (Dict[str, Any]): Information extracted from document
            repo_rules (Dict[str, Any]): Repository mapping rules
            
        Returns:
            Dict[str, Any]: Architecture plan
        """
        system_message = """
You are a senior software architect. Based on the extracted features and repository rules,
determine which existing services should be used, which new services might need to be created,
and create a high-level architecture plan.

Provide your response as a JSON object with the following structure:
{
    "services": {
        "Feature 1": ["service_a", "service_b"],
        "Feature 2": ["service_c"]
    },
    "new_services": ["new_service_1", "new_service_2"],
    "modified_services": {
        "service_a": {
            "changes": ["Change 1", "Change 2"],
            "impact": "High/Medium/Low"
        }
    },
    "tech_stack": {
        "frontend": ["Tech 1", "Tech 2"],
        "backend": ["Tech 3", "Tech 4"],
        "database": ["Tech 5"],
        "infrastructure": ["Tech 6", "Tech 7"]
    },
    "architecture_overview": "Brief description of the overall architecture"
}
"""
        
        user_message = f"""
Extracted Information:
{json.dumps(extracted_info, indent=2)}

Repository Rules:
{json.dumps(repo_rules, indent=2)}
"""
        
        try:
            response = self.chat(system_message, user_message)
            # Parse the JSON response
            return json.loads(response)
        except json.JSONDecodeError:
            # If response isn't valid JSON, create a structured response anyway
            return {
                "services": {},
                "new_services": [],
                "modified_services": {},
                "tech_stack": {
                    "frontend": [],
                    "backend": [],
                    "database": [],
                    "infrastructure": []
                },
                "architecture_overview": "Error: Could not generate architecture overview",
                "error": "Failed to parse LLM response as JSON"
            }
    
    def generate_tech_spec(self, architecture_plan: Dict[str, Any], extracted_info: Dict[str, Any], guidelines: str) -> str:
        """Generate a technical specification based on the architecture plan and guidelines.
        
        Args:
            architecture_plan (Dict[str, Any]): Architecture plan
            extracted_info (Dict[str, Any]): Information extracted from document
            guidelines (str): Specification writing guidelines
            
        Returns:
            str: Technical specification in Markdown format
        """
        system_message = """
You are a senior technical writer. Generate a comprehensive technical specification 
based on the architecture plan, extracted information, and specification guidelines.
Your response should be in Markdown format and follow the provided guidelines.
"""
        
        user_message = f"""
Architecture Plan:
{json.dumps(architecture_plan, indent=2)}

Extracted Information:
{json.dumps(extracted_info, indent=2)}

Specification Guidelines:
{guidelines}
"""
        
        return self.chat(system_message, user_message) 