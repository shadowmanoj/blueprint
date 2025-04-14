"""Core functionality for the Blueprint package."""


class Blueprint:
    """Main class for the Blueprint package."""

    def __init__(self, name):
        """Initialize Blueprint with a name.
        
        Args:
            name (str): Name of the blueprint
        """
        self.name = name
    
    def run(self):
        """Run the blueprint process."""
        return f"Running blueprint: {self.name}"


def create_blueprint(name):
    """Factory function to create a new Blueprint instance.
    
    Args:
        name (str): Name for the new blueprint
        
    Returns:
        Blueprint: A new Blueprint instance
    """
    return Blueprint(name) 