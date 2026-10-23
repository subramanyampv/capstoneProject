# Multi-Agent Customer Support System

A production-grade, framework-based (LangGraph & LangChain) customer support assistant featuring bounded specialist agents, semantic policy retrieval (RAG), deterministic safety enforcement, session memory, and reversible style adaptation.

---

## Quickstart Guide (Run from Scratch)

### 1. Environment Setup
```bash
# Create and activate a clean Python virtual environment (Python >= 3.10)
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies and verify environment
pip install -r requirements.txt
pip check
```

### 2. Configure Environment Variables
Copy the template and configure your OpenAI-compatible endpoint:
```bash
cp .env.example .env
```

Open `.env` and configure the 3 standard connection parameters:
```ini
LLM_BASE_URL="https://your-openai-compatible-endpoint/v1"
LLM_MODEL="your-model-name"
LLM_API_KEY="your-api-key"
```
*(Optional: For local mock servers that do not require an API key, `LLM_API_KEY` can be left blank).*

### 3. Ingest Policies into Vector Store
Index the raw policy documents into the local Chroma vector store (~5 seconds):
```bash
bash scripts/ingest.sh
```

### 4. Run the Support Desk UI
Launch the interactive Streamlit application:
```bash
bash scripts/run_ui.sh
```
Open **`http://127.0.0.1:8501`** in your browser.

### 5. Run Offline Test Suite
Verify system integrity with the offline test suite (runs 100% offline without network calls):
```bash
pytest -q
# Expected: 606 passed in ~45s
```

---

## Command Line Interface (CLI)

The application provides a unified CLI for one-shot questions, interactive chat, and diagnostic verification:

```bash
# 1. Ask a one-shot support question
python -m capstone_agent.main support "Can I return order O-1001?" --customer C-100

# 2. Interactive multi-turn chat session with memory
python -m capstone_agent.main support --chat --customer C-100

# 3. System diagnostic health check
python -m capstone_agent.main doctor

# 4. Search policy database directly
python -m capstone_agent.main search-policy "footwear return window"
```

---

## System Architecture

The core architecture uses a hierarchical **Supervisor + Specialist** topology built with **LangGraph**:

```
                       [ Customer Turn ]
                               │
                    [ Safety & PII Guards ]
                               │
                     [ Supervisor Agent ]
                               │
        ┌──────────────────────┼──────────────────────┐
        ▼                      ▼                      ▼
[ Order & Shipping ]   [ Policy & Product ]    [ Escalation ]
   (Order/Tracking)      (Vector RAG & Specs)   (Human Handoff)
        │                      │                      │
        └──────────────────────┼──────────────────────┘
                               ▼
               [ Obligation & Claim Auditor ]
                               ▼
                     [ Verified Response ]
```

- **Supervisor Agent (`SupervisorAgent`)**: Routes requests to domain specialists based on customer intent, enforcing context boundaries and preventing tool collisions.
- **Order & Shipping Specialist (`OrderShippingSpecialist`)**: Queries structured transactional databases (`lookup_order`, `get_tracking_events`, `calculate_delivery_estimate`) with server-side customer identity enforcement.
- **Policy & Product Specialist (`PolicyProductSpecialist`)**: Queries the versioned Chroma vector database (`PolicySearch`) for return, refund, shipping, and warranty rules, and extracts SKU catalog specifications.
- **Escalation Specialist (`EscalationSpecialist`)**: Enforces non-negotiable human escalation for physical injury complaints, policy conflicts, and refunds exceeding the $100 threshold, generating canonical mock tickets.

---

## Interactive Features & Verification

### Session Memory & Follow-Ups
In interactive chat (`--chat` or Streamlit):
1. Ask: *"Track order O-1001."* $\rightarrow$ Agent inspects tracking and provides status.
2. Ask: *"What about that order?"* $\rightarrow$ Resolves pronoun reference via `SessionMemory` without re-prompting for the order ID.
3. Type: `"/reset"` $\rightarrow$ Clears session projection.
4. Ask: *"What about that order?"* $\rightarrow$ Correctly asks for clarification because memory was cleared.

### Reversible Style Adaptation
Adjust response verbosity with rollback guarantees:
- Send: `"/feedback too_long"` twice $\rightarrow$ Style store switches verbosity to `concise` for subsequent answers.
- Send: `"/feedback reset_style"` $\rightarrow$ Restores standard verbosity.
- Send: `"/forget-preferences"` $\rightarrow$ Permanently deletes stored customer preference profiles.

---

## Project Structure

```
capstone_agent/
├── README.md                      # Quickstart and overview
├── pyproject.toml                 # Package definition
├── requirements.txt               # Pinned dependencies
├── streamlit_app.py               # Streamlit Support Desk UI
├── .env.example                   # Environment configuration template
├── src/capstone_agent/
│   ├── agents/                    # Modular specialist agents & supervisor
│   ├── support/                   # LangGraph orchestration, runtime & memory
│   ├── retrieval/                 # Chroma vector store, embeddings & search
│   └── safety/                    # PII redaction and claim boundary guards
├── data/                          # Synthetic order, tracking & catalog fixtures
├── knowledge/raw/                 # Source policy markdown documents
├── tests/                         # Unit, integration, safety & regression tests
└── docs/                          # Comprehensive technical documentation
```
