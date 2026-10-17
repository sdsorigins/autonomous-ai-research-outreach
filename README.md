# Autonomous AI Research and Outreach Assistant with 3D Chatbot

A genuinely agentic application built with **Python 3.11+**, **CrewAI**, the **Groq API**, **DuckDuckGo Search**, **ReportLab PDF Generator**, and an **Immersive 3D GSAP Frontend** with Three.js.

Features an autonomous multi-agent crew:
1. **Agent 1 — Autonomous Research Agent**: Discovers intelligence, formulates dynamic search queries, evaluates findings, and adapts search strategies.
2. **Agent 2 — Citations & Fact Verification Agent**: Rigorously audits every claim, maps canonical source URLs and citations (`[E1]`, `[E2]`), detects hallucinations, and calculates Grounding Confidence Scores.
3. **Agent 3 — Outreach & Executive Delivery Agent**: Composes personalized emails, compiles executive PDF briefs, and enforces Human-In-The-Loop approval before email dispatch.

---

## 🌐 Quick Start: Launch the 3D Chatbot Frontend

Launch the local interactive 3D web application:
```bash
python server.py
```
Open **[http://127.0.0.1:8000](http://127.0.0.1:8000)** in your browser to experience:
- **3D Neural Core Hologram** rendered in WebGL using **Three.js** with interactive mouse parallax and state morphing.
- **Cinematic GSAP Animations**: Smooth timelines for chat messages, live multi-agent steppers, and interactive card rollouts.
- **Instant PDF Generation**: Downloads an executive PDF brief with source citations and verified findings.
- **Customized Email Delivery**: Review and dispatch personalized emails with strict Human-In-The-Loop approval.

---

## 🏗️ Architecture & Agent Topology

The system deploys **exactly 2 autonomous agents** collaborating in one Crew:

```
                                  [ Research Objective ]
                                             │
                                             ▼
                        ┌─────────────────────────────────────────┐
                        │   Agent 1: Autonomous Research Agent    │
                        │   - Formulates dynamic search queries   │
                        │   - Observes & evaluates tool snippets  │
                        │   - Adapts queries if results ambiguous │
                        │   - Halts on sufficiency or limit       │
                        └────────────────────┬────────────────────┘
                                             │
                              [ Verified Evidence & Citations ]
                                             │
                                             ▼
                        ┌─────────────────────────────────────────┐
                        │   Agent 2: Intelligent Outreach Agent   │
                        │   - Evaluates recipient relevance       │
                        │   - Drafts grounded outreach emails     │
                        │   - Audits claims / flags hallucinations│
                        └──────────────┬──────────────────────────┘
                                       │
                ┌──────────────────────┴──────────────────────┐
                │                                             │
      [ If Essential Info Missing ]                [ When Draft Verified ]
                │                                             │
                ▼                                             ▼
     [ Dynamic Feedback Loop ]                    [ HITL Gmail Guard ]
     Requests targeted search                     User Review & Approval Gate
     from Agent 1                                 [Approve | Edit | Dry-Run | Reject]
                │                                             │
                └───────────────► Agent 1                     ▼
                                                    Gmail API / EML Export
```

### Agent 1 — Autonomous Research Agent
- **Role:** Autonomous Lead Research Investigator
- **Behavior:** Given an objective, independently selects search queries, calls web search tools, evaluates result quality, identifies information gaps, and decides whether to conduct follow-up searches.
- **Adaptive Strategy:** If a tool returns ambiguous or irrelevant results, the agent observes the deficiency, changes its strategy, and refines the query with technical/entity keywords.
- **Stopping Condition:** Terminates once sufficient verified evidence is registered in the ledger, or when a configurable iteration limit (`MAX_RESEARCH_ITERATIONS`) is reached.
- **Tools:** `WebSearchTool`, `EvidenceEvaluatorTool`.

### Agent 2 — Intelligent Outreach Agent
- **Role:** Strategic Outreach & Communications Specialist
- **Behavior:** Evaluates a user-provided contact list, selects suitable prospects with explicit rationale, filters out unqualified contacts, and composes personalized emails grounded in verified research.
- **Dynamic Feedback Loop:** If key information needed to pitch a prospect is missing, it calls `RequestMoreResearchTool`, causing the orchestrator to trigger Agent 1 for targeted queries before drafting.
- **Claim Verification & Grounding:** Audits drafted text using `ClaimVerifierTool` to detect and eliminate hallucinations or ungrounded assertions.
- **Human-In-The-Loop Approval:** Invokes `GmailOutreachTool` which halts for user confirmation before any message can be dispatched via Gmail API.

---

## 📁 Project Structure

```
agentic_ai/
├── .env.example               # Environment variables template
├── .gitignore                  # Git exclusions for Python & credentials
├── requirements.txt            # Python dependencies (CrewAI, Groq, Rich, etc.)
├── README.md                   # System documentation & usage guide
├── main.py                     # Interactive CLI entrypoint & menu system
├── data/
│   └── contacts.json           # Default contact dataset for evaluation
├── reports/                    # Exported audit ledgers (.json) and drafts (.eml)
├── src/
│   ├── __init__.py
│   ├── config.py               # Settings loader, Groq LLM initialization
│   ├── memory.py               # EvidenceLedger, EvidenceItem & AuditRecord
│   ├── agents.py               # CrewAI definitions for the 2 autonomous agents
│   ├── tasks.py                # Task definitions with observe-decide-act guidelines
│   ├── orchestrator.py         # CrewAI orchestrator & dynamic feedback loop
│   ├── demo.py                 # Self-contained tool adaptation demonstration
│   └── tools/
│       ├── __init__.py
│       ├── search_tool.py      # Live DuckDuckGo search with citation extraction
│       ├── evidence_tool.py    # Evidence registration, confidence & gap evaluation
│       ├── verification_tool.py# Claim verifier & research requester (feedback loop)
│       └── gmail_tool.py       # Gmail API integration with strict HITL approval
└── tests/
    ├── __init__.py
    ├── test_search_and_evidence.py
    ├── test_claim_verification.py
    ├── test_gmail_hitl.py
    └── test_agentic_loop.py
```

---

## 🚀 Setup & Installation

### 1. Prerequisites
- **Python 3.10 to 3.12** installed (or `uv`).
- Free **Groq API Key** from [console.groq.com](https://console.groq.com).

### 2. Virtual Environment Setup
```bash
# Clone or navigate to the directory
cd "c:\Users\sdsor\OneDrive\Desktop\agentic ai"

# Create a virtual environment using Python 3.11
python -m venv .venv

# Activate virtual environment
# Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# Windows CMD:
.\.venv\Scripts\activate.bat
# Linux / macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Configuration
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Edit `.env` with your settings:
```ini
# Groq API Key (free tier available at https://console.groq.com)
GROQ_API_KEY=gsk_your_groq_api_key_here

# Groq Model
GROQ_MODEL=groq/llama-3.3-70b-versatile

# Autonomous Research Bounds
MAX_RESEARCH_ITERATIONS=3
EVIDENCE_CONFIDENCE_THRESHOLD=0.75

# Optional Gmail API OAuth credentials
GMAIL_CREDENTIALS_PATH=credentials.json
GMAIL_TOKEN_PATH=token.json
```

---

## 🎬 Running the Application

### Option A: Interactive Menu (Recommended)
Launch the interactive terminal interface:
```bash
python main.py
```
This presents options to:
1. **Run Live Autonomous Crew** with live Groq inference and DuckDuckGo search.
2. **Run Step-by-Step Tool Adaptation Demonstration** (shows the agent changing actions based on tool output).
3. **Run Test Suite (`pytest`)**.
4. **Inspect Exported Audit Ledgers**.

### Option B: Direct CLI Execution
```bash
# Run the tool-adaptation demonstration directly
python main.py --demo

# Run live research with a specific objective
python main.py --objective "Investigate breakthroughs in agentic AI memory architectures 2026"

# Run with a custom contacts file
python main.py --objective "Acme AI enterprise benchmarks" --contacts data/contacts.json

# Non-interactive mode (auto dry-run for CI/scripts)
python main.py --demo --non-interactive
```

---

## 🔍 Demonstration: Agent Adapting Actions Based on Tool Results

The application includes an explicit demonstration (`python main.py --demo`) showcasing the agent's runtime adaptability:

1. **Initial Action:** Agent 1 queries `"Acme AI"`.
2. **Tool Output:** Returns ambiguous results mixed with cartoon Acme Corporation and generic product catalogs.
3. **Agent Observation & Decision:** Agent 1 observes that the output lacks technical relevance. Rather than continuing with a fixed prompt, it **adapts its strategy** and changes its next query to `"Acme AI enterprise latency reduction benchmarks 2026 Series B"`.
4. **Evidence Evaluation:** The adapted query yields high-confidence results ($45M Series B, 64% latency reduction). Agent 1 registers facts `[E1]` and `[E2]` in the `EvidenceLedger` and halts research.
5. **Contact Filtering:** Agent 2 selects the CTO and VP of Ops, while rejecting an unrelated fashion intern with explicit justification.
6. **Dynamic Feedback Loop:** Agent 2 detects missing CRM integration details for the VP of Ops, calls `RequestMoreResearchTool`, and Agent 1 executes a targeted search, storing `[E3]`.
7. **Hallucination Audit:** Agent 2 drafts the email, audits it with `ClaimVerifierTool`, detects an unsupported claim (*"Won 2026 Nobel Prize for Software Engineering"*), and purges it.
8. **HITL Gmail Approval:** The user is prompted to approve, edit, dry-run, or reject the email before any transmission occurs.

---

## 🛡️ Human-In-The-Loop (HITL) Email Policy

To prevent unauthorized email transmission:
- **Zero-Auto-Send Guarantee:** The `GmailOutreachTool` intercepts every dispatch attempt and renders an interactive terminal approval dialog.
- **Review Options:**
  - `[A]` **Approve & Send:** Dispatches live email via Gmail API.
  - `[E]` **Edit Draft:** Allows manual adjustment of subject and body in the terminal before sending.
  - `[D]` **Dry-Run / Save Local Draft:** Saves an `.eml` draft to `reports/draft_<name>.eml` for local review without sending.
  - `[R]` **Reject:** Immediately dismisses the outreach email.
- **Graceful Fallback:** If `credentials.json` is not present, the tool automatically operates in safe Dry-Run mode, allowing complete verification of email payloads without crashing.

### Configuring Gmail OAuth (Optional for Live Sending)
1. Go to [Google Cloud Console](https://console.cloud.google.com).
2. Create a project and enable the **Gmail API**.
3. Configure OAuth Consent Screen and create **OAuth Client ID** credentials (Desktop Application).
4. Download the JSON file as `credentials.json` in the project root.
5. On the first send, a browser tab will open for one-time OAuth approval, saving `token.json`.

---

## 📊 Source Citations & Audit Ledger

Every action, decision, tool invocation, and evidence item is tracked in runtime memory and exported to `reports/audit_ledger_<timestamp>.json`.

### Evidence Citation Format:
```
[E1] Acme AI raised $45M Series B led by Apex Capital.
   Source: Tech Chronicle (https://techchronicle.example.com/acme-45m-series-b)

[E2] Acme AI achieved 64% latency reduction in multi-agent orchestration.
   Source: Enterprise AI Benchmarks 2026 (https://benchmark-review.example.com/enterprise-ai-2026)
```

### Audit Ledger Fields:
- `iteration`: Step number within the bounded loop.
- `agent`: Agent responsible (`Autonomous Research Agent` or `Intelligent Outreach Agent`).
- `phase`: `OBSERVE`, `DECIDE`, `ACT`, `EVALUATE`, or `LOOPBACK`.
- `observation`: What the agent perceived from tool results or state.
- `decision`: Why the agent chose its next action.
- `tool_called`: Name and arguments of the tool executed.
- `tool_output_summary`: Result summary.
- `evaluation`: Assessment of sufficiency, gaps, or grounding.

---

## 🧪 Running Unit Tests

Execute the comprehensive test suite with `pytest`:
```bash
pytest tests/ -v
```

### Test Coverage:
- `test_search_and_evidence.py`: Validates DuckDuckGo search execution, citation extraction, and evidence ledger logging.
- `test_claim_verification.py`: Tests evidence grounding matching, hallucination detection, and research feedback loop triggering.
- `test_gmail_hitl.py`: Verifies that user rejection prevents email dispatch and dry-run drafts are persisted locally.
- `test_agentic_loop.py`: Verifies 2-agent initialization with tools, ledger audit recording, and JSON export.

---

## ⚠️ Error Handling & Resilience

- **Search Rate Limits & Errors:** `WebSearchTool` catches network exceptions and instructs the agent to reformulate queries or adjust keywords.
- **Missing API Keys:** If `GROQ_API_KEY` is not configured, `main.py` provides clear instructions and offers the interactive demonstration mode.
- **Ungrounded Claims:** `ClaimVerifierTool` flags any statements unsupported by evidence citations, preventing email dispatch until claims are resolved.
- **Windows Terminal Encodings:** Configures `sys.stdout` and `sys.stderr` to UTF-8 to prevent charmap encoding errors on Windows PowerShell.
