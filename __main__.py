import os
import fitz  # PyMuPDF (ensure installed: pip install pymupdf)
import json
import webbrowser
import re
import sys
from openai import AzureOpenAI

# Attempt to import markdown and set a flag
try:
    import markdown
    MARKDOWN_AVAILABLE = True
    print("✅ Markdown library found. HTML output will be generated.")
except ImportError:
    MARKDOWN_AVAILABLE = False
    print("⚠️ Python 'markdown' package not found. HTML output will be basic <pre> text.")
    print("   For richer HTML install using: pip install markdown Markdown-Tables python-markdown-math")

# --- Configuration ---
# Input/Output Paths
INPUT_PATH = "input_docs/dcc_prd.pdf"  # Path to your input Product Requirements Document PDF
REPO_PATH = "repo"                     # Path to your code repository/context documentation
GUIDELINE_PATH = "guidelines/spec_guidelines.md" # Path to your standard tech spec template/guidelines
SPEC_EXAMPLES_PATH = "spec_examples"   # Folder containing good/bad spec examples (now expects PDFs)
OUTPUT_FOLDER = "outputs"              # Folder where all generated files will be saved
TECH_SPEC_REVIEW_GUIDELINE_PATH = "guidelines/tech_spec_review_guidelines.md" # Guidelines specifically for reviewing specs

# Create output folder if it doesn't exist
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Azure OpenAI Credentials (❗️ Best Practice: Use Environment Variables ❗️)
# Replace "YOUR_..." values ONLY if not using environment variables.
OPENAI_API_KEY = os.getenv("AZURE_OPENAI_KEY", "2RUOScQCo243qls9wgMaPBjwZ5LH3GENFPKjwTOkLZDPKm5Wh0icJQQJ99BDAC77bzfXJ3w3AAABACOGjxKB")
AZURE_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "https://fy26-hackon-q1.openai.azure.com")
AZURE_DEPLOYMENT = "Blueprint" # Your Azure deployment name
API_VERSION = "2025-01-01-preview"     # Use a stable API version

# Basic check for placeholder credentials
if "YOUR_API_KEY" in OPENAI_API_KEY or "YOUR_ENDPOINT" in AZURE_ENDPOINT:
    print("🚨 WARNING: Azure OpenAI credentials look like placeholders.")
    print("   Please set AZURE_OPENAI_KEY and AZURE_OPENAI_ENDPOINT environment variables or replace placeholders in the script.")
    # Consider exiting if credentials are required
    # import sys
    # sys.exit("Exiting: Azure OpenAI credentials not configured.")

# --- Initialize Azure OpenAI Client ---
try:
    client = AzureOpenAI(
        api_key=OPENAI_API_KEY,
        azure_endpoint=AZURE_ENDPOINT,
        api_version=API_VERSION
    )
    # You could add a simple test call here if needed, e.g., list models
    print("✅ Azure OpenAI client initialized.")
except Exception as e:
    print(f"❌ Failed to initialize Azure OpenAI client: {e}")
    print("   Please check your API key, endpoint, and network connection.")
    import sys
    sys.exit("Exiting: OpenAI client initialization failed.")

# === Core Functions ===

# --- Function 1: Extract Text from PDF ---
def extract_pdf_text(file_path):
    """Extracts all text content from a PDF file using PyMuPDF (fitz)."""
    if not os.path.exists(file_path):
        print(f"❌ Error: PDF file not found at {file_path}")
        return None
    try:
        with fitz.open(file_path) as doc:
            full_text = "\n".join(page.get_text("text", sort=True).strip() for page in doc if page.get_text())
            # Sort=True can help with reading order on some documents
            # Added check to avoid joining None if a page has no text
        if not full_text:
             print(f"⚠️ Warning: No text extracted from PDF {file_path}. It might be empty or image-based.")
             return None # Return None if no text could be extracted
        # print(f"   📄 Extracted ~{len(full_text)} characters from {os.path.basename(file_path)}")
        return full_text
    except Exception as e:
        print(f"❌ Error opening or reading PDF {file_path}: {e}")
        return None # Indicate failure

# --- Function 2: Parse LLM JSON Response Safely ---
def parse_llm_json_response(response):
    """Safely parses JSON from LLM response, handling potential markdown code blocks."""
    try:
        # Check if response structure is as expected
        if not response or not response.choices or not response.choices[0].message or not response.choices[0].message.content:
             print("❌ Error: Unexpected LLM response structure.")
             return {"error": "Invalid LLM response structure", "raw_content": None}

        raw_content = response.choices[0].message.content.strip()

        # Remove potential markdown code block fences (```json ... ``` or ``` ... ```)
        match = re.search(r'```(?:json)?\s*(.*?)\s*```', raw_content, re.DOTALL | re.IGNORECASE)
        if match:
            clean_content = match.group(1).strip()
        else:
            # Assume the entire content is JSON if no code block fences are found
            clean_content = raw_content

        # Attempt to parse the cleaned content
        return json.loads(clean_content)

    except json.JSONDecodeError as e:
        print(f"❌ Failed to parse LLM response as JSON: {e}")
        raw_response_snippet = getattr(response.choices[0].message, 'content', 'N/A')
        print(f"   Raw response snippet: {raw_response_snippet[:300]}...")
        return {"error": "Invalid JSON received from LLM", "raw_content": raw_response_snippet}
    except (AttributeError, IndexError, TypeError) as e:
        print(f"❌ Error accessing LLM response content: {e}")
        return {"error": "Unexpected response structure from LLM", "raw_content": str(response)}
    except Exception as e: # Catch any other unexpected errors
        print(f"❌ An unexpected error occurred during JSON parsing: {e}")
        return {"error": f"Unexpected error during JSON parsing: {e}", "raw_content": getattr(response.choices[0].message, 'content', 'N/A')}

# --- Function 3: Analyze PRD Text ---
def analyze_prd(prd_text):
    """Analyzes PRD text using LLM to extract structured information."""
    if not prd_text:
        return {"error": "PRD text is empty or could not be extracted."}

    print("   🧠 Sending PRD text to LLM for analysis...")
    system_instruction = (
        "You are a Senior Principal Engineer analyzing a Product Requirements Document (PRD). "
        "Your goal is to extract precise, actionable technical insights. "
        "Translate requirements into engineering constructs for a microservices architecture.\n\n"
        "Your response must be a single, valid JSON object with these keys:\n"
        "1. domain: High-level product context (e.g., Payments, Onboarding, Risk).\n"
        "2. features: List of specific user-facing or backend features described.\n"
        "3. goals: Key engineering goals implied (e.g., performance, compliance, scalability).\n"
        "4. apis: Mentioned or implied API endpoints (internal/external) impacted or needed.\n"
        "5. recommended_tech_stack: Relevant technologies suggested or implied (e.g., Go, Postgres, Kafka, gRPC).\n"
        "6. service_mapping: Initial thoughts on mapping features to potential existing microservices.\n"
        "7. data_models: High-level description of expected data entities, schemas, or flows.\n"
        "8. edge_cases: Non-trivial edge cases, failure modes, or security/compliance concerns.\n\n"
        "Respond ONLY with the JSON object, without any introductory text or markdown formatting."
    )

    try:
        response = client.chat.completions.create(
            model=AZURE_DEPLOYMENT,
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": prd_text}
            ],
            temperature=0.2, # Lower temperature for more predictable JSON extraction
            response_format={"type": "json_object"}
        )
        print("   ✅ LLM analysis received.")
        return parse_llm_json_response(response)
    except Exception as e:
        print(f"❌ Error calling OpenAI API during PRD analysis: {e}")
        return {"error": f"API call failed during PRD analysis: {e}", "raw_content": None}

# --- Function 4: Load Repository Context ---
def load_repo_context(repo_path):
    """Loads context from documentation files (README.md, etc.) within a repository structure."""
    service_mapping = {}
    if not os.path.isdir(repo_path):
        print(f"⚠️ Repository context path '{repo_path}' not found or is not a directory. Skipping context loading.")
        return service_mapping

    print(f"   Scannning repository path: {repo_path}")
    context_files_found = 0
    # Look for specific files like README.md, ARCHITECTURE.md, or overview docs
    relevant_filenames = ["readme.md", "architecture.md", "overview.md", "service.md", "readme.txt", "overview.txt"]

    for root, _, files in os.walk(repo_path):
        # Try to identify a service name from the directory path
        # Assumes services are in subdirectories, e.g., repo/service-a/, repo/service-b/
        relative_path = os.path.relpath(root, repo_path)
        service_name = relative_path.split(os.sep)[0] if relative_path != '.' else os.path.basename(repo_path) # Use folder name

        for file in files:
            if file.lower() in relevant_filenames:
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding='utf-8', errors='ignore') as f:
                        context = f.read()
                    # Add context, creating entry if it doesn't exist
                    if service_name not in service_mapping:
                        service_mapping[service_name] = ""
                    service_mapping[service_name] += f"\n\n--- Context from {os.path.relpath(file_path, repo_path)} ---\n{context}"
                    context_files_found += 1
                    # print(f"     Loaded context for '{service_name}' from '{os.path.relpath(file_path, repo_path)}'")
                except Exception as e:
                    print(f"     ⚠️ Could not read context file {file_path}: {e}")

    if context_files_found > 0:
        print(f"   ✅ Found context from {context_files_found} files in {len(service_mapping)} potential service directories.")
    else:
         print(f"   ⚠️ No relevant context files ({', '.join(relevant_filenames)}) found in {repo_path}.")
    return service_mapping

# --- Function 5: Load Spec Examples from PDF ---
def load_spec_examples(examples_path):
    """Loads good and bad tech spec examples from PDF files using extract_pdf_text."""
    examples = {"good": None, "bad": None}
    # Define paths for expected PDF files
    good_pdf_path = os.path.join(examples_path, "good_spec_example.pdf")
    bad_pdf_path = os.path.join(examples_path, "bad_spec_example.pdf")

    # Check if the examples directory exists
    if not os.path.isdir(examples_path):
        print(f"⚠️ Spec examples directory '{examples_path}' not found. Cannot load examples.")
        return examples # Return defaults (None)

    print(f"   Looking for spec examples in: {examples_path}")

    # --- Load Good Example PDF ---
    if os.path.exists(good_pdf_path):
        print(f"   Attempting to load good spec example from PDF: {good_pdf_path}")
        extracted_text = extract_pdf_text(good_pdf_path) # Reuse PDF extractor
        if extracted_text:
            examples["good"] = extracted_text
            print(f"   ✅ Loaded good spec example text from PDF.")
        else:
            print(f"   ⚠️ Failed to extract text from good spec PDF (or PDF was empty): {good_pdf_path}")
    else:
        print(f"   ⚠️ Good spec example PDF file not found: {good_pdf_path}")

    # --- Load Bad Example PDF ---
    if os.path.exists(bad_pdf_path):
        print(f"   Attempting to load bad spec example from PDF: {bad_pdf_path}")
        extracted_text = extract_pdf_text(bad_pdf_path) # Reuse PDF extractor
        if extracted_text:
            examples["bad"] = extracted_text
            print(f"   ✅ Loaded bad spec example text from PDF.")
        else:
            print(f"   ⚠️ Failed to extract text from bad spec PDF (or PDF was empty): {bad_pdf_path}")
    else:
        print(f"   ⚠️ Bad spec example PDF file not found: {bad_pdf_path}")

    return examples

# --- Function 6: Plan Architecture ---
def plan_architecture(extracted_info, repo_context):
    """Generates a high-level architecture plan using LLM based on PRD analysis and repo context."""
    # Validate input from PRD analysis
    if "error" in extracted_info or not isinstance(extracted_info.get("features"), list) or not extracted_info.get("features"):
         error_msg = extracted_info.get("error", "Missing features in structured info.")
         print(f"⚠️ Skipping architecture planning: {error_msg}")
         return f"Error: Could not plan architecture. Reason: {error_msg}"

    print("   🧠 Sending features and repo context to LLM for architecture planning...")
    feature_list = extracted_info.get("features", [])
    feature_text = "\n".join(f"- {f}" for f in feature_list)
    repo_summary = "\n".join([f"Service: {k}\nContext Summary:\n{v[:350]}...\n---" for k, v in repo_context.items()]) if repo_context else "No repository context provided."

    system_instruction = (
        "You are a Senior Solutions Architect designing a high-level system architecture "
        "within an existing microservices environment.\n\n"
        "Based on the requested features and the summary of existing services (repo context):\n"
        "1.  **Map each feature** to the most appropriate existing service(s). Clearly name the service.\n"
        "2.  If a feature doesn't fit, **propose a new service/component** with rationale and responsibility.\n"
        "3.  Outline primary **interactions or data flow** between services (e.g., Service A calls Service B via gRPC, Service C publishes Kafka event).\n"
        "4.  Consider service boundaries, data ownership, potential reuse, and common patterns (events, sync calls).\n"
        "5.  Output a **clear, concise architecture plan in Markdown format** using the sections below.\n\n"
        "Required Sections:\n"
        "1.  **Overview:** Brief summary of changes.\n"
        "2.  **Feature-to-Service Mapping:** Feature -> Target Service(s) or 'New Service Needed'.\n"
        "3.  **New Components (If Any):** Proposed new services/components, purpose, justification.\n"
        "4.  **High-Level Data Flow / Interactions:** Key communication paths.\n"
        "5.  **Key Considerations / Risks:** Obvious dependencies, scaling, potential issues."
    )

    user_content = f"**Requested Features:**\n{feature_text}\n\n**Existing Repository Context Summary:**\n{repo_summary}"

    try:
        response = client.chat.completions.create(
            model=AZURE_DEPLOYMENT,
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_content}
            ],
            temperature=0.3,
            max_tokens=2000 # Allow reasonable length for the plan
        )
        print("   ✅ LLM architecture plan received.")
        return response.choices[0].message.content
    except Exception as e:
        print(f"❌ Error calling OpenAI API during architecture planning: {e}")
        return f"Error: API call failed during architecture planning.\n{e}"

# --- Function 7: Generate Tech Spec Draft ---
def generate_tech_spec_draft(architecture_plan, guideline_path):
    """Generates a detailed tech spec draft using LLM based on the architecture plan and guidelines."""
    if architecture_plan.startswith("Error:"): # Check if planning failed
        print(f"⚠️ Skipping tech spec generation: {architecture_plan}")
        return f"Error: Cannot generate tech spec draft. {architecture_plan}"

    # Load guidelines
    try:
        print(f"   Loading tech spec guidelines from: {guideline_path}")
        with open(guideline_path, "r", encoding='utf-8') as f:
            guidelines = f.read()
        if not guidelines:
             print(f"⚠️ Warning: Guideline file '{guideline_path}' is empty.")
             # Decide if you want to proceed with a default structure or return error
             return f"Error: Tech spec guideline file '{guideline_path}' is empty."
    except Exception as e:
        print(f"❌ Error reading tech spec guidelines file {guideline_path}: {e}")
        return f"Error: Could not read tech spec guidelines file: {e}"

    print("   🧠 Sending architecture plan and guidelines to LLM for tech spec draft generation...")
    system_instruction = (
        "You are a Senior Principal Engineer drafting a **detailed technical specification DRAFT**.\n"
        "Base this draft *only* on the provided Architecture Plan and follow the Tech Spec Template Guidelines strictly.\n\n"
        "Instructions:\n"
        "- **Adhere strictly** to the structure, headings, and formatting from the 'Tech Spec Template' in the guidelines.\n"
        "- **Populate ALL sections** of the template using information from the 'Architecture Plan'.\n"
        "- **Expand** on the plan: Add potential API details (simple format), data model ideas, specific components/modules affected, config needs, etc., *as implied by the plan*.\n"
        "- Use clear placeholders like `<To be defined>`, `<Needs detailing>`, `<Placeholder: ...>`, `<Diagram description needed>` where the plan lacks detail. **Do NOT invent technical details** not present or implied.\n"
        "- Address data flow, dependencies, high-level schema impact, initial rollout/rollback thoughts.\n"
        "- Output **ONLY the Markdown content** of the spec, matching the template structure exactly.\n\n"
        "Goal: Create a comprehensive *first draft* based *solely* on the provided plan and template, ready for detailed engineering review."
    )

    user_content = f"**Architecture Plan:**\n```markdown\n{architecture_plan}\n```\n\n**Tech Spec Template Guidelines (Use this structure EXACTLY):**\n```markdown\n{guidelines}\n```"

    try:
        response = client.chat.completions.create(
            model=AZURE_DEPLOYMENT,
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_content}
            ],
            temperature=0.25, # Slightly lower temp for adherence to template
            max_tokens=3800   # Allow ample space for a detailed spec
        )
        print("   ✅ LLM tech spec draft received.")
        # Basic check if response seems empty or too short
        if len(response.choices[0].message.content) < 100:
             print("⚠️ Warning: Generated tech spec draft seems very short.")
        return response.choices[0].message.content
    except Exception as e:
        print(f"❌ Error calling OpenAI API during tech spec draft generation: {e}")
        return f"Error: API call failed during tech spec draft generation.\n{e}"

# --- Function 8: Review Tech Spec Draft ---
def review_tech_spec(tech_spec_draft, review_guideline_path, good_example_text, bad_example_text):
    """Reviews the tech spec draft using LLM, comparing against guidelines and examples (good/bad)."""
    if tech_spec_draft.startswith("Error:"):
         print(f"⚠️ Skipping tech spec review: {tech_spec_draft}")
         return f"Error: Cannot review tech spec. {tech_spec_draft}"

    # Load review-specific guidelines
    review_guidelines = "No specific review guidelines provided." # Default
    try:
        if os.path.exists(review_guideline_path):
            print(f"   Loading tech spec review guidelines from: {review_guideline_path}")
            with open(review_guideline_path, "r", encoding='utf-8') as f:
                review_guidelines = f.read() or review_guidelines # Keep default if file is empty
        else:
             print(f"⚠️ Review guideline file not found: {review_guideline_path}. Using default guidance.")
    except Exception as e:
        print(f"❌ Error reading tech spec review guidelines file {review_guideline_path}: {e}")
        print("   ⚠️ Proceeding with default review guidance.")

    # Prepare example texts for the prompt
    good_example_prompt = f"\n**Good Tech Spec Example (Reference for Quality):**\n```\n{good_example_text}\n```" if good_example_text else "\n**Good Tech Spec Example:** Not Available."
    bad_example_prompt = f"\n**Bad Tech Spec Example (Reference for Pitfalls):**\n```\n{bad_example_text}\n```" if bad_example_text else "\n**Bad Tech Spec Example:** Not Available."

    print("   🧠 Sending draft, guidelines, and examples to LLM for review...")
    system_instruction = (
        "You are a Senior Technical Reviewer evaluating a draft technical specification.\n"
        "Provide **constructive feedback** to improve the draft, comparing it against guidelines and examples.\n\n"
        "Instructions:\n"
        "- Analyze the provided **Tech Spec Draft**.\n"
        "- Consult the **Review Guidelines**.\n"
        "- Compare the draft against the **Good Example** (for quality benchmarks) and **Bad Example** (for common pitfalls).\n"
        "- **Identify strengths:** Where does the draft align well with guidelines or the good example?\n"
        "- **Identify weaknesses:** Point out sections that are unclear, lack detail, deviate from guidelines, or resemble the bad example.\n"
        "- **Suggest concrete actions:** Propose specific improvements (e.g., 'Add sequence diagram for X', 'Specify API contract for Y', 'Elaborate on error handling Z').\n"
        "- Structure feedback clearly in Markdown using the format below.\n\n"
        "Output Format (Markdown):\n"
        "## Tech Spec Review & Feedback\n\n"
        "**Overall Assessment:** (Brief summary of draft quality and readiness)\n\n"
        "**Strengths:**\n- (Point 1)\n- ...\n\n"
        "**Areas for Improvement / Weaknesses:**\n"
        "- **Section [Name/Number]:** (Issue description. Reference bad example if relevant)\n"
        "  - *Suggestion:* (Concrete action)\n"
        "- ...\n"
        "**General Feedback:** (Overall comments like missing diagrams, consistency issues)\n\n"
        "**Comparison with Examples:**\n- (How does it stack up against the good/bad examples?)\n\n"
        "**Recommendations / Next Steps:**\n- (Priority revisions needed)"
    )

    user_content = (
        f"**Tech Spec Draft to Review:**\n```markdown\n{tech_spec_draft}\n```\n\n"
        f"**Review Guidelines:**\n```markdown\n{review_guidelines}\n```\n"
        f"{good_example_prompt}\n"
        f"{bad_example_prompt}"
    )

    try:
        response = client.chat.completions.create(
            model=AZURE_DEPLOYMENT,
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_content}
            ],
            temperature=0.4, # Slightly higher temp for more nuanced feedback
            max_tokens=2500  # Allow good length for review comments
        )
        print("   ✅ LLM tech spec review received.")
        return response.choices[0].message.content
    except Exception as e:
        print(f"❌ Error calling OpenAI API during tech spec review: {e}")
        return f"Error: API call failed during tech spec review.\n{e}"

# --- Function 9: Convert Markdown to HTML ---
def markdown_to_html(md_text, output_html_path):
    """Converts Markdown text to a styled HTML file."""
    html_content = ""
    title = os.path.basename(output_html_path).replace('.html', '').replace('_', ' ').title()

    # Basic CSS Styling (can be externalized to a .css file if preferred)
    html_style = """
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; line-height: 1.6; padding: 25px; max-width: 960px; margin: 20px auto; color: #333; background-color: #fdfdfd; }
        h1, h2, h3, h4, h5, h6 { color: #0056b3; margin-top: 1.8em; margin-bottom: 0.8em; border-bottom: 1px solid #eee; padding-bottom: 6px; }
        h1 { font-size: 2.2em; }
        h2 { font-size: 1.8em; }
        h3 { font-size: 1.4em; border-bottom: none; }
        h4 { font-size: 1.1em; color: #333; border-bottom: none; }
        pre { background-color: #f5f5f5; border: 1px solid #ddd; border-radius: 4px; padding: 15px; overflow: auto; font-family: Consolas, 'Courier New', monospace; font-size: 0.9em; }
        code:not(pre > code) { background-color: #eee; padding: 0.2em 0.4em; border-radius: 3px; font-family: Consolas, 'Courier New', monospace; font-size: 0.9em;}
        pre > code { background-color: transparent; padding: 0; font-size: 1em; border: none; } /* Reset style for code inside pre */
        table { border-collapse: collapse; width: 100%; margin-bottom: 1.5em; border: 1px solid #ccc; }
        th, td { border: 1px solid #ccc; padding: 10px 12px; text-align: left; }
        th { background-color: #f2f2f2; font-weight: bold; }
        tr:nth-child(even) { background-color: #f9f9f9; }
        ul, ol { margin-bottom: 1em; padding-left: 2em; }
        li { margin-bottom: 0.6em; }
        blockquote { border-left: 5px solid #ccc; padding: 10px 20px; margin: 1.5em 0; color: #555; background-color: #f9f9f9; }
        a { color: #0066cc; text-decoration: none; }
        a:hover { text-decoration: underline; }
        hr { border: none; border-top: 1px solid #eee; margin: 2em 0; }
        /* Basic styles for codehilite if markdown library uses it */
        .codehilite pre { margin: 0; }
        .codehilite .hll { background-color: #ffffcc }
        /* Add more specific codehilite theme styles here if needed */
    </style>
    """

    try:
        if MARKDOWN_AVAILABLE:
            # Use markdown library with extensions for tables, code blocks, etc.
            html_content = markdown.markdown(
                md_text,
                extensions=['tables', 'fenced_code', 'codehilite', 'md_in_html', 'nl2br', 'toc'] # toc for table of contents
                # Add 'codehilite' specific configs here if needed, e.g., css_class='highlight'
            )
        else:
             # Basic fallback: wrap in <pre> tag
            html_content = f"<pre>{md_text}</pre>"

        # Combine into full HTML document
        styled_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    {html_style}
</head>
<body>
    <h1>{title}</h1>
    {html_content}
</body>
</html>"""

        # Save the HTML file
        with open(output_html_path, 'w', encoding='utf-8') as f:
            f.write(styled_html)
        print(f"   📄 HTML file generated: {output_html_path}")
        return True

    except Exception as e:
        print(f"❌ Error creating HTML file {output_html_path}: {e}")
        # Fallback: Save raw markdown if HTML fails
        fallback_md_path = output_html_path.replace(".html", "_error.md")
        try:
             with open(fallback_md_path, "w", encoding='utf-8') as f:
                 f.write(md_text)
             print(f"   ⚠️ Saved raw markdown to {fallback_md_path} due to HTML conversion error.")
        except Exception as fe:
             print(f"   ❌ Also failed to save raw markdown fallback: {fe}")
        return False


# === Main Execution Pipeline ===
if __name__ == "__main__":
    print(f"🚀 Starting Tech Spec Generation Pipeline @ {__file__}")
    # Use the standard datetime module instead of a non-existent fitz function
    from datetime import datetime
    print(f"--- Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---")

    # --- Step 1: Extract PRD Text ---
    print("\n📄 Step 1: Extracting text from PRD...")
    prd_text = extract_pdf_text(INPUT_PATH)
    if not prd_text:
        print("❌ Pipeline halted: Could not extract text from PRD.")
        sys.exit(1) # Exit script if input fails

    # --- Step 2: Analyze PRD ---
    print("\n🧠 Step 2: Analyzing PRD text via LLM...")
    structured_info = analyze_prd(prd_text)
    structured_output_path = os.path.join(OUTPUT_FOLDER, "1_prd_analysis.json")
    # Save analysis regardless of errors for debugging, but check for errors before proceeding
    try:
        with open(structured_output_path, "w", encoding="utf-8") as f:
            json.dump(structured_info, f, indent=2, ensure_ascii=False)
        print(f"   ✅ Structured PRD analysis saved to: {structured_output_path}")
    except Exception as e:
         print(f"   ⚠️ Error saving PRD analysis JSON: {e}")

    if "error" in structured_info:
        print(f"❌ Pipeline halted: Failed to analyze PRD - {structured_info.get('error', 'Unknown analysis error')}")
        if "raw_content" in structured_info and structured_info["raw_content"]:
             print(f"   Raw LLM Response Snippet: {structured_info['raw_content'][:500]}...")
        sys.exit(1)

    # --- Step 3: Load Repo Context ---
    print("\n📚 Step 3: Loading repository context...")
    repo_context = load_repo_context(REPO_PATH)
    # Optional: Save summary for debugging
    # repo_summary_path = os.path.join(OUTPUT_FOLDER, "repo_context_summary.json")
    # with open(repo_summary_path, "w", encoding="utf-8") as f: json.dump(repo_context, f, indent=2)

    # --- Step 3.5: Load Spec Examples (PDF) ---
    print("\n✨ Step 3.5: Loading tech spec examples (PDF)...")
    spec_examples = load_spec_examples(SPEC_EXAMPLES_PATH)
    if not spec_examples.get("good") and not spec_examples.get("bad"):
        print("   ⚠️ Proceeding without good or bad spec examples.")

    # --- Step 4: Plan Architecture ---
    print("\n🧱 Step 4: Planning architecture via LLM...")
    architecture_plan = plan_architecture(structured_info, repo_context)
    architecture_plan_path = os.path.join(OUTPUT_FOLDER, "2_architecture_plan.md")
    try:
        with open(architecture_plan_path, "w", encoding="utf-8") as f:
            f.write(architecture_plan)
        print(f"   ✅ Architecture plan saved to: {architecture_plan_path}")
    except Exception as e:
         print(f"   ⚠️ Error saving architecture plan: {e}")

    if architecture_plan.startswith("Error:"):
         print(f"❌ Pipeline halted: Failed to plan architecture.")
         # Error message is already in the variable
         sys.exit(1)

    # --- Step 5: Generate Tech Spec Draft ---
    print("\n📝 Step 5: Generating initial tech spec draft via LLM...")
    tech_spec_draft = generate_tech_spec_draft(architecture_plan, GUIDELINE_PATH)
    draft_spec_md_path = os.path.join(OUTPUT_FOLDER, "3_tech_spec_draft.md")
    draft_spec_html_path = os.path.join(OUTPUT_FOLDER, "3_tech_spec_draft.html")
    draft_html_success = False
    try:
        with open(draft_spec_md_path, "w", encoding="utf-8") as f:
            f.write(tech_spec_draft)
        print(f"   ✅ Tech spec draft (Markdown) saved to: {draft_spec_md_path}")
        # Try generating HTML for the draft
        if not tech_spec_draft.startswith("Error:"):
            draft_html_success = markdown_to_html(tech_spec_draft, draft_spec_html_path)
    except Exception as e:
         print(f"   ⚠️ Error saving tech spec draft Markdown: {e}")

    if tech_spec_draft.startswith("Error:"):
         print(f"❌ Pipeline halted: Failed to generate tech spec draft.")
         sys.exit(1)

    # --- Step 6: Review Tech Spec Draft ---
    print("\n🔍 Step 6: Reviewing tech spec draft via LLM...")
    tech_spec_review = review_tech_spec(
        tech_spec_draft,
        TECH_SPEC_REVIEW_GUIDELINE_PATH,
        spec_examples.get("good"), # Pass potentially None values
        spec_examples.get("bad")
    )
    review_md_path = os.path.join(OUTPUT_FOLDER, "4_tech_spec_review.md")
    review_html_path = os.path.join(OUTPUT_FOLDER, "4_tech_spec_review.html")
    review_generated = False
    review_html_success = False

    if not tech_spec_review.startswith("Error:"):
        review_generated = True
        try:
            with open(review_md_path, "w", encoding="utf-8") as f:
                f.write(tech_spec_review)
            print(f"   ✅ Tech spec review (Markdown) saved to: {review_md_path}")
            # Try generating HTML for the review
            review_html_success = markdown_to_html(tech_spec_review, review_html_path)
        except Exception as e:
             print(f"   ⚠️ Error saving tech spec review Markdown: {e}")
    else:
         print(f"⚠️ Failed to generate tech spec review.")
         print(f"   Reason: {tech_spec_review}")
         # Save the error message itself as the review file for debugging
         try:
             with open(review_md_path, "w", encoding="utf-8") as f:
                f.write(f"# Tech Spec Review Generation Failed\n\nReason:\n{tech_spec_review}")
         except: pass # Ignore error saving the error message

    # --- Final Output and Browser Opening ---
    print("\n🎉 Pipeline execution finished!")
    print(f"   Output files are located in: {os.path.abspath(OUTPUT_FOLDER)}")
    print("-" * 40)
    print(f"   - PRD Analysis:        {os.path.basename(structured_output_path)}")
    print(f"   - Architecture Plan:   {os.path.basename(architecture_plan_path)}")
    print(f"   - Tech Spec Draft MD:  {os.path.basename(draft_spec_md_path)}")
    if draft_html_success:
        print(f"   - Tech Spec Draft HTML: {os.path.basename(draft_spec_html_path)}")
    if review_generated:
        print(f"   - Tech Spec Review MD:   {os.path.basename(review_md_path)}")
        if review_html_success:
            print(f"   - Tech Spec Review HTML:  {os.path.basename(review_html_path)}")
    else:
        print(f"   - Tech Spec Review:    Failed to generate.")
    print("-" * 40)

    # Determine which HTML file to open (prefer review, fallback to draft)
    file_to_open = None
    if review_generated and review_html_success:
        file_to_open = review_html_path
        print("\nAttempting to open the Tech Spec Review HTML in your browser...")
    elif draft_html_success:
        file_to_open = draft_spec_html_path
        print("\nReview HTML not available, attempting to open the Tech Spec Draft HTML...")
    else:
        print("\nNo suitable HTML output available to open in browser.")
        print(f"Please check the Markdown files in: {os.path.abspath(OUTPUT_FOLDER)}")

    if file_to_open:
        try:
            # Use file:// URI scheme for local files
            webbrowser.open(f"file://{os.path.abspath(file_to_open)}")
            print(f"   Opened (or attempted to open): {os.path.abspath(file_to_open)}")
        except Exception as e:
            print(f"\n⚠️ Could not automatically open browser: {e}")
            print(f"   Please open the file manually: {os.path.abspath(file_to_open)}")

    print("\n✅ Script finished.")