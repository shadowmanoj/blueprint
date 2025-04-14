"""Input parsers for Blueprint."""


class BaseParser:
    """Base class for all input parsers."""
    
    def __init__(self):
        """Initialize the base parser."""
        pass
    
    def parse(self, data):
        """Parse input data.
        
        Args:
            data: Data to parse
            
        Returns:
            dict: Parsed data
        """
        raise NotImplementedError("Subclasses must implement parse method")


class TextParser(BaseParser):
    """Parser for text input."""
    
    def parse(self, text):
        """Parse text input.
        
        Args:
            text (str): Text to parse
            
        Returns:
            dict: Parsed text data
        """
        if not text:
            return {"content": "", "metadata": {}}
            
        return {
            "content": text,
            "metadata": {
                "length": len(text),
                "word_count": len(text.split())
            }
        }


class JSONParser(BaseParser):
    """Parser for JSON input."""
    
    def parse(self, json_data):
        """Parse JSON input.
        
        Args:
            json_data (dict): JSON data to parse
            
        Returns:
            dict: Processed JSON data
        """
        if not json_data:
            return {"data": {}, "metadata": {}}
            
        return {
            "data": json_data,
            "metadata": {
                "keys": list(json_data.keys())
            }
        } 