import os
import fitz  # PyMuPDF
import json
from openai import AzureOpenAI

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
    system_instruction = (
        "You are a product requirements document (PRD) analyzer. "
        "Extract the domain/business context, list of features, engineering goals, and any relevant APIs. "
        "Output only JSON with the following keys: domain, features, goals, apis"
    )
    
    response = client.chat.completions.create(
        model=AZURE_DEPLOYMENT,
        messages=[
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": prd_text}
        ],
        temperature=0.3
    )
    
    try:
        return json.loads(response.choices[0].message.content)
    except json.JSONDecodeError:
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
        "You are a codebase-aware planner agent. Given the list of features and context from the codebase, "
        "map features to existing services (if possible), and suggest new services if needed. "
        "Return a high-level system architecture plan in Markdown format."
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
        "You are a technical specification writer. Use the architecture plan and the internal spec guidelines "
        "to generate a complete technical spec in structured Markdown format."
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

    print("✅ All done! Outputs saved in the outputs/ folder.")
