"""Output formatters for Blueprint."""

import json


class BaseFormatter:
    """Base class for output formatters."""
    
    def format(self, data):
        """Format the data for output.
        
        Args:
            data: Data to format
            
        Returns:
            Formatted output
        """
        raise NotImplementedError("Subclasses must implement format method")


class JSONFormatter(BaseFormatter):
    """Formatter for JSON output."""
    
    def __init__(self, indent=2):
        """Initialize JSON formatter.
        
        Args:
            indent (int, optional): JSON indentation. Defaults to 2.
        """
        self.indent = indent
    
    def format(self, data):
        """Format data as JSON.
        
        Args:
            data (dict): Data to format
            
        Returns:
            str: JSON formatted string
        """
        return json.dumps(data, indent=self.indent)


class TextFormatter(BaseFormatter):
    """Formatter for text output."""
    
    def __init__(self, template=None):
        """Initialize text formatter.
        
        Args:
            template (str, optional): Text template. Defaults to None.
        """
        self.template = template
    
    def format(self, data):
        """Format data as text.
        
        Args:
            data (dict): Data to format
            
        Returns:
            str: Formatted text
        """
        if self.template:
            # Simple template formatting
            result = self.template
            for key, value in data.items():
                placeholder = f"{{{key}}}"
                result = result.replace(placeholder, str(value))
            return result
        
        # Basic formatting
        if isinstance(data, dict):
            return "\n".join(f"{k}: {v}" for k, v in data.items())
        return str(data) 