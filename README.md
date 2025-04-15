# Blueprint

Blueprint is an AI-powered technical specification generator that automatically transforms Product Requirements Documents (PRDs) into detailed technical specifications.

## Features

- PDF text extraction
- AI-powered PRD analysis
- Architecture planning
- Technical specification generation
- Technical specification review

## Requirements

- Python 3.6+
- Required packages (automatically installed):
  - PyMuPDF (fitz)
  - markdown

## Installation

No installation required beyond cloning the repository:

```bash
git clone <repository-url>
cd blueprint
```

## Usage

Blueprint provides two main workflows: Generate and Review.

### Generate Workflow

This workflow extracts text from a PRD, analyzes it, loads repository context, plans architecture, and generates a technical specification.

```bash
# Generate a specification using default paths
python blueprint.py generate

# Generate with a custom PRD file
python blueprint.py generate --input path/to/your/prd.pdf

# Generate with custom repository context
python blueprint.py generate --repo path/to/your/repo

# Generate with custom guidelines
python blueprint.py generate --input path/to/prd.pdf --guidelines path/to/guidelines.md

# Show help for generate command
python blueprint.py generate --help
```

### Review Workflow

This workflow analyzes an existing technical specification, extracts structured information, and generates an enhanced review.

```bash
# Review the most recently generated specification
python blueprint.py review

# Review a specific specification file
python blueprint.py review --spec path/to/your/spec.md

# Show help for review command
python blueprint.py review --help
```

### General Help

```bash
# Show general help information
python blueprint.py --help
```

## Output Files

All output files are saved to the `outputs` directory:

- `structured_output.json` - Structured information extracted from the PRD
- `architecture_plan.md` - High-level architecture plan
- `final_spec.md` - Generated technical specification
- `final_spec.html` - HTML version of the technical specification
- `tech_spec_review_structured.json` - Structured information from review
- `tech_spec_review_architecture_plan.md` - Review architecture plan
- `review_spec.md` - Generated specification review
- `review_spec.html` - HTML version of the specification review

## Directory Structure

- `input_docs/` - Contains input PRD files (default: `dcc_prd.pdf`)
- `repo/` - Contains repository context for architecture planning
- `guidelines/` - Contains specification guidelines
- `outputs/` - Contains all generated files

## License

[Specify license information here] 