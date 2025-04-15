import os
import json
import webbrowser
import argparse
import sys
import subprocess

def check_install_dependencies():
    """Check and install required dependencies"""
    print("🔍 Checking and installing required dependencies...")
    required_packages = ["pymupdf", "markdown"]
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"✅ {package} is already installed")
        except ImportError:
            print(f"📦 Installing {package}...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                print(f"✅ {package} installed successfully")
            except subprocess.CalledProcessError:
                print(f"❌ Failed to install {package}. Please install it manually: pip install {package}")
                sys.exit(1)

# Check and install dependencies
check_install_dependencies()

# Now import dependencies
import fitz  # PyMuPDF
import markdown
from openai import AzureOpenAI

# CONFIG
INPUT_PATH = "input_docs/dcc_prd.pdf"
REPO_PATH = "repo"
GUIDELINE_PATH = "guidelines/spec_guidelines.md"
OUTPUT_FOLDER = "outputs"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
TECH_SPEC_REVIEW_GUIDELINE_PATH = "guidelines/tech_spec_review_guidelines.md"

# ✅ Create shared LLM instance
OPENAI_API_KEY = "2RUOScQCo243qls9wgMaPBjwZ5LH3GENFPKjwTOkLZDPKm5Wh0icJQQJ99BDAC77bzfXJ3w3AAABACOGjxKB"  # keep this secret
AZURE_ENDPOINT = "https://fy26-hackon-q1.openai.azure.com"
AZURE_DEPLOYMENT = "Blueprint"
API_VERSION = "2025-01-01-preview"

client = AzureOpenAI(
    api_key=OPENAI_API_KEY,
    azure_endpoint=AZURE_ENDPOINT,
    api_version=API_VERSION
)

# Step 1: Extract text from PRD PDF
def extract_pdf_text(file_path):
    """Extract text from a PDF file with robust error handling"""
    # Check if file exists before attempting to open
    if not os.path.exists(file_path):
        print(f"❌ Error: PDF file not found at '{file_path}'")
        print("Please check if the file path is correct and the file exists")
        sys.exit(1)
    
    try:
        with fitz.open(file_path) as doc:
            return "\n".join(page.get_text() for page in doc)
    except Exception as e:
        print(f"❌ Error extracting text from PDF: {e}")
        print("Please ensure the file is a valid PDF document")
        sys.exit(1)

# Step 2: Analyze PRD → Structured Info
def analyze_prd(prd_text):
    system_instruction = (
        "You are a Senior Principal Engineer analyzing a Product Requirements Document (PRD). "
    "Your goal is to extract precise, actionable technical insights from the PRD. "
    "Translate user stories and product requirements into engineering constructs that can be implemented "
    "within an existing microservices architecture.\n\n"

    "Your response must include a JSON with the following keys:\n"
    "1. domain: High-level business or product context (e.g. Payments, Onboarding, Risk)\n"
    "2. features: List of product capabilities or user-facing features described\n"
    "3. goals: Engineering goals or outcomes expected (e.g. performance, compliance, reliability)\n"
    "4. apis: Any mentioned or implied API endpoints that will be used or impacted, including integration touchpoints\n"
    "5. recommended_tech_stack: List of relevant technologies for implementing this (e.g. Go, Postgres, Redis, Kafka, gRPC, HTTP)\n"
    "6. service_mapping: Map each feature or requirement to the most likely existing service(s) or component(s) that would own the logic\n"
    "7. data_models: Describe any expected entities, schemas, or data flow at a high level\n"
    "8. edge_cases: List any non-trivial edge cases, failure modes, or security/compliance concerns that should be handled\n\n"

    "Respond only in JSON format."
    )
    
    response = client.chat.completions.create(
        model=AZURE_DEPLOYMENT,
        messages=[
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": prd_text}
        ],
        temperature=0.3,
        response_format={"type": "json_object"}
    )
    
    try:
        # Get the raw content
        raw_content = response.choices[0].message.content
        
        # Check if the content is wrapped in code blocks
        if raw_content.startswith("```json") or raw_content.startswith("```"):
            # Extract the JSON part by removing the code block markers
            content_lines = raw_content.strip().split("\n")
            if content_lines[0].startswith("```"):
                content_lines = content_lines[1:-1]  # Remove first and last lines
            clean_content = "\n".join(content_lines)
            result = json.loads(clean_content)
        else:
            # Regular JSON parsing
            result = json.loads(raw_content)
            
        return result
    except json.JSONDecodeError as e:
        print(f"Failed to parse LLM response as JSON: {e}")
        print(f"Raw response: {response.choices[0].message.content[:200]}...")
        return {"error": "Invalid JSON", "raw": response.choices[0].message.content}

# Step 3: Load repo context
def load_repo_context(repo_path):
    service_mapping = {}
    for root, _, files in os.walk(repo_path):
        for file in files:
            if file.endswith(".md") or file.endswith(".txt"):
                service_name = os.path.basename(root)
                with open(os.path.join(root, file), "r") as f:
                    context = f.read()
                service_mapping[service_name] = context
    return service_mapping

# Step 4: Plan architecture
def plan_architecture(extracted_info, repo_context):
    feature_text = "\n".join(f"- {f}" for f in extracted_info.get("features", []))
    repo_summary = "\n".join([f"{k}: {v[:300]}..." for k, v in repo_context.items()])

    system_instruction = (
       "You are a Senior Principal Engineer responsible for designing robust and scalable system architectures "
    "within a complex microservices environment. You have access to a summary of existing repositories and features "
    "requested from a new product requirement.\n\n"
    "Your output should be as **detailed as possible**, covering all relevant aspects of the system, and structured in a way that it should have "
    "**clear sectioning**, **technical accuracy**, and **completeness**."

    "Your job is to:\n"
    "- Map each feature to existing services, modules, or packages where implementation should happen\n"
    "- Recommend creation of new services or components only if necessary\n"
    "- Leverage and reference reusable utilities, workflows, contracts, and interfaces wherever possible\n"
    "- Consider engineering constraints like service boundaries, data ownership, reliability, latency, and compliance\n"
    "- Reflect awareness of typical internal patterns (e.g. pub-sub via Kafka, gRPC/HTTP interfaces, internal SDKs)\n"
    "- Outline inter-service data flow if relevant\n"
    "- Keep in mind domain boundaries like Payments, Terminals, Risk, etc.\n\n"

    "Your output should be a high-level architecture plan in **Markdown** format with the following sections:\n"
    "1. Overview\n"
    "2. Feature-to-Service Mapping\n"
    "3. Suggested Code Touchpoints (functions, packages, interfaces, or modules)\n"
    "4. New Components (if needed) with rationale\n"
    "5. Data Flow & Interfaces\n"
    "6. Risks and Considerations\n"
    )

    response = client.chat.completions.create(
        model=AZURE_DEPLOYMENT,
        messages=[
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": f"Features:\n{feature_text}\n\nRepo Context:\n{repo_summary}"}
        ],
        temperature=0.3
    )
    
    return response.choices[0].message.content

# Step 5: Generate tech spec
def generate_tech_spec(architecture_plan, guideline_path):
    with open(guideline_path, "r") as f:
        guidelines = f.read()

    system_instruction = (
   "You are a Senior Principal Engineer responsible for drafting a detailed and implementation-ready technical specification "
    "based on the provided architecture plan. This specification is meant for internal engineering, SRE, and product teams, and must follow "
    "the internal tech spec format strictly.\n\n"
    "Your output should be as **detailed as possible**, covering all relevant aspects of the system, and structured in a way that it should have "
    "**clear sectioning**, **technical accuracy**, and **completeness**, ensuring that it can be **directly copied into a Google Doc** for review and further distribution."

    "You must:\n"
    "- Interpret the architecture plan to identify the final approach, data flow, service mapping, and external dependencies\n"
    "- Follow the exact section order and headings from the provided Tech Spec Template\n"
    "- Populate all relevant sections with technical reasoning, proposed changes, diagrams (described in text), data flows, and rollout mechanisms\n"
    "- Clearly specify any schema changes, API contracts, gRPC/proto formats, and system-level configuration needs\n"
    "- Call out edge case handling, retry/timeout strategies, observability, and migration/rollback considerations\n"
    "- Use <placeholder> tags like `<Insert>`, `<dd/mm/yyyy>`, `<To be filled>` for fields not provided\n"
    "- Output the entire response in **Markdown format** using the given Tech Spec Template without altering structure or headings\n\n"

    "The final spec should reflect:\n"
    "- Production readiness\n"
    "- Code-level impact and touchpoints\n"
    "- Engineering, infra, and security considerations\n"
    "- A clear path for rollout and testing\n\n"

    "Strictly use the following Markdown format when generating your output:\n\n"
    "# Tech Spec Template\n\n"
    "**Title**: <Insert clear and concise project title>  \n"
    "**Author/s**: <List all authors>  \n"
    "**Team/Pod**: <e.g. Terminals & Routing>  \n"
    "**BU**: <e.g. Payments>  \n"
    "**Published Date**: <dd/mm/yyyy>  \n\n"
    "**Reviewer Name | Reviewed Date | Status**  \n"
    "- Reviewer 1 | <dd/mm/yyyy> | <Status>  \n"
    "- Reviewer 2 | <dd/mm/yyyy> | <Status>  \n\n"
    "---\n\n"
    "## 1. Problem Statement  \nDescribe the problem being addressed...\n\n"
    "## 2. Introduction and Scope  \nExplain the context and project purpose...\n\n"
    "### Scope  \n- <...>\n\n"
    "### Out of Scope  \n- <...>\n\n"
    "## 3. Assumptions  \n- <...>\n\n"
    "## 4. Current Architecture  \n### 4.1 Legacy System\n### 4.2 Intermediate Stack\n### 4.3 Target System\n\n"
    "## 5. Final Approach  \n### 5.1 Data Flow\n### 5.2 Data Model Changes\n### 5.3 Event Consumption Logic\n"
    "### 5.4 Context Awareness / Routing\n### 5.5 External Integrations\n### 5.6 Rollout Specific Enhancements\n"
    "### 5.7 Settings / Config Requirements\n\n"
    "## 6. Dependencies\n| Service Name | Dependency Description | SLA | POC |\n|--------------|-------------------------|-----|-----|\n\n"
    "## 7. Schema Changes  \n- <...>\n\n"
    "## 8. Rollout Plan  \n### 8.1 Dry Run\n### 8.2 Merchant Level Rollout\n### 8.3 PG Level Rollout\n\n"
    "## 9. Rollback Strategy  \n<...>\n\n"
    "## 10. Traffic Estimates  \n<...>\n\n"
    "## 11. System Stability Plan  \n<...>\n\n"
    "## 12. Open Questions  \n<...>\n\n"
    "## 13. Migration Experience  \n<...>\n\n"
    "## 14. Future Enhancements  \n<...>\n\n"
    "## 15. Pre and Post Migration Comparison  \n<...>\n\n"
    "**Document Link**: [To be added once uploaded]  \n"
    "**Slack Thread for Review**: [Insert thread link]"
)

    response = client.chat.completions.create(
        model=AZURE_DEPLOYMENT,
        messages=[
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": f"Architecture Plan:\n{architecture_plan}\n\nGuidelines:\n{guidelines}"}
        ],
        temperature=0.3
    )
    
    return response.choices[0].message.content

def analyze_tech_spec(tech_spec_text):
    system_instruction = (
        "You are a technical spec analyzer. Your job is to extract structured insights from a technical specification document. "
        "Parse and summarize the document into the following keys in JSON format: "
        "1. 'domain' - the problem space and business context, "
        "2. 'features' - a list of user-facing or backend features mentioned, "
        "3. 'goals' - engineering or design objectives stated in the spec, "
        "4. 'apis' - a list of any public-facing or internal APIs referenced or proposed. "
        "Return only a valid JSON object with keys: domain, features, goals, apis."
    )
    response = client.chat.completions.create(
        model=AZURE_DEPLOYMENT,
        messages=[
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": tech_spec_text}
        ],
        temperature=0.3
    )
    try:
        return json.loads(response.choices[0].message.content)
    except json.JSONDecodeError:
        return {"error": "Invalid JSON", "raw": response.choices[0].message.content}
    
def tech_spec_plan_architecture(extracted_info, repo_context):
    feature_text = "\n".join(f"- {f}" for f in extracted_info.get("features", []))
    repo_summary = "\n".join([f"{k}: {v[:300]}..." for k, v in repo_context.items()])
    system_instruction = (
        "You are a system architect AI. Given extracted features and the current codebase context, "
        "map each feature to an existing service (if possible) or propose new services/components. "
        "Return a clear, high-level system architecture plan in **Markdown format**, including service names, data flow, and responsibilities. "
        "Avoid implementation details — focus on structure, integration, and ownership."
    )
    response = client.chat.completions.create(
        model=AZURE_DEPLOYMENT,
        messages=[
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": f"Features:\n{feature_text}\n\nRepo Context:\n{repo_summary}"}
        ],
        temperature=0.3
    )
    return response.choices[0].message.content

def review_tech_spec(architecture_plan, guideline_path):
    with open(guideline_path, "r") as f:
        guidelines = f.read()
    system_instruction = (
        "You are a technical writer and reviewer assistant. Given a system architecture plan and internal spec guidelines, "
        "compose a full technical specification in Markdown format. Ensure the spec is clear, well-structured, and adheres to the provided guidelines. "
        "Include sections such as Overview, Features, Architecture Diagram (if described), API Contracts (if mentioned), and Open Questions. "
        "Make the output suitable for internal team review or handoff to engineering."
    )
    response = client.chat.completions.create(
        model=AZURE_DEPLOYMENT,
        messages=[
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": f"Architecture Plan:\n{architecture_plan}\n\nGuidelines:\n{guidelines}"}
        ],
        temperature=0.3
    )
    return response.choices[0].message.content

def markdown_to_html(md_text, output_html_path):
    try:
        # Try using the Python markdown module
        try:
            import markdown
            html_content = markdown.markdown(
                md_text,
                extensions=['tables', 'fenced_code', 'codehilite']
            )
        except ImportError:
            # If markdown module is not available, do a simple conversion
            html_content = f"<pre>{md_text}</pre>"
        
        # Add CSS styling
        styled_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Technical Specification</title>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                    line-height: 1.6;
                    padding: 40px;
                    max-width: 900px;
                    margin: 0 auto;
                    color: #333;
                }}
                h1, h2, h3, h4 {{
                    color: #0066cc;
                    margin-top: 24px;
                    margin-bottom: 16px;
                }}
                h1 {{ font-size: 28px; border-bottom: 1px solid #eee; padding-bottom: 10px; }}
                h2 {{ font-size: 24px; border-bottom: 1px solid #eee; padding-bottom: 8px; }}
                h3 {{ font-size: 20px; }}
                h4 {{ font-size: 16px; }}
                pre {{
                    background-color: #f6f8fa;
                    border-radius: 3px;
                    padding: 16px;
                    overflow: auto;
                    font-family: SFMono-Regular, Consolas, "Liberation Mono", Menlo, monospace;
                }}
                code {{
                    background-color: rgba(27, 31, 35, 0.05);
                    border-radius: 3px;
                    font-family: SFMono-Regular, Consolas, "Liberation Mono", Menlo, monospace;
                    padding: 0.2em 0.4em;
                }}
                table {{
                    border-collapse: collapse;
                    width: 100%;
                    margin-bottom: 20px;
                }}
                table, th, td {{
                    border: 1px solid #ddd;
                }}
                th, td {{
                    padding: 12px;
                    text-align: left;
                }}
                th {{
                    background-color: #f2f2f2;
                }}
                blockquote {{
                    border-left: 4px solid #ddd;
                    padding-left: 16px;
                    color: #666;
                    margin-left: 0;
                }}
                ul, ol {{
                    padding-left: 2em;
                }}
                img {{
                    max-width: 100%;
                }}
            </style>
        </head>
        <body>
            {html_content}
        </body>
        </html>
        """
        
        # Save the HTML file
        with open(output_html_path, 'w', encoding='utf-8') as f:
            f.write(styled_html)
            
        print(f"✅ HTML file created at: {output_html_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error creating HTML: {e}")
        return False

def open_output_file(file_path):
    """Helper function to open the output file in browser"""
    try:
        webbrowser.open(f"file://{os.path.abspath(file_path)}")
        print(f"🎉 Pipeline complete! Check your browser to view the output.")
    except Exception as e:
        print(f"Could not open browser: {e}")
        print(f"🎉 Pipeline complete! Your file is available at: {file_path}")

def generate_workflow(input_path=INPUT_PATH, repo_path=REPO_PATH, guideline_path=GUIDELINE_PATH):
    """Execute the generation workflow (Steps 1-5)"""
    # Validate all required paths exist
    if not os.path.exists(input_path):
        print(f"❌ Error: PRD file not found at '{input_path}'")
        print("Please provide a valid path to the PRD PDF file")
        sys.exit(1)
    
    if not os.path.exists(repo_path):
        print(f"❌ Error: Repository context not found at '{repo_path}'")
        print("Please provide a valid path to the repository context")
        sys.exit(1)
    
    if not os.path.exists(guideline_path):
        print(f"❌ Error: Guidelines file not found at '{guideline_path}'")
        print("Please provide a valid path to the specification guidelines")
        sys.exit(1)
        
    print(f"🔍 Step 1: Extracting PRD from '{input_path}'...")
    prd_text = extract_pdf_text(input_path)
    
    print("🧠 Step 2: Analyzing PRD...")
    structured = analyze_prd(prd_text)
    with open(os.path.join(OUTPUT_FOLDER, "structured_output.json"), "w") as f:
        json.dump(structured, f, indent=2)

    print("📚 Step 3: Loading repo context...")
    repo_context = load_repo_context(repo_path)

    print("🧱 Step 4: Planning architecture...")
    plan = plan_architecture(structured, repo_context)
    with open(os.path.join(OUTPUT_FOLDER, "architecture_plan.md"), "w") as f:
        f.write(plan)

    print("📝 Step 5: Generating tech spec...")
    spec = generate_tech_spec(plan, guideline_path)

    # Generate outputs
    final_md_path = os.path.join(OUTPUT_FOLDER, "final_spec.md")
    final_html_path = os.path.join(OUTPUT_FOLDER, "final_spec.html")

    # Save the markdown
    with open(final_md_path, "w", encoding="utf-8") as f:
        f.write(spec)
    print(f"✅ Markdown spec saved at: {final_md_path}")

    # Convert to HTML
    success = markdown_to_html(spec, final_html_path)

    # Determine which file to open
    file_to_open = final_html_path if success else final_md_path

    # Open the file in browser
    open_output_file(file_to_open)
    
    return spec  # Return the spec for potential future use

def review_workflow(spec_path=None):
    """Execute the review workflow (Steps 6-8)"""
    # If no spec path is provided, use the default final_spec.md
    if not spec_path:
        spec_path = os.path.join(OUTPUT_FOLDER, "final_spec.md")
    
    # Check if the file exists
    if not os.path.exists(spec_path):
        print(f"❌ Warning: Spec file not found at '{spec_path}'")
        
        # Ask user if they want to generate a spec first
        user_input = input("Would you like to generate a spec first? (y/n): ").strip().lower()
        if user_input == 'y' or user_input == 'yes':
            print("Generating spec first...")
            spec = generate_workflow()
        else:
            print("Review process cannot continue without a spec file.")
            sys.exit(1)
    else:
        # Load the spec
        with open(spec_path, "r", encoding="utf-8") as f:
            spec = f.read()
    
    print("🧠 Step 6: Analyzing Tech Spec...")
    tech_spec_review_structured = analyze_tech_spec(spec)
    review_output_json = os.path.join(OUTPUT_FOLDER, "tech_spec_review_structured.json")
    with open(review_output_json, "w") as f:
        json.dump(tech_spec_review_structured, f, indent=2)
    
    print("🧱 Step 7: Planning review architecture...")
    repo_context = load_repo_context(REPO_PATH)
    tech_spec_review_plan = tech_spec_plan_architecture(tech_spec_review_structured, repo_context)
    review_plan_path = os.path.join(OUTPUT_FOLDER, "tech_spec_review_architecture_plan.md")
    with open(review_plan_path, "w") as f:
        f.write(tech_spec_review_plan)
    
    print("📝 Step 8: Generating tech spec review...")
    spec_review = review_tech_spec(tech_spec_review_plan, TECH_SPEC_REVIEW_GUIDELINE_PATH)
    
    # Save the review output
    review_md_path = os.path.join(OUTPUT_FOLDER, "review_spec.md")
    review_html_path = os.path.join(OUTPUT_FOLDER, "review_spec.html")
    
    with open(review_md_path, "w", encoding="utf-8") as f:
        f.write(spec_review)
    print(f"✅ Review markdown saved at: {review_md_path}")
    
    # Convert to HTML
    success = markdown_to_html(spec_review, review_html_path)
    
    # Determine which file to open
    file_to_open = review_html_path if success else review_md_path
    
    # Open the file in browser
    open_output_file(file_to_open)

if __name__ == "__main__":
    # Create the main parser
    parser = argparse.ArgumentParser(
        description="Blueprint: AI-powered technical specification generator",
        epilog="""
Examples:
  # Generate a spec using default paths
  python blueprint.py generate
  
  # Generate a spec with a custom PRD file
  python blueprint.py generate --input path/to/prd.pdf
  
  # Review an existing spec file
  python blueprint.py review --spec path/to/spec.md
  
  # Show this help message
  python blueprint.py --help
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Add subparsers for the main commands
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Generate command
    generate_parser = subparsers.add_parser(
        "generate", 
        help="Generate a technical specification from a PRD",
        description="Generate a comprehensive technical specification from a Product Requirements Document (PRD)"
    )
    generate_parser.add_argument(
        "--input", "-i", 
        help=f"Path to the PRD PDF file (default: {INPUT_PATH})", 
        default=INPUT_PATH
    )
    generate_parser.add_argument(
        "--repo", "-r", 
        help=f"Path to the repository context (default: {REPO_PATH})", 
        default=REPO_PATH
    )
    generate_parser.add_argument(
        "--guidelines", "-g", 
        help=f"Path to the specification guidelines (default: {GUIDELINE_PATH})", 
        default=GUIDELINE_PATH
    )
    
    # Review command
    review_parser = subparsers.add_parser(
        "review", 
        help="Review an existing technical specification",
        description="Analyze and review an existing technical specification document"
    )
    review_parser.add_argument(
        "--spec", "-s", 
        help="Path to the technical specification to review (default: outputs/final_spec.md)",
        default=os.path.join(OUTPUT_FOLDER, "final_spec.md")
    )
    
    # Parse the arguments
    args = parser.parse_args()
    
    # Display help if no command is provided
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        if args.command == "generate":
            print(f"Running generate workflow with:")
            print(f"- Input PRD: {args.input}")
            print(f"- Repo context: {args.repo}")
            print(f"- Guidelines: {args.guidelines}")
            generate_workflow(args.input, args.repo, args.guidelines)
        elif args.command == "review":
            spec_path = args.spec or os.path.join(OUTPUT_FOLDER, "final_spec.md")
            print(f"Running review workflow on: {spec_path}")
            review_workflow(spec_path)
        else:
            # This should not happen due to the argparse configuration
            print(f"❌ Unknown command: {args.command}")
            parser.print_help()
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️ Process interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"❌ An error occurred: {e}")
        print("Please check your inputs and try again")
        sys.exit(1) 