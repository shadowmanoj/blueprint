# Blueprint Technical Specification Generator

A multi-agent system for automatically generating technical specifications from product requirement documents (PRDs).

## Overview

This system processes PRD documents through a three-step pipeline:

1. **Input Analyzer Agent**: Extracts domain/business context, features, and engineering goals from input documents
2. **Codebase-Aware Planner Agent**: Maps features to existing services and suggests architecture changes
3. **Tech Spec Generator Agent**: Produces a complete technical specification following organization guidelines

## Directory Structure

```
blueprint/
├── input/                  # Input PRD documents (PDF, DOCX, MD)
├── output/                 # Generated technical specifications and analysis results
├── context/                # Context files for customization
│   ├── guidelines.md       # Technical specification guidelines
│   └── repo_rules.yaml     # Repository rules for service mapping
├── services/               # Core service components
├── helpers/                # Utility functions
├── nlp/                    # NLP processing components (optional)
├── tech_spec_pipeline.py   # Main pipeline script
├── config.yaml             # Configuration file
└── README.md               # This file
```

## Installation

1. Clone the repository
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. (Optional) Set your OpenAI API key in the environment:

```bash
export OPENAI_API_KEY="your-api-key-here"
```

## Usage

### Basic Usage

Process all documents in the input directory:

```bash
python tech_spec_pipeline.py
```

Process a specific document:

```bash
python tech_spec_pipeline.py --input input/sample_prd.md
```

### Advanced Usage

Specify custom input and output paths:

```bash
python tech_spec_pipeline.py --input /path/to/prd.pdf --output /path/to/output/spec
```

Use a custom configuration file:

```bash
python tech_spec_pipeline.py --config /path/to/config.yaml
```

Generate HTML output in addition to Markdown:

```bash
python tech_spec_pipeline.py --html
```

## Customization

### Repository Rules

Edit `context/repo_rules.yaml` to customize how features are mapped to services in your organization.

### Specification Guidelines

Edit `context/guidelines.md` to define the structure and content requirements for technical specifications.

## LLM Integration

The system supports two modes of operation:

1. **Template-based**: Uses rule-based extraction and templating (no API key required)
2. **LLM-enhanced**: Uses GPT-4o for advanced analysis and generation (requires API key)

## License

[MIT License](LICENSE)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. 