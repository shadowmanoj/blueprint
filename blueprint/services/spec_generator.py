"""Tech Spec Generator service for creating technical specifications."""

import os
import markdown


class SpecGenerator:
    """Generator service for creating technical specifications."""

    def __init__(self, guidelines_path=None):
        """Initialize the SpecGenerator service.
        
        Args:
            guidelines_path (str, optional): Path to spec writing guidelines. Defaults to None.
        """
        self.guidelines_path = guidelines_path
        self.guidelines = self._load_guidelines()
    
    def _load_guidelines(self):
        """Load specification writing guidelines.
        
        Returns:
            str: Guidelines content
        """
        if not self.guidelines_path or not os.path.exists(self.guidelines_path):
            # Return default guidelines if no path provided
            return """# Default Technical Specification Guidelines
            
1. Include an executive summary at the top
2. List all impacted services
3. Provide sequence diagrams for key flows
4. Include API specifications
5. Discuss storage requirements
6. Address security considerations
7. Include rollout and testing plan
"""
            
        try:
            with open(self.guidelines_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error loading guidelines: {e}")
            return ""
    
    def generate_spec(self, architecture_plan, extracted_info=None):
        """Generate a technical specification based on the architecture plan.
        
        Args:
            architecture_plan (dict): Architecture plan from the Planner
            extracted_info (dict, optional): Original extracted info. Defaults to None.
            
        Returns:
            str: Generated technical specification in Markdown format
        """
        # In a real implementation, this would use an LLM to generate the spec
        # based on the architecture plan and guidelines
        
        # For this placeholder implementation, we'll create a basic spec template
        spec = self._generate_spec_template(architecture_plan, extracted_info)
        
        return spec
    
    def _generate_spec_template(self, architecture_plan, extracted_info=None):
        """Generate a basic technical specification template.
        
        Args:
            architecture_plan (dict): Architecture plan
            extracted_info (dict, optional): Original extracted info. Defaults to None.
            
        Returns:
            str: Specification template in Markdown
        """
        domain = extracted_info.get("domain", "Unspecified Domain") if extracted_info else "Unspecified Domain"
        features = extracted_info.get("features", []) if extracted_info else []
        services = architecture_plan.get("services", {})
        new_services = architecture_plan.get("new_services", [])
        modified_services = architecture_plan.get("modified_services", {})
        tech_stack = architecture_plan.get("tech_stack", {})
        overview = architecture_plan.get("architecture_overview", "")
        
        # Build the specification in Markdown format
        spec = f"""# Technical Specification: {domain}

## 1. Executive Summary

{overview}

## 2. Features

The following features will be implemented:

"""
        
        # Add features
        for feature in features:
            spec += f"- {feature}\n"
            mapped_services = services.get(feature, [])
            if mapped_services:
                spec += f"  - Services: {', '.join(mapped_services)}\n"
        
        spec += f"""
## 3. Architecture

### 3.1 Service Architecture

"""
        
        # Add existing services
        if services:
            spec += "#### Existing Services\n\n"
            for feature, service_list in services.items():
                for service in service_list:
                    spec += f"- {service} (for {feature})\n"
        
        # Add new services
        if new_services:
            spec += "\n#### New Services\n\n"
            for service in new_services:
                spec += f"- {service}\n"
        
        # Add modified services
        if modified_services:
            spec += "\n#### Modified Services\n\n"
            for service, details in modified_services.items():
                spec += f"- {service}\n"
                if "changes" in details:
                    spec += "  - Changes:\n"
                    for change in details["changes"]:
                        spec += f"    - {change}\n"
                if "impact" in details:
                    spec += f"  - Impact: {details['impact']}\n"
        
        # Add tech stack
        spec += "\n### 3.2 Technology Stack\n\n"
        for category, technologies in tech_stack.items():
            spec += f"- {category.capitalize()}: {', '.join(technologies)}\n"
        
        # Add additional sections based on guidelines
        spec += """
## 4. API Specifications

[API specifications will be detailed here]

## 5. Data Model

[Data model will be detailed here]

## 6. Security Considerations

[Security considerations will be detailed here]

## 7. Testing Strategy

[Testing strategy will be detailed here]

## 8. Deployment Plan

[Deployment plan will be detailed here]

## 9. Monitoring and Observability

[Monitoring and observability details will be provided here]

"""
        
        return spec
    
    def save_output(self, spec, output_path, format="md"):
        """Save the technical specification to the output folder.
        
        Args:
            spec (str): The generated specification in Markdown
            output_path (str): Path to save the output
            format (str, optional): Output format ('md' or 'html'). Defaults to "md".
            
        Returns:
            str: Path to the saved file
        """
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Save as Markdown
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(spec)
        
        # Optionally convert to HTML
        if format.lower() == "html":
            html_output_path = output_path.replace(".md", ".html")
            html_content = markdown.markdown(spec)
            with open(html_output_path, 'w', encoding='utf-8') as f:
                f.write(f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Technical Specification</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
        h1 {{ color: #333; }}
        h2 {{ color: #444; border-bottom: 1px solid #ddd; padding-bottom: 5px; }}
        h3 {{ color: #555; }}
        pre {{ background: #f4f4f4; padding: 10px; border-radius: 5px; }}
        code {{ background: #f4f4f4; padding: 2px 5px; }}
    </style>
</head>
<body>
{html_content}
</body>
</html>""")
            return html_output_path
        
        return output_path 