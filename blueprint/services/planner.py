"""Planner service for matching features to codebase repositories."""

import os
import yaml
from ..helpers.utils import load_json, save_json


class Planner:
    """Planner service for determining architecture and service mapping."""

    def __init__(self, repo_rules_path=None):
        """Initialize the Planner service.
        
        Args:
            repo_rules_path (str, optional): Path to repository rules file. Defaults to None.
        """
        self.repo_rules_path = repo_rules_path
        self.repo_rules = self._load_repo_rules()
    
    def _load_repo_rules(self):
        """Load repository rules from YAML file.
        
        Returns:
            dict: Repository rules mapping
        """
        if not self.repo_rules_path or not os.path.exists(self.repo_rules_path):
            # Return default/empty rules if no path provided
            return {}
            
        try:
            with open(self.repo_rules_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"Error loading repo rules: {e}")
            return {}
    
    def plan(self, extracted_info):
        """Create architecture plan based on extracted information.
        
        Args:
            extracted_info (dict): Information extracted by the Analyzer
            
        Returns:
            dict: Architecture plan with service mappings
        """
        # Map features to existing services based on rules
        service_mappings = self._map_features_to_services(extracted_info["features"])
        
        # Generate architecture plan
        architecture_plan = {
            "services": service_mappings,
            "new_services": self._identify_new_services(extracted_info),
            "modified_services": self._identify_modified_services(extracted_info),
            "tech_stack": self._recommend_tech_stack(extracted_info),
            "architecture_overview": self._generate_architecture_overview(extracted_info)
        }
        
        return architecture_plan
    
    def _map_features_to_services(self, features):
        """Map features to existing services based on repository rules.
        
        Args:
            features (list): List of features to map
            
        Returns:
            dict: Mapping of features to services
        """
        service_mappings = {}
        
        # In a real implementation, this would use the repo_rules to match
        # features to appropriate services/repositories
        for feature in features:
            # Simple placeholder logic - would be more sophisticated in real impl
            matched_services = []
            
            # Check each rule for feature match
            for service, rules in self.repo_rules.get("services", {}).items():
                keywords = rules.get("keywords", [])
                for keyword in keywords:
                    if keyword.lower() in feature.lower():
                        matched_services.append(service)
            
            service_mappings[feature] = matched_services or ["unknown_service"]
            
        return service_mappings
    
    def _identify_new_services(self, extracted_info):
        """Identify potential new services needed based on extracted info.
        
        Args:
            extracted_info (dict): Information extracted by the Analyzer
            
        Returns:
            list: Suggested new services
        """
        # Placeholder logic - in real implementation would analyze features
        # against existing services to identify gaps
        return ["new_service_1"]
    
    def _identify_modified_services(self, extracted_info):
        """Identify existing services that need modification.
        
        Args:
            extracted_info (dict): Information extracted by the Analyzer
            
        Returns:
            dict: Services needing modification with details
        """
        # Placeholder for identifying services that need changes
        return {
            "service_1": {
                "changes": ["Add new endpoint", "Update database schema"],
                "impact": "Medium"
            }
        }
    
    def _recommend_tech_stack(self, extracted_info):
        """Recommend technology stack based on extracted info.
        
        Args:
            extracted_info (dict): Information extracted by the Analyzer
            
        Returns:
            dict: Recommended technology stack
        """
        # Placeholder for tech stack recommendations
        return {
            "frontend": ["React", "TypeScript"],
            "backend": ["Python", "FastAPI"],
            "database": ["PostgreSQL"],
            "infrastructure": ["Kubernetes", "Docker"]
        }
    
    def _generate_architecture_overview(self, extracted_info):
        """Generate high-level architecture overview.
        
        Args:
            extracted_info (dict): Information extracted by the Analyzer
            
        Returns:
            str: Architecture overview description
        """
        # Placeholder for architecture overview
        return "This implementation will follow a microservices architecture with RESTful APIs for communication between services."
    
    def save_output(self, architecture_plan, output_path):
        """Save the architecture plan to the output folder.
        
        Args:
            architecture_plan (dict): The generated architecture plan
            output_path (str): Path to save the output
            
        Returns:
            str: Path to the saved file
        """
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Save as JSON
        save_json(architecture_plan, output_path)
        
        return output_path 