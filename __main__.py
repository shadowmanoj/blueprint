import os
import fitz  # PyMuPDF
import json
from langchain.chat_models import ChatOpenAI

# CONFIG
INPUT_PATH = "input_docs/dcc_prd.pdf"
REPO_PATH = "repo"
GUIDELINE_PATH = "guidelines/spec_guidelines.txt"
OUTPUT_FOLDER = "outputs"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


OPENAI_API_KEY = "2RUOScQCo243qls9wgMaPBjwZ5LH3GENFPKjwTOkLZDPKm5Wh0icJQQJ99BDAC77bzfXJ3w3AAABACOGjxKB"
OPENAI_API_BASE = "https://fy26-hackon-q1.openai.azure.com/openai/deployments/Blueprint/chat/completions?api-version=2025-01-01-preview"

llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0.3,
    openai_api_key=OPENAI_API_KEY,
    openai_api_base=OPENAI_API_BASE
)

# Step 1: Extract text from PRD PDF
def extract_pdf_text(file_path):
    with fitz.open(file_path) as doc:
        return "\n".join(page.get_text() for page in doc)

# Step 2: Analyze PRD → Structured Info (features, APIs, goals)
def analyze_prd(prd_text):
    system_instruction = (
        "You are a product requirements document (PRD) analyzer. "
        "Extract the domain/business context, list of features, engineering goals, and any relevant APIs. "
        "Output only JSON with the following keys: domain, features, goals, apis"
    )
    response = llm.predict(messages=[
        {"role": "system", "content": system_instruction},
        {"role": "user", "content": prd_text}
    ])
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        return {"error": "Invalid JSON response", "raw": response}

# Step 3: Read codebase context from /repo folder
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

# Step 4: Planner Agent → Suggest system architecture
def plan_architecture(extracted_info, repo_context):
    feature_text = "\n".join(f"- {f}" for f in extracted_info.get("features", []))
    repo_summary = "\n".join([f"{k}: {v[:300]}..." for k, v in repo_context.items()])

    system_instruction = (
        "You are a codebase-aware planner agent. Given the list of features and context from the codebase, "
        "map features to existing services (if possible), and suggest new services if needed. "
        "Return a high-level system architecture plan in Markdown format."
    )

    response = llm.predict(messages=[
        {"role": "system", "content": system_instruction},
        {"role": "user", "content": f"Features:\n{feature_text}\n\nRepo Context:\n{repo_summary}"}
    ])
    return response

# Step 5: Generate tech spec using guidelines
def generate_tech_spec(architecture_plan, guideline_path):
    with open(guideline_path, "r") as f:
        guidelines = f.read()

    system_instruction = (
        "You are a technical specification writer. Use the architecture plan and the internal spec guidelines "
        "to generate a complete technical spec in structured Markdown format."
    )

    response = llm.predict(messages=[
        {"role": "system", "content": system_instruction},
        {"role": "user", "content": f"Architecture Plan:\n{architecture_plan}\n\nGuidelines:\n{guidelines}"}
    ])
    return response


# Main pipeline
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