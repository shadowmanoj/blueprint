# Blueprint: Technical Documentation Generator

Blueprint is an AI-powered tool that automatically generates technical specifications and documentation from product requirements. It analyzes input documents, extracts key information, and creates structured technical specifications in Markdown format.

## Features

- **Document Analysis**: Extracts structured information from PRD (Product Requirements Document) files
- **Architecture Planning**: Generates a high-level architecture design based on extracted requirements
- **Technical Specification Generation**: Creates comprehensive technical specifications in both Markdown and HTML formats
- **Repository Context Integration**: Incorporates existing codebase information to create relevant and aligned specifications

## Installation

1. Clone this repository:
   ```
   git clone <repository-url>
   cd blueprint
   ```

2. Create and activate a virtual environment (recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Place your Product Requirements Document (PDF) in the `input_docs/` directory.
2. Place your repository documentation in the `repo/` directory.
3. Create your specification guidelines in `guidelines/spec_guidelines.md`.
4. Run the main script:
   ```
   python __main__.py
   ```
5. The generated outputs will be available in the `outputs/` directory:
   - `structured_output.json`: Extracted information from the PRD
   - `architecture_plan.md`: High-level architecture plan
   - `final_spec.md`: Complete technical specification in Markdown format
   - `final_spec.html`: Technical specification in HTML format (for better rendering)

## Configuration

Edit the following variables in `__main__.py` to customize the tool:

```python
# CONFIG
INPUT_PATH = "input_docs/dcc_prd.pdf"  # Path to your input PRD
REPO_PATH = "repo"                    # Path to your repo documentation
GUIDELINE_PATH = "guidelines/spec_guidelines.md"  # Path to spec guidelines
OUTPUT_FOLDER = "outputs"             # Directory for output files
```

## Dependencies

- openai: For AI-powered text generation
- langchain: For document processing
- pymupdf: For PDF text extraction
- python-dotenv: For environment variable management
- markdown: For converting Markdown to HTML

## Troubleshooting

### Unicode Errors
If you encounter Unicode errors when processing documents, ensure your input files are UTF-8 encoded.

### Missing Dependencies
Run `python check_imports.py` to verify all dependencies are correctly installed.

### Browser Not Opening
If the browser doesn't open automatically, manually navigate to the output files in the `outputs/` directory.

## License

[Your License Information]

## Contributing

[Your Contributing Guidelines] 