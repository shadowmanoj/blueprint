"""LLM Service for GPT-4o integration."""

import os
import json
import requests
from typing import Dict, List, Any, Optional

from .context_retriever import ContextRetriever


class LLMService:
    """Service for interacting with OpenAI GPT-4o API."""
    
    def __init__(self, api_key=None, model="gpt-4o", context_base_path=None):
        """Initialize the LLM service.
        
        Args:
            api_key (str, optional): OpenAI API key. Defaults to None.
            model (str, optional): Model to use. Defaults to "gpt-4o".
            context_base_path (str, optional): Base path for context files. Defaults to None.
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
        
        # Initialize context retriever
        self.context_retriever = ContextRetriever(context_base_path)
    
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
            extracted_info = json.loads(response)
            
            # Extract keywords for later context retrieval
            keywords = []
            if "features" in extracted_info:
                keywords.extend(extracted_info["features"])
            if "domain" in extracted_info:
                keywords.append(extracted_info["domain"])
            if "engineering_goals" in extracted_info:
                for goal_type, goals in extracted_info["engineering_goals"].items():
                    keywords.extend(goals)
                    
            # Store keywords in extracted info for later use
            extracted_info["_keywords"] = keywords
            
            return extracted_info
            
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
                "_keywords": [],
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
        # Get features and keywords for context retrieval
        features = extracted_info.get("features", [])
        keywords = extracted_info.get("_keywords", [])
        
        # Retrieve relevant domain context
        domain_context = self.context_retriever.retrieve_context(features, keywords)
        
        system_message = """
You are a senior software architect. Based on the extracted features and repository rules,
determine which existing services should be used, which new services might need to be created,
and create a high-level architecture plan.

Use the domain context provided to make informed decisions about services, APIs, and database schemas.

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
# Extracted Information
{json.dumps(extracted_info, indent=2)}

# Repository Rules
{json.dumps(repo_rules, indent=2)}

# Domain Context

## Services
{domain_context["services"]}

## Database Schema
{domain_context["database_schema"]}

## APIs
{domain_context["apis"]}
"""
        
        try:
            response = self.chat(system_message, user_message)
            # Parse the JSON response
            architecture_plan = json.loads(response)
            # Add domain context references to the architecture plan
            architecture_plan["_domain_context"] = {
                "services_used": True,
                "database_schema_used": True if domain_context["database_schema"] != "No database schema information available." else False,
                "apis_used": True if domain_context["apis"] != "No API information available." else False
            }
            return architecture_plan
            
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
                "_domain_context": {
                    "services_used": False,
                    "database_schema_used": False,
                    "apis_used": False
                },
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
        # Get features and keywords for context retrieval
        features = extracted_info.get("features", [])
        keywords = extracted_info.get("_keywords", [])
        
        # Retrieve domain context if not already included in architecture plan
        domain_context = {}
        if "_domain_context" not in architecture_plan:
            domain_context = self.context_retriever.retrieve_context(features, keywords)
        
        # Get tech spec template
        template_path = os.path.join(os.path.dirname(self.context_retriever.context_base_path), 
                                    'repo_context', 'tech_spec_template.md')
        template = ""
        if os.path.exists(template_path):
            with open(template_path, 'r', encoding='utf-8') as f:
                template = f.read()
        
        system_message = """
You are a senior technical writer experienced in writing detailed technical specifications.
Generate a comprehensive technical specification based on the architecture plan, extracted information,
domain context, and specification guidelines.

Follow the template structure closely, filling in all relevant sections with detailed information.
Use the domain context to ensure the specification aligns with existing systems and practices.

Your response should be in Markdown format and should be ready to be used as an implementation guide by developers.
"""
        
        user_message = f"""
# Architecture Plan
{json.dumps(architecture_plan, indent=2)}

# Extracted Information
{json.dumps(extracted_info, indent=2)}

# Domain Context
## Services
{domain_context.get("services", architecture_plan.get("_domain_context", {}).get("services", ""))}

## Database Schema
{domain_context.get("database_schema", architecture_plan.get("_domain_context", {}).get("database_schema", ""))}

## APIs
{domain_context.get("apis", architecture_plan.get("_domain_context", {}).get("apis", ""))}

## Authentication
{domain_context.get("auth", "")}

## Infrastructure
{domain_context.get("infrastructure", "")}

# Specification Guidelines
{guidelines}

# Template
{template}
"""
        
        return self.chat(system_message, user_message, temperature=0.3)
    
    def generate_code_examples(self, tech_spec: str, context: Dict[str, Any] = None) -> Dict[str, str]:
        """Generate code examples based on the technical specification.
        
        Args:
            tech_spec (str): The technical specification
            context (Dict[str, Any], optional): Additional context. Defaults to None.
            
        Returns:
            Dict[str, str]: Generated code examples by category
        """
        # Prepare context for code generation
        if context is None:
            context = {}
        
        system_message = """
You are a senior software engineer with expertise in multiple programming languages and frameworks.
Generate code examples for the key components described in the technical specification.

Focus on producing practical, realistic code that follows best practices for each language/framework.
Include necessary imports, proper error handling, and comments explaining key parts of the code.

Provide examples for:
1. API endpoints (e.g., in Python/FastAPI, Node.js/Express, etc.)
2. Database models or migrations
3. Frontend components (if applicable)
4. Infrastructure as code (if applicable)

Each code example should be production-ready and consistent with the tech stack mentioned in the spec.
"""
        
        user_message = f"""
# Technical Specification
{tech_spec}

# Additional Context
{json.dumps(context, indent=2) if context else "No additional context provided."}
"""
        
        response = self.chat(system_message, user_message, temperature=0.2)
        
        # Parse the response into categories
        # This is a simplified approach - in practice you'd need a more robust parser
        code_examples = {}
        current_category = None
        current_code = []
        
        for line in response.split("\n"):
            if line.startswith("## "):
                # Save previous category if exists
                if current_category and current_code:
                    code_examples[current_category] = "\n".join(current_code)
                    current_code = []
                current_category = line.lstrip("## ").strip()
            elif line.startswith("```") and current_category:
                if current_code and current_code[-1].startswith("```"):
                    # End of code block
                    current_code.append(line)
                    code_examples[current_category] = "\n".join(current_code)
                    current_code = []
                else:
                    # Start of code block
                    current_code.append(line)
            elif current_category and current_code:
                current_code.append(line)
        
        # Save last category if exists
        if current_category and current_code:
            code_examples[current_category] = "\n".join(current_code)
        
        return code_examples 