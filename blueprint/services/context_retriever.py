"""Context Retriever service for extracting domain knowledge from repositories."""

import os
import re
import glob
from typing import Dict, List, Any, Optional

class ContextRetriever:
    """Service for retrieving domain context from code repositories."""
    
    def __init__(self, context_base_path=None):
        """Initialize the Context Retriever service.
        
        Args:
            context_base_path (str, optional): Base path for context files. Defaults to None.
        """
        self.context_base_path = context_base_path or os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
            'repo_context'
        )
    
    def retrieve_context(self, features: List[str], keywords: List[str] = None) -> Dict[str, str]:
        """Retrieve relevant domain context based on features and keywords.
        
        Args:
            features (List[str]): List of features from the PRD
            keywords (List[str], optional): Additional keywords to search for. Defaults to None.
            
        Returns:
            Dict[str, str]: Retrieved context categorized by type
        """
        if keywords is None:
            keywords = []
            
        # Extract additional keywords from features
        for feature in features:
            # Extract key terms from feature descriptions
            words = re.findall(r'\b\w+\b', feature.lower())
            # Add words with length > 3 to avoid common words
            keywords.extend([word for word in words if len(word) > 3])
        
        # Remove duplicates and convert to lowercase
        keywords = list(set([k.lower() for k in keywords]))
        
        # Retrieve context by type
        return {
            "services": self._retrieve_services(keywords),
            "database_schema": self._retrieve_database_schema(keywords),
            "apis": self._retrieve_apis(keywords),
            "auth": self._retrieve_auth_info(),
            "infrastructure": self._retrieve_infrastructure_info()
        }
    
    def _retrieve_services(self, keywords: List[str]) -> str:
        """Retrieve information about services relevant to the keywords.
        
        Args:
            keywords (List[str]): Keywords to search for
            
        Returns:
            str: Information about relevant services
        """
        services_path = os.path.join(self.context_base_path, 'services.md')
        if not os.path.exists(services_path):
            return "No service information available."
            
        with open(services_path, 'r', encoding='utf-8') as f:
            services_content = f.read()
            
        # Split content by service sections and filter by keywords
        services_sections = re.split(r'(?=^## )', services_content, flags=re.MULTILINE)
        
        relevant_sections = []
        for section in services_sections:
            if section.strip():
                # Check if any keyword appears in this section
                if any(keyword in section.lower() for keyword in keywords):
                    relevant_sections.append(section)
                    
        # If no relevant sections found, include a general overview
        if not relevant_sections and services_sections:
            # Find any general overview section or return the first section
            for section in services_sections:
                if 'overview' in section.lower() or 'introduction' in section.lower():
                    relevant_sections.append(section)
                    break
            
            # If still empty, add the first section
            if not relevant_sections and services_sections:
                relevant_sections.append(services_sections[0])
        
        return "\n".join(relevant_sections)
    
    def _retrieve_database_schema(self, keywords: List[str]) -> str:
        """Retrieve database schema information relevant to the keywords.
        
        Args:
            keywords (List[str]): Keywords to search for
            
        Returns:
            str: Relevant database schema information
        """
        # Try schema.sql or other schema files in the context directory
        schema_paths = [
            os.path.join(self.context_base_path, 'schema.sql'),
            os.path.join(self.context_base_path, 'database.sql'),
            os.path.join(self.context_base_path, 'db_schema.md')
        ]
        
        schema_content = ""
        for path in schema_paths:
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    schema_content = f.read()
                break
        
        if not schema_content:
            return "No database schema information available."
        
        # For SQL schema, try to extract relevant table definitions
        if path.endswith('.sql'):
            # Find CREATE TABLE statements that contain keywords
            tables = re.findall(r'CREATE TABLE [^;]+;', schema_content, re.IGNORECASE | re.DOTALL)
            
            relevant_tables = []
            for table in tables:
                if any(keyword in table.lower() for keyword in keywords):
                    relevant_tables.append(table)
            
            if relevant_tables:
                return "\n\n".join(relevant_tables)
        
        # For markdown or if no relevant tables found, return full content
        return schema_content
    
    def _retrieve_apis(self, keywords: List[str]) -> str:
        """Retrieve API information relevant to the keywords.
        
        Args:
            keywords (List[str]): Keywords to search for
            
        Returns:
            str: Relevant API information
        """
        api_path = os.path.join(self.context_base_path, 'apis.md')
        if not os.path.exists(api_path):
            return "No API information available."
            
        with open(api_path, 'r', encoding='utf-8') as f:
            apis_content = f.read()
            
        # Split content by API endpoint sections and filter by keywords
        api_sections = re.split(r'(?=^### |^## )', apis_content, flags=re.MULTILINE)
        
        relevant_sections = []
        for section in api_sections:
            if section.strip():
                # Check if any keyword appears in this section
                if any(keyword in section.lower() for keyword in keywords):
                    relevant_sections.append(section)
        
        # If no relevant sections found, return a header and note
        if not relevant_sections:
            return "## APIs\n\nNo relevant API information found."
            
        return "\n".join(relevant_sections)
    
    def _retrieve_auth_info(self) -> str:
        """Retrieve authentication and authorization information.
        
        Returns:
            str: Authentication information
        """
        auth_path = os.path.join(self.context_base_path, 'auth.md')
        if not os.path.exists(auth_path):
            return "No authentication information available."
            
        with open(auth_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def _retrieve_infrastructure_info(self) -> str:
        """Retrieve infrastructure information.
        
        Returns:
            str: Infrastructure information
        """
        infra_path = os.path.join(self.context_base_path, 'infra.md')
        if not os.path.exists(infra_path):
            return "No infrastructure information available."
            
        with open(infra_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def search_repositories(self, keywords: List[str], repos_dir: str) -> Dict[str, List[str]]:
        """Search through repositories for files containing keywords.
        
        Args:
            keywords (List[str]): Keywords to search for
            repos_dir (str): Directory containing repositories
            
        Returns:
            Dict[str, List[str]]: Relevant files grouped by repository
        """
        if not os.path.exists(repos_dir) or not os.path.isdir(repos_dir):
            return {}
            
        results = {}
        
        # Get all repositories (directories) in the repos_dir
        for repo_dir in [d for d in os.listdir(repos_dir) if os.path.isdir(os.path.join(repos_dir, d))]:
            repo_path = os.path.join(repos_dir, repo_dir)
            
            # Find all .py, .js, .ts, .java, .go, .rb files
            code_files = []
            for ext in ['.py', '.js', '.ts', '.java', '.go', '.rb', '.md', '.sql']:
                code_files.extend(glob.glob(f"{repo_path}/**/*{ext}", recursive=True))
            
            # Search through files
            matching_files = []
            for file_path in code_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        rel_path = os.path.relpath(file_path, repos_dir)
                        
                        # Check if any keyword appears in the content
                        if any(keyword in content.lower() for keyword in keywords):
                            matching_files.append(rel_path)
                except (UnicodeDecodeError, IOError):
                    # Skip binary files or files that can't be read
                    continue
            
            if matching_files:
                results[repo_dir] = matching_files
        
        return results 