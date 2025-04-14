# Blueprint Technical Specification Generator with Domain Context

This tool automatically generates detailed technical specifications from Product Requirement Documents (PRDs) by leveraging domain context from your codebase.

## Overview

Traditional LLM-based tech spec generation often produces generic specifications that lack awareness of your existing systems and architecture. This tool solves this problem by:

1. Extracting key information from PRDs
2. Retrieving relevant context from your domain knowledge base
3. Generating technical specifications that are aligned with your existing systems

## Key Features

- **Domain-Aware Specifications**: Generated specs take into account your existing services, APIs, and database schemas
- **Customizable Templates**: Use your own tech spec templates to ensure consistency
- **Code Example Generation**: Automatically generate sample code snippets for key components
- **Multiple Output Formats**: Generate specs in Markdown and HTML formats
- **LLM-Powered**: Uses GPT-4o for high-quality, contextually relevant specs

## Getting Started

### Prerequisites

- Python 3.8+
- OpenAI API key (for LLM-enhanced functionality)
- Domain context files (see below)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/blueprint.git
cd blueprint
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set your OpenAI API key:
```bash
export OPENAI_API_KEY="your-api-key-here"
```

### Setting up Domain Context

The domain context should be placed in the `repo_context` directory. Create the following files:

1. **services.md**: Information about your microservices
2. **schema.sql**: Database schemas
3. **apis.md**: API documentation
4. **auth.md**: Authentication/authorization information
5. **infra.md**: Infrastructure details
6. **tech_spec_template.md**: Your preferred tech spec template

Example structure:
```
blueprint/
└── repo_context/
    ├── services.md
    ├── schema.sql
    ├── apis.md
    ├── auth.md
    ├── infra.md
    └── tech_spec_template.md
```

See the included examples in the `repo_context` directory for reference.

## Usage

### Basic Usage

Process a single PRD file:

```bash
python tech_spec_pipeline.py --input input/your_prd.md
```

Process all PRD files in the input directory:

```bash
python tech_spec_pipeline.py
```

### Advanced Options

Generate HTML output in addition to Markdown:

```bash
python tech_spec_pipeline.py --html
```

Generate code examples:

```bash
python tech_spec_pipeline.py --code-examples
```

Use a specific repository context directory:

```bash
python tech_spec_pipeline.py --repo-context /path/to/your/context
```

Specify a custom configuration file:

```bash
python tech_spec_pipeline.py --config /path/to/config.yaml
```

### Configuration

You can customize the tool's behavior by editing the `config.yaml` file or providing your own configuration file.

Key configuration options:
- `use_domain_context`: Enable/disable domain context-aware generation
- `generate_code_examples`: Enable/disable code example generation
- `openai_model`: Specify which OpenAI model to use
- `repositories_path`: Path to actual code repositories for dynamic context extraction (advanced)

## How It Works

### Pipeline Architecture

```
┌────────────┐
│   PRD.txt  │ ← User Input
└────┬───────┘
     │
     ▼
┌────────────────────┐
│  PRD Understanding  │ ← GPT-4o extracts features & requirements
└────────┬───────────┘
     │
     ▼
┌────────────────────────────┐
│ Domain Context Retriever    │ ← Pulls relevant context from repo_context
└────────┬───────────────────┘
     │
     ▼
┌────────────────────────────┐
│ Architecture Planning       │ ← Plans architecture based on PRD + context
└────────┬───────────────────┘
     │
     ▼
┌────────────────────────────┐
│ Tech Spec Generation        │ ← Generates the final technical spec
└────────┬───────────────────┘
     │
     ▼
┌────────────────────┐
│  Technical Spec     │ ← Final output in Markdown/HTML
└────────────────────┘
```

### Domain Context Retrieval

The system uses keyword extraction to identify the most relevant parts of your domain context:

1. The analyzer extracts features and keywords from the PRD
2. These keywords are used to search through your context files
3. Relevant sections are retrieved and provided to the LLM
4. The LLM generates specifications informed by this context

## Extending the Tool

### Adding New Context Types

To add a new type of context:

1. Create a new file in the `repo_context` directory
2. Update the `ContextRetriever` class in `services/context_retriever.py`
3. Update the `LLMService` class to include the new context in its prompts

### Customizing Templates

To customize the tech spec template:

1. Edit `repo_context/tech_spec_template.md`
2. The system will automatically use your template for generating specs

### Dynamic Repository Search

For advanced usage, you can enable dynamic repository search:

1. Set `search_repositories: true` in config.yaml
2. Set `repositories_path` to the directory containing your repositories
3. The system will search through actual code instead of static context files

## Troubleshooting

### Common Issues

**Issue**: No OpenAI API key found
**Solution**: Set the OPENAI_API_KEY environment variable or add it to config.yaml

**Issue**: Domain context not being incorporated
**Solution**: Check that your repo_context files contain relevant information and follow the proper format

**Issue**: Generated specs are too generic
**Solution**: Add more detailed context in your repo_context files and consider using a more detailed template

## License

[MIT License](LICENSE)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. 