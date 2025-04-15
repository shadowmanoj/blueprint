# Blueprint

Blueprint is an AI-powered technical specification generator that transforms Product Requirements Documents (PRDs) into implementation-ready technical specifications with code-level detail.

## Features

- PDF text extraction from PRDs
- AI-powered comprehensive PRD analysis
- Detailed architecture planning with service mappings
- **Production-ready technical specifications with actual code examples**:
  - Complete function/method definitions with signatures
  - Actual database schemas with SQL DDL statements
  - Comprehensive API contracts with JSON examples
  - Detailed sequence diagrams and workflows
  - Extensive error handling and observability specifications

## Benefits

- Reduces spec creation time from weeks to minutes
- Ensures consistent format and comprehensive coverage
- Provides implementation-ready details engineers can code from directly
- Includes 20+ code examples per specification
- Features complete API contracts and database schemas
- Incorporates detailed testing strategies and observability plans
- Scales from 40-50 pages (8000-10000 words) of technical content

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

- `structured_output.json` - Comprehensive structured information extracted from the PRD
- `architecture_plan.md` - Detailed high-level architecture plan with component diagrams and implementation roadmap
- `final_spec.md` - **Production-ready technical specification (40-50 pages, 8000-10000 words)** including:
  - Actual code examples (20+ snippets)
  - Complete function/method definitions
  - SQL database schema definitions
  - Comprehensive API contracts with request/response examples
  - Detailed sequence diagrams
  - Error handling strategies with error codes
  - Observability specifications (logs, metrics, alerts)
  - Testing strategies and test cases
- `final_spec.html` - HTML version of the technical specification with proper formatting
- `tech_spec_review_structured.json` - Comprehensive analysis of the technical specification
- `tech_spec_review_architecture_plan.md` - Detailed architectural assessment and improvements
- `review_spec.md` - Extensive specification review with actionable feedback
- `review_spec.html` - HTML version of the specification review

## Directory Structure

- `input_docs/` - Contains input PRD files (default: `dcc_prd.pdf`)
- `repo/` - Contains repository context for architecture planning
- `guidelines/` - Contains specification guidelines
- `outputs/` - Contains all generated files

## License

[Specify license information here] 