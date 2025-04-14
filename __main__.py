import os
import fitz  # PyMuPDF
import json
import webbrowser  # Add this import
from openai import AzureOpenAI
from fpdf import FPDF
import re

# CONFIG
INPUT_PATH = "input_docs/dcc_prd.pdf"
REPO_PATH = "repo"
GUIDELINE_PATH = "guidelines/spec_guidelines.md"
OUTPUT_FOLDER = "outputs"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

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
    with fitz.open(file_path) as doc:
        return "\n".join(page.get_text() for page in doc)

# Step 2: Analyze PRD → Structured Info
def analyze_prd(prd_text):
    print(f"Starting PRD analysis with text length: {len(prd_text)} characters")
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
            
        print(f"Successfully parsed LLM response into JSON")
        print(json.dumps(result, indent=2))
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

def markdown_to_pdf(md_text, output_pdf_path):
    # Convert to PDF using FPDF2
    try:
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        
        # Set default font
        pdf.set_font("Helvetica", size=12)
        
        # Process markdown line by line
        for line in md_text.split('\n'):
            # Skip empty lines but add space
            if not line.strip():
                pdf.ln(5)
                continue
            
            # Clean line - replace any non-ASCII characters
            clean_line = ""
            for char in line:
                if ord(char) < 128:  # ASCII range
                    clean_line += char
                # Replace specific Unicode characters with ASCII equivalents
                elif char == '•':
                    clean_line += '-'  # Use hyphen instead of bullet
                elif char == '–' or char == '—':
                    clean_line += '-'  # Use normal hyphen for dashes
                elif char == '"' or char == '"':
                    clean_line += '"'  # Use straight quotes
                elif char == ''' or char == ''':
                    clean_line += "'"  # Use straight apostrophe
                elif char == '…':
                    clean_line += '...'  # Use three dots instead of ellipsis
                else:
                    clean_line += ' '  # Replace any other Unicode with space
            
            # Handle Markdown formatting
            if clean_line.startswith('# '):
                # H1 - Title
                pdf.set_font("Helvetica", 'B', 24)
                pdf.multi_cell(0, 12, text=clean_line[2:])
                pdf.ln(10)
                pdf.set_font("Helvetica", size=12)
            
            elif clean_line.startswith('## '):
                # H2 - Section
                pdf.set_font("Helvetica", 'B', 18)
                pdf.multi_cell(0, 10, text=clean_line[3:])
                pdf.ln(8)
                pdf.set_font("Helvetica", size=12)
            
            elif clean_line.startswith('### '):
                # H3 - Subsection
                pdf.set_font("Helvetica", 'B', 14)
                pdf.multi_cell(0, 10, text=clean_line[4:])
                pdf.ln(6)
                pdf.set_font("Helvetica", size=12)
            
            # Handle bullet points
            elif clean_line.startswith('- ') or clean_line.startswith('* '):
                pdf.set_font("Helvetica", size=12)
                # Use plain hyphen instead of bullet
                pdf.cell(5, 10, text="-")
                pdf.multi_cell(0, 10, text=clean_line[2:])
                pdf.ln(2)
            
            # Regular text
            else:
                pdf.set_font("Helvetica", size=12)
                pdf.multi_cell(0, 10, text=clean_line)
                pdf.ln(2)
        
        pdf.output(output_pdf_path)
        print(f"✅ PDF created successfully at: {output_pdf_path}")
        return True
        
    except Exception as e:
        print(f"❌ PDF creation error: {e}")
        
        # If PDF creation fails, save as text file
        text_path = output_pdf_path.replace('.pdf', '.txt')
        with open(text_path, 'w', encoding='utf-8') as f:
            f.write(md_text)
        print(f"✅ Saved content as text file instead: {text_path}")
        return False

# 🔁 Main pipeline
if __name__ == "__main__":
    print("🔍 Step 1: Extracting PRD...")
    prd_text = extract_pdf_text(INPUT_PATH)

    print("🧠 Step 2: Analyzing PRD...")
    structured = analyze_prd(prd_text)
    with open(os.path.join(OUTPUT_FOLDER, "structured_output.json"), "w") as f:
        json.dump(structured, f, indent=2)

    print("📚 Step 3: Loading repo context...")
    repo_context = load_repo_context(REPO_PATH)

    print("🧱 Step 4: Planning architecture...")
    plan = plan_architecture(structured, repo_context)
    with open(os.path.join(OUTPUT_FOLDER, "architecture_plan.md"), "w") as f:
        f.write(plan)

    print("📝 Step 5: Generating tech spec...")
    spec = generate_tech_spec(plan, GUIDELINE_PATH)
    with open(os.path.join(OUTPUT_FOLDER, "final_spec.md"), "w") as f:
        f.write(spec)

    # Generate PDF from spec markdown
    final_pdf_path = os.path.join(OUTPUT_FOLDER, "final_spec.pdf")
    success = markdown_to_pdf(spec, final_pdf_path)

    if success:
        print(f"📄 PDF created at: {final_pdf_path}")
        # Open the PDF in browser
        webbrowser.open(f"file://{os.path.abspath(final_pdf_path)}")
    else:
        # If PDF creation failed, open the text version
        final_txt_path = final_pdf_path.replace('.pdf', '.txt')
        print(f"📄 Text file created at: {final_txt_path}")
        webbrowser.open(f"file://{os.path.abspath(final_txt_path)}")

    print("🎉 Pipeline complete! Check your browser to view the output.")
