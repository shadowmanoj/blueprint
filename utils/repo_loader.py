"""
Utilities for loading and extracting context from code repositories.
"""
import os
import glob
from typing import Dict, List, Set, Optional, Any


def load_repository_context(repo_path: str, max_files: int = 50) -> str:
    """
    Load and extract context from a code repository.
    
    Args:
        repo_path: Path to the repository directory
        max_files: Maximum number of files to include in the context
        
    Returns:
        Repository context as text
    """
    if not os.path.exists(repo_path):
        return f"Repository path {repo_path} does not exist."
    
    # Define important file patterns to prioritize
    priority_patterns = [
        "README.md",
        "ARCHITECTURE.md",
        "DESIGN.md",
        "**/*.md",
        "**/package.json",
        "**/requirements.txt",
        "**/*.gradle",
        "**/pom.xml",
        "**/build.gradle",
        "**/*.json",
        "**/Dockerfile",
        "**/docker-compose.yml",
        "**/*.yaml",
        "**/*.yml",
        "**/*.proto",
        "**/main.*",
        "**/app.*",
        "**/index.*",
        "**/server.*",
        "**/client.*",
        "**/models/",
        "**/controllers/",
        "**/services/",
        "**/api/",
        "**/core/",
        "**/config/"
    ]
    
    # Collect important files first
    important_files = []
    for pattern in priority_patterns:
        matching_files = glob.glob(os.path.join(repo_path, pattern), recursive=True)
        for file_path in matching_files:
            if os.path.isfile(file_path) and file_path not in important_files:
                important_files.append(file_path)
    
    # Get all remaining files
    all_files = []
    for root, _, files in os.walk(repo_path):
        for file in files:
            file_path = os.path.join(root, file)
            if file_path not in important_files:
                all_files.append(file_path)
    
    # Combine files, prioritizing important ones
    selected_files = important_files + all_files
    
    # Limit to max_files
    selected_files = selected_files[:max_files]
    
    # Generate context
    context_builder = []
    
    # Add repository overview
    context_builder.append(f"# Repository: {os.path.basename(repo_path)}\n")
    
    # Find and add README content
    readme_path = os.path.join(repo_path, "README.md")
    if os.path.exists(readme_path):
        try:
            with open(readme_path, 'r', encoding='utf-8', errors='ignore') as f:
                readme_content = f.read()
                context_builder.append("## README\n")
                context_builder.append(readme_content + "\n\n")
        except Exception as e:
            context_builder.append(f"Error reading README: {e}\n\n")
    
    # Add file structure overview
    context_builder.append("## File Structure\n")
    for file_path in selected_files:
        rel_path = os.path.relpath(file_path, repo_path)
        context_builder.append(f"- {rel_path}\n")
    
    # Add file contents for important files
    context_builder.append("\n## Key Files Content\n")
    
    # Binary file extensions to skip
    binary_extensions = {'.exe', '.bin', '.jar', '.war', '.ear', '.zip', '.tar', '.gz', 
                         '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.ico', '.svg', 
                         '.pdf', '.doc', '.docx', '.ppt', '.pptx', '.xls', '.xlsx'}
    
    # Size limit for file content (100KB)
    size_limit = 100 * 1024
    
    for file_path in selected_files[:20]:  # Only include first 20 files content
        rel_path = os.path.relpath(file_path, repo_path)
        ext = os.path.splitext(file_path)[1].lower()
        
        # Skip binary files and large files
        if ext in binary_extensions or os.path.getsize(file_path) > size_limit:
            continue
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                context_builder.append(f"\n### {rel_path}\n")
                context_builder.append("```\n")
                
                # Limit content to 500 lines
                lines = content.split('\n')
                if len(lines) > 500:
                    content = '\n'.join(lines[:250] + ["...(truncated)..."] + lines[-250:])
                
                context_builder.append(content)
                context_builder.append("\n```\n")
        except Exception as e:
            context_builder.append(f"Error reading file: {e}\n")
    
    return ''.join(context_builder) 