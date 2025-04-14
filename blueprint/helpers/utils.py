"""Utility functions for Blueprint."""

import json
import os
from datetime import datetime


def load_json(file_path):
    """Load JSON data from a file.
    
    Args:
        file_path (str): Path to the JSON file
        
    Returns:
        dict: Loaded JSON data
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json(data, file_path):
    """Save data to a JSON file.
    
    Args:
        data (dict): Data to save
        file_path (str): Path to save the JSON file
    """
    directory = os.path.dirname(file_path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)
        
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)


def get_timestamp():
    """Get current timestamp as string.
    
    Returns:
        str: Current timestamp in ISO format
    """
    return datetime.now().isoformat()


def sanitize_input(text):
    """Sanitize input text for safe processing.
    
    Args:
        text (str): Text to sanitize
        
    Returns:
        str: Sanitized text
    """
    if not text:
        return ""
    # Implement sanitization logic
    return text.strip() 