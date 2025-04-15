import os
import json
import webbrowser
import argparse
import sys
import subprocess

def check_install_dependencies():
    """Check and install required dependencies"""
    print("🔍 Checking dependencies...")
    required_packages = ["pymupdf", "markdown"]
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
        except ImportError:
            print(f"📦 Installing {package}...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
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
SPEC_EXAMPLES_PATH = "spec_examples"  # Add this path for spec examples

# ✅ Create shared LLM instance
OPENAI_API_KEY = "2RUOScQCo243qls9wgMaPBjwZ5LH3GENFPKjwTOkLZDPKm5Wh0icJQQJ99BDAC77bzfXJ3w3AAABACOGjxKB"  # keep this secret
AZURE_ENDPOINT = "https://fy26-hackon-q1.openai.azure.com"
AZURE_DEPLOYMENT = "blueprint-gpt4"
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

# Load spec examples (good and bad)
def load_spec_examples(examples_path):
    """Loads good and bad tech spec examples from PDF files using extract_pdf_text."""
    examples = {"good": None, "bad": None}
    # Define paths for expected PDF files
    good_pdf_path = os.path.join(examples_path, "good_spec_example.pdf")
    bad_pdf_path = os.path.join(examples_path, "bad_spec_example.pdf")

    # Check if the examples directory exists
    if not os.path.isdir(examples_path):
        print(f"⚠️ Spec examples directory '{examples_path}' not found.")
        return examples # Return defaults (None)

    # --- Load Good Example PDF ---
    if os.path.exists(good_pdf_path):
        extracted_text = extract_pdf_text(good_pdf_path) # Reuse PDF extractor
        if extracted_text:
            examples["good"] = extracted_text
        else:
            print(f"⚠️ Failed to extract text from good spec PDF: {good_pdf_path}")
    else:
        print(f"⚠️ Good spec example PDF file not found: {good_pdf_path}")

    # --- Load Bad Example PDF ---
    if os.path.exists(bad_pdf_path):
        extracted_text = extract_pdf_text(bad_pdf_path) # Reuse PDF extractor
        if extracted_text:
            examples["bad"] = extracted_text
        else:
            print(f"⚠️ Failed to extract text from bad spec PDF: {bad_pdf_path}")
    else:
        print(f"⚠️ Bad spec example PDF file not found: {bad_pdf_path}")

    return examples

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
    "- NEVER recommend creation of new services or components unless absolutely impossible to implement within existing services\n"
    "- If proposing a new service is truly unavoidable, provide extensive justification explaining why existing services cannot be modified\n"
    "- Leverage and reference reusable utilities, workflows, contracts, and interfaces wherever possible\n"
    "- Extend existing services' responsibilities rather than creating new boundaries\n"
    "- Consider engineering constraints like service boundaries, data ownership, reliability, latency, and compliance\n"
    "- Reflect awareness of typical internal patterns (e.g. pub-sub via Kafka, gRPC/HTTP interfaces, internal SDKs)\n"
    "- Outline inter-service data flow if relevant\n"
    "- Keep in mind domain boundaries like Payments, Terminals, Risk, etc.\n\n"

    "Your output should be a high-level architecture plan in **Markdown** format with the following sections:\n"
    "1. Overview\n"
    "2. Feature-to-Service Mapping (MUST use existing services)\n"
    "3. Suggested Code Touchpoints (functions, packages, interfaces, or modules)\n"
    "4. New Components (RARELY NEEDED - only if absolutely necessary) with extensive justification\n"
    "5. Data Flow & Interfaces\n"
    "6. Risks and Considerations\n"
    )

    response = client.chat.completions.create(
        model=AZURE_DEPLOYMENT,
        messages=[
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": f"Features:\n{feature_text}\n\nRepo Context:\n{repo_summary}"}
        ],
        temperature=0.3,
    )
    
    return response.choices[0].message.content

# Step 5: Generate tech spec
def generate_tech_spec(architecture_plan, guideline_path, good_example_text=None, bad_example_text=None):
    with open(guideline_path, "r") as f:
        guidelines = f.read()

    # Add examples to the prompt if available
    example_prompt = ""
    if good_example_text:
        example_prompt += f"\n\n**GOOD SPEC EXAMPLE (Reference for Quality):**\nHere is a snippet of a good quality specification to emulate:\n```\n{good_example_text[:2000] if len(good_example_text) > 2000 else good_example_text}\n```"
    
    if bad_example_text:
        example_prompt += f"\n\n**BAD SPEC EXAMPLE (Patterns to Avoid):**\nHere is a snippet of issues to avoid in your specification:\n```\n{bad_example_text[:2000] if len(bad_example_text) > 2000 else bad_example_text}\n```"

    system_instruction = (
   "You are a Senior Principal Engineer with 20+ years of experience, responsible for drafting an EXTREMELY detailed and implementation-ready technical specification. "
    "This technical specification MUST be at the level of detail that would satisfy the most rigorous engineering review board. "
    "Your output WILL be directly used by engineers to implement the system without needing to ask any clarifying questions.\n\n"
    
    "CRITICAL REQUIREMENTS FOR YOUR OUTPUT:\n"
    "1. LENGTH AND DEPTH: Your specification MUST be at least 25-30 pages (15000-20000 words) of extremely detailed technical content\n"
    "2. CODE EXAMPLES: Include ACTUAL code snippets for critical components (30+ examples minimum)\n"
    "3. IMPLEMENTATION DETAILS: Provide exact function signatures, class definitions, and method calls\n"
    "4. INTERFACE DEFINITIONS: Include complete API contracts with request/response examples in JSON\n"
    "5. DATABASE SCHEMA: Provide complete database schema definitions with field types, indexes, and constraints\n"
    "6. SEQUENCE DIAGRAMS: Include detailed sequence diagrams in text format (using ASCII) for all main workflows\n"
    "7. DATA FLOW: Describe step-by-step data flow with specific function calls between services\n"
    "8. ERROR HANDLING: Define comprehensive error handling strategy with error codes and recovery mechanisms\n"
    "9. OBSERVABILITY: Include detailed logging, monitoring, and alerting specifications\n"
    "10. TESTING STRATEGY: Detail unit, integration, and load testing approaches with specific test cases\n\n"

    "EACH SECTION MUST BE EXTREMELY DETAILED:\n"
    "- Problem Statement: At least 1000 words with specific business impacts and technical challenges\n"
    "- Scope: Minimum 15 detailed bullet points with paragraph explanations for each\n"
    "- Architecture: Complete component diagram with every connection defined and justified\n"
    "- Data Models: Full database schema with field names, types, constraints, indexes, and relationships\n"
    "- API Contracts: Complete API specifications with endpoints, parameters, headers, status codes, and response formats\n"
    "- Implementation: Specific classes and functions to be created or modified with signatures\n"
    "- Rollout: Comprehensive plan with specific metrics, thresholds, and rollback triggers\n"
    "- Observability: Exact log formats, metrics names, and alert thresholds\n\n"
    
    "YOU MUST INCLUDE CLASS/FUNCTION DEFINITIONS: Your spec must include ACTUAL implementation details such as:\n"
    "```java\npublic class DccTransactionProcessor {\n  private ForexRateService forexService;\n  private TransactionRepository txRepo;\n  private MarkupCalculator markupCalc;\n\n  public DccTransactionProcessor(ForexRateService forexService, TransactionRepository txRepo, MarkupCalculator markupCalc) {\n    this.forexService = forexService;\n    this.txRepo = txRepo;\n    this.markupCalc = markupCalc;\n  }\n\n  public DccResult processDccTransaction(Transaction tx, Currency customerCurrency) {\n    // Implementation logic here with detailed steps\n    ForexRate rate = forexService.getLatestRate(tx.getMerchantCurrency(), customerCurrency);\n    // More implementation logic\n    return new DccResult(/* full constructor with all fields */);\n  }\n}\n```\n\n"
    
    "YOU MUST INCLUDE API CONTRACTS: Provide EXACT request/response formats such as:\n"
    "```json\n// POST /api/v1/dcc/calculate\n// Request Headers\n// Content-Type: application/json\n// Authorization: Bearer <token>\n// Request\n{\n  \"amount\": 100.00,\n  \"baseCurrency\": \"INR\",\n  \"targetCurrency\": \"USD\",\n  \"merchantId\": \"mrc_123456789\",\n  \"transactionContext\": {\n    \"channelType\": \"online|offline\",\n    \"terminalId\": \"term_123456\",\n    \"requestTimestamp\": \"2023-04-15T11:55:00Z\"\n  }\n}\n\n// Response\n// Status: 200 OK\n{\n  \"convertedAmount\": 1.35,\n  \"exchangeRate\": 0.0135,\n  \"markupPercentage\": 3.5,\n  \"markupAmount\": 0.05,\n  \"totalConvertedAmount\": 1.40,\n  \"expiresAt\": \"2023-04-15T12:00:00Z\",\n  \"requestId\": \"req_abcdef123456\",\n  \"metadata\": {\n    \"rateSource\": \"real-time|cached\",\n    \"rateTimestamp\": \"2023-04-15T11:54:30Z\"\n  }\n}\n\n// Error Response\n// Status: 400 Bad Request\n{\n  \"error\": {\n    \"code\": \"INVALID_CURRENCY\",\n    \"message\": \"The specified target currency is not supported\",\n    \"requestId\": \"req_abcdef123456\"\n  }\n}\n```\n\n"
    
    "YOU MUST INCLUDE DATABASE SCHEMAS: Define exact schema definitions such as:\n"
    "```sql\nCREATE TABLE dcc_transactions (\n  transaction_id VARCHAR(36) PRIMARY KEY,\n  merchant_id VARCHAR(36) NOT NULL,\n  base_amount DECIMAL(20,6) NOT NULL,\n  base_currency VARCHAR(3) NOT NULL,\n  converted_amount DECIMAL(20,6) NOT NULL,\n  target_currency VARCHAR(3) NOT NULL,\n  exchange_rate DECIMAL(20,6) NOT NULL,\n  markup_percentage DECIMAL(5,2) NOT NULL,\n  markup_amount DECIMAL(20,6) NOT NULL,\n  total_converted_amount DECIMAL(20,6) NOT NULL,\n  rate_source ENUM('real-time', 'cached') NOT NULL,\n  rate_timestamp TIMESTAMP NOT NULL,\n  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,\n  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,\n  channel_type ENUM('online', 'offline') NOT NULL,\n  terminal_id VARCHAR(36),\n  request_id VARCHAR(36) NOT NULL,\n  PRIMARY KEY (transaction_id),\n  INDEX idx_merchant_id (merchant_id),\n  INDEX idx_created_at (created_at),\n  INDEX idx_request_id (request_id)\n);\n\nCREATE TABLE forex_rates (\n  id BIGINT AUTO_INCREMENT PRIMARY KEY,\n  base_currency VARCHAR(3) NOT NULL,\n  target_currency VARCHAR(3) NOT NULL,\n  rate DECIMAL(20,10) NOT NULL,\n  source_api VARCHAR(100) NOT NULL,\n  fetched_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,\n  expires_at TIMESTAMP NOT NULL,\n  is_active BOOLEAN NOT NULL DEFAULT TRUE,\n  INDEX idx_currency_pair (base_currency, target_currency),\n  INDEX idx_expires_at (expires_at)\n);\n```\n\n"

    "The final spec must read like it was written by an expert who has intimate knowledge of the codebase and has already thought through every implementation detail. It must be so specific and comprehensive that any engineer could implement the system directly from this specification without asking questions.\n\n"

    "EXTREMELY IMPORTANT: You MUST include detailed sections for ALL 15 points in the template, especially the often overlooked sections: Traffic Estimates, System Stability Plan, Open Questions, Migration Experience, Future Enhancements, and Pre/Post Migration Comparison. Each of these sections should be comprehensive with specific metrics, strategies, and considerations.\n\n"

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

    # Ensure the guidelines include a strong emphasis on implementation details
    enhanced_guidelines = guidelines + "\n\nEMPHASIS: This technical specification should include ACTUAL implementation details such as concrete class/method definitions, database schema definitions with SQL DDL statements, and complete API contracts with JSON examples for request/response payloads. Engineers should be able to implement directly from this document without additional clarification." + example_prompt

    response = client.chat.completions.create(
        model=AZURE_DEPLOYMENT,
        messages=[
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": f"Architecture Plan:\n{architecture_plan}\n\nGuidelines:\n{enhanced_guidelines}"}
        ],
        temperature=0.2,  # Lower temperature for more consistent technical details
        max_tokens=4096     # Increased token limit to maximum value
    )
    
    return response.choices[0].message.content

def analyze_tech_spec(tech_spec_text):
    system_instruction = (
        "You are an expert technical spec analyzer. Your job is to extract comprehensive structured insights from a technical specification document. "
        "Parse and summarize the document into the following keys in JSON format: "
        "1. 'domain' - the problem space and business context in exceptional detail, "
        "2. 'features' - a comprehensive list of user-facing or backend features mentioned with detailed descriptions, "
        "3. 'goals' - detailed engineering or design objectives stated in the spec with concrete acceptance criteria, "
        "4. 'apis' - a complete list of any public-facing or internal APIs referenced or proposed with endpoints, methods, parameters, and response formats, "
        "5. 'architecture' - key architectural components and their relationships with diagrams, "
        "6. 'data_models' - detailed data structures and schemas with field types and relationships, "
        "7. 'implementation_stages' - the planned implementation phases and timeline with dependencies, "
        "8. 'risks' - identified risks and concrete mitigation strategies with contingency plans, "
        "9. 'performance_considerations' - details about throughput, latency requirements, and scaling strategies, "
        "10. 'observability' - monitoring, logging, and alerting approaches with specific metrics. "
        "Return only a valid JSON object with these keys. Be thorough and detailed, extracting as much information as possible from the specification."
    )
    response = client.chat.completions.create(
        model=AZURE_DEPLOYMENT,
        messages=[
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": tech_spec_text}
        ],
        temperature=0.3,
    )
    try:
        return json.loads(response.choices[0].message.content)
    except json.JSONDecodeError:
        return {"error": "Invalid JSON", "raw": response.choices[0].message.content}
    
def tech_spec_plan_architecture(extracted_info, repo_context):
    feature_text = "\n".join(f"- {f}" for f in extracted_info.get("features", []))
    repo_summary = "\n".join([f"{k}: {v[:300]}..." for k, v in repo_context.items()])
    
    # Create more detailed feature descriptions if additional details are available
    if isinstance(extracted_info.get("features"), list) and all(isinstance(i, dict) for i in extracted_info.get("features", [])):
        feature_text = "\n".join([f"- {f.get('name', 'Feature')}: {f.get('description', '')}" for f in extracted_info.get("features", [])])
    
    system_instruction = (
        "You are a Principal Systems Architect with 25+ years of experience. Given the extracted features and the current codebase context, "
        "create a comprehensive and extremely detailed architecture plan. Your plan should: "
        "1. Map each feature to existing services with specific code touchpoints where possible - NEVER create new services unless absolutely impossible to implement within existing ones "
        "2. Only propose new services/components when there is absolutely no way to implement within existing services - provide extensive justification if you must propose a new service "
        "3. Create a detailed component diagram (described in text format) showing all relationships "
        "4. Specify the exact data flow between components with sequence diagrams (in text) "
        "5. Identify specific libraries, frameworks, and technologies to use with version numbers "
        "6. Include a detailed implementation roadmap with dependencies and timelines "
        "7. Address potential bottlenecks, scaling considerations, and high availability strategies "
        "8. Include capacity planning with specific metrics and thresholds "
        "9. Detail caching strategies, database indices, and query optimization approaches "
        "10. Specify deployment architecture including infrastructure requirements "
        "11. Include security considerations and data protection strategies "
        "12. Detail monitoring and observability approaches with specific tools and metrics "
        "CRITICAL INSTRUCTION: Your architecture MUST be based on extending EXISTING services from the repository context. Do NOT propose new services unless it's absolutely impossible to implement the feature within the existing architecture. If you MUST propose a new service, you need to provide extensive justification explaining why existing services cannot be modified to accommodate the feature."
        "Return a comprehensive, high-level system architecture plan in **Markdown format** (minimum 6000 words)."
    )
    response = client.chat.completions.create(
        model=AZURE_DEPLOYMENT,
        messages=[
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": f"Features:\n{feature_text}\n\nRepo Context:\n{repo_summary}"}
        ],
        temperature=0.3,
    )
    return response.choices[0].message.content

def review_tech_spec(architecture_plan, guideline_path, good_example_text=None, bad_example_text=None):
    with open(guideline_path, "r") as f:
        guidelines = f.read()
        
    system_instruction = (
        "You are a Distinguished Engineer with 30+ years of experience reviewing technical specifications. Given a system architecture plan and internal spec guidelines, "
        "compose a comprehensive, in-depth technical specification review in Markdown format. "
        "Your review should be extremely detailed (at least 8000 words) and include: "
        
        "1. Executive Summary - A high-level overview of the technical specification's strengths and weaknesses "
        "2. Architectural Assessment - Detailed analysis of the architecture with specific improvements "
        "3. Implementation Feasibility - Analysis of implementation challenges with recommended approaches "
        "4. Missing Elements - Identification of any critical components, edge cases, or considerations omitted "
        "5. Security & Compliance Review - Evaluation of security practices and compliance considerations "
        "6. Performance & Scalability Analysis - Assessment of performance implications and scaling strategies "
        "7. Alternative Approaches - Discussion of alternative designs with pros and cons "
        "8. Specific Code-Level Recommendations - Suggestions for implementation patterns and practices "
        "9. Testing Strategy Recommendations - Detailed approach for validation and quality assurance "
        "10. Detailed Feedback by Section - Line-by-line assessment of key sections with improvements "
        "11. Risk Assessment - Identification of potential project risks with mitigation strategies "
        "12. Operational Readiness - Analysis of operational considerations including monitoring and alerting "
        "13. Cost and Resource Analysis - Evaluation of implementation costs and resource requirements "
        "14. Timeline Assessment - Analysis of proposed timelines with recommendations "
        "15. Implementation Priorities - Suggested prioritization of features and components "
        
        "Ensure your review is actionable, specific, and provides concrete guidance for improving the spec. "
        "Use a professional tone, but don't hesitate to highlight critical issues that must be addressed. "
        "Format the output with clear sections, subsections, tables, and bullet points for readability. "
        "Your review should be thorough enough to substantially improve the quality of the final specification."
    )
    
    # Add examples to the prompt if available
    example_prompt = ""
    if good_example_text:
        example_prompt += f"\n\n**GOOD SPEC EXAMPLE (Reference for Quality):**\nHere is a snippet of a good quality specification to emulate:\n```\n{good_example_text[:2000] if len(good_example_text) > 2000 else good_example_text}\n```"
    
    if bad_example_text:
        example_prompt += f"\n\n**BAD SPEC EXAMPLE (Patterns to Avoid):**\nHere is a snippet of issues to avoid in your specification:\n```\n{bad_example_text[:2000] if len(bad_example_text) > 2000 else bad_example_text}\n```"

    response = client.chat.completions.create(
        model=AZURE_DEPLOYMENT,
        messages=[
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": f"Architecture Plan:\n{architecture_plan}\n\nGuidelines:\n{guidelines}\n\n{example_prompt}"}
        ],
        temperature=0.2,
        max_tokens=4096
    )
    
    return response.choices[0].message.content

def markdown_to_html(md_text, output_html_path):
    """Converts Markdown text to a styled HTML file."""
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
        return True
        
    except Exception as e:
        print(f"❌ Error creating HTML: {e}")
        return False

def open_output_file(file_path):
    """Helper function to open the output file in browser"""
    try:
        webbrowser.open(f"file://{os.path.abspath(file_path)}")
        print(f"🎉 Complete! Output available in browser.")
    except Exception as e:
        print(f"Could not open browser. Output available at: {file_path}")

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
        
    print(f"🔍 Step 1: Extracting PRD...")
    prd_text = extract_pdf_text(input_path)
    
    print("🧠 Step 2: Analyzing PRD...")
    structured = analyze_prd(prd_text)
    with open(os.path.join(OUTPUT_FOLDER, "structured_output.json"), "w") as f:
        json.dump(structured, f, indent=2)

    print("📚 Step 3: Loading repo context and examples...")
    repo_context = load_repo_context(repo_path)
    spec_examples = load_spec_examples(SPEC_EXAMPLES_PATH)

    print("🧱 Step 4: Planning architecture...")
    plan = plan_architecture(structured, repo_context)
    with open(os.path.join(OUTPUT_FOLDER, "architecture_plan.md"), "w") as f:
        f.write(plan)

    print("📝 Step 5: Generating tech spec...")
    spec = generate_tech_spec(
        plan, 
        guideline_path,
        good_example_text=spec_examples.get("good"),
        bad_example_text=spec_examples.get("bad")
    )

    # Generate outputs
    final_md_path = os.path.join(OUTPUT_FOLDER, "final_spec.md")
    final_html_path = os.path.join(OUTPUT_FOLDER, "final_spec.html")

    # Save the markdown
    with open(final_md_path, "w", encoding="utf-8") as f:
        f.write(spec)
    print(f"✅ Output saved at: {final_md_path}")

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
    
    print("📚 Loading spec examples and analyzing...")
    spec_examples = load_spec_examples(SPEC_EXAMPLES_PATH)
    
    print("🧠 Step 6: Analyzing tech spec...")
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
    spec_review = review_tech_spec(
        tech_spec_review_plan, 
        TECH_SPEC_REVIEW_GUIDELINE_PATH,
        good_example_text=spec_examples.get("good"),
        bad_example_text=spec_examples.get("bad")
    )
    
    # Save the review output
    review_md_path = os.path.join(OUTPUT_FOLDER, "review_spec.md")
    review_html_path = os.path.join(OUTPUT_FOLDER, "review_spec.html")
    
    with open(review_md_path, "w", encoding="utf-8") as f:
        f.write(spec_review)
    print(f"✅ Review saved at: {review_md_path}")
    
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