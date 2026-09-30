

# 🕵️ Intelligent Research Copilot

> **AI-powered research & intelligence workspace for turning open-ended questions into structured, evidence-backed intelligence.**

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![SQLite](https://img.shields.io/badge/SQLite-Local%20Persistence-003B57?logo=sqlite)](https://www.sqlite.org/)
[![AI](https://img.shields.io/badge/AI-Gemini%20%7C%20Groq-purple)](#-ai-providers)
[![License](https://img.shields.io/badge/License-MIT-green)](#-license)

---

## ⚡ What is Intelligent Research Copilot?

**Intelligent Research Copilot** is a local-first AI research and intelligence workspace designed to transform a natural-language research request into an auditable research workflow.

Instead of simply generating a chatbot answer, the system can:

```text
RESEARCH QUESTION
       │
       ▼
┌──────────────────┐
│  RESEARCH PLANNER│
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ SOURCE DISCOVERY │
└────────┬─────────┘
         │
     ┌───┴──────────────┐
     ▼                  ▼
  WEB SOURCES       LOCAL FILES
     │                  │
     └───────┬──────────┘
             ▼
     ┌───────────────┐
     │ EVIDENCE      │
     │ COLLECTION    │
     └───────┬───────┘
             ▼
     ┌───────────────┐
     │ PROCESSING &  │
     │ VERIFICATION  │
     └───────┬───────┘
             ▼
     ┌───────────────┐
     │ STRUCTURED    │
     │ DATASET       │
     └───────┬───────┘
             ▼
     ┌────────────────┐
     │ INTELLIGENCE   │
     │ REPORT         │
     └───────┬────────┘
             ▼
     ┌─────────────────────┐
     │ SOURCES / EVIDENCE  │
     │ GRAPH / CSV / JSON   │
     └─────────────────────┘
```

The idea is simple:

> **Don't just generate an answer. Build a research trail.**

---

## ⚡ What makes it different from a normal chatbot?

A normal chatbot:

```text
Question
   ↓
LLM
   ↓
Answer
```

Intelligent Research Copilot:

```text
Question
   ↓
Plan
   ↓
Sub-questions
   ↓
Source Discovery
   ↓
Web / File Collection
   ↓
Evidence Extraction
   ↓
Processing
   ↓
Verification
   ↓
Deduplication
   ↓
Structured Dataset
   ↓
Report
   ↓
Knowledge Graph
```

The LLM is only one component of the system.

The actual product is the **research workflow around the model**.

---

## 🔎 Core Capabilities

### 🧠 Research Planner

Convert a natural-language request into a structured research plan.

The planner can define:

* research objectives
* sub-questions
* search queries
* source preferences
* deliverables
* verification requirements

---

### 🌐 Multi-Source Collection

The system can work with:

#### Web

* Explicit URLs
* Provider-native web grounding/search when available

#### Local research material

* PDF
* DOCX
* TXT
* Markdown
* CSV
* JSON
* LOG

---

### 🧾 Evidence & Provenance

Research findings can be connected to supporting evidence.

```text
CLAIM
  │
  ▼
EVIDENCE
  │
  ▼
SOURCE
  │
  ▼
RESEARCH RUN
```

This makes the research process easier to inspect and audit.

---

### 🧹 Data Processing

Research results can be transformed into structured information:

* entities
* relationships
* evidence
* confidence
* conflicts
* dataset rows
* limitations

---

### 🕸️ Knowledge Graph

Research relationships can be represented as connected entities.

Example:

```text
                    ┌──────────────┐
                    │   COMPANY    │
                    └──────┬───────┘
                           │
             ┌─────────────┼─────────────┐
             │             │             │
             ▼             ▼             ▼
          FOUNDER       PRODUCT       COUNTRY
             │             │             │
             ▼             ▼             ▼
           PERSON       SERVICE        REGION
```

---

### 📊 Structured Dataset

Instead of returning only paragraphs, research can produce structured data.

Example:

| Entity       | Category | Attribute    | Evidence | Confidence |
| ------------ | -------- | ------------ | -------- | ---------- |
| Example Corp | Company  | AI Security  | Source A | 0.91       |
| Example Labs | Company  | Threat Intel | Source B | 0.84       |

---

### 🕒 Research Activity Timeline

A research run can expose stages such as:

```text
START
  ↓
PLANNING
  ↓
DISCOVERY
  ↓
INGEST
  ↓
PROCESS
  ↓
VERIFY
  ↓
SYNTHESIZE
  ↓
COMPLETE
```

---

### 🗃️ Research History

Research runs are stored locally using SQLite.

Previous research can be inspected through the workspace.

---

### 📦 Export

Research results can be exported as:

```text
Markdown
CSV
JSON
```

---

## 🤖 AI Providers

The application supports:

* **Google Gemini**
* **Groq**

Provider and model selection is available from the application settings.

> Provider models and capabilities can change over time. Use the provider's current documentation when selecting models.

---

## 🏗️ Architecture

```text
┌──────────────────────────────────────────────┐
│                  FRONTEND                    │
│                                              │
│  Research Workspace                          │
│  Settings                                    │
│  Research History                            │
│  Evidence                                    │
│  Dataset                                     │
│  Knowledge Graph                             │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────┐
│                  FASTAPI                     │
│                                              │
│  Research API                                │
│  Provider API                                │
│  File Upload API                             │
│  Export API                                  │
└──────────────┬────────────────┬──────────────┘
               │                │
               ▼                ▼
       ┌─────────────┐   ┌──────────────┐
       │ RESEARCH    │   │ SCANNER      │
       │ AGENT       │   │              │
       │             │   │ URL Reader   │
       │ Planner     │   │ PDF Reader   │
       │ Workflow    │   │ DOCX Reader  │
       │ Synthesis   │   │ Text Parser  │
       └──────┬──────┘   └──────┬───────┘
              │                 │
              └────────┬────────┘
                       ▼
              ┌─────────────────┐
              │ EVIDENCE ENGINE │
              └────────┬────────┘
                       ▼
              ┌─────────────────┐
              │ SQLITE STORAGE  │
              └─────────────────┘
```

---

## 📁 Project Structure

```text
intelligent-research-copilot/
│
├── backend/
│   ├── main.py
│   ├── run.py
│   ├── requirements.txt
│   │
│   └── services/
│       ├── agent.py
│       ├── db.py
│       ├── providers.py
│       └── scanner.py
│
├── frontend/
│   ├── index.html
│   ├── app.js
│   └── styles.css
│
├── data/
├── storage/
├── tests/
│
├── .env.example
├── .gitignore
└── README.md
```

---

## 🚀 Installation — Windows PowerShell

### 1. Clone the repository

```powershell
git clone https://github.com/Iamhasan69/intelligent-research-copilot.git
```

```powershell
cd intelligent-research-copilot
```

---

### 2. Create virtual environment

```powershell
py -m venv .venv
```

---

### 3. Activate virtual environment

```powershell
Set-ExecutionPolicy -Scope Process Bypass
```

```powershell
.\.venv\Scripts\Activate.ps1
```

You should now see:

```text
(.venv)
```

---

### 4. Install dependencies

```powershell
python -m pip install --upgrade pip
```

```powershell
pip install -r backend\requirements.txt
```

---

## 🔐 Configure API Keys

Create your local `.env`:

```powershell
Copy-Item .env.example .env
```

Open it:

```powershell
notepad .env
```

Add your own keys:

```env
GEMINI_API_KEY=
GROQ_API_KEY=

HOST=127.0.0.1
PORT=8000
```

---

## ▶️ Start the Application

From the project root:

```powershell
python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

Then open:

```text
http://127.0.0.1:8000
```

---

## 🩺 Health Check

Open:

```text
http://127.0.0.1:8000/api/health
```

This should confirm that the backend is running.

---

## 🔬 Example Research

Try:

```text
Research Indian cybersecurity companies working on AI security.

For each company identify:

- company name
- product focus
- founders
- public funding information
- recent public activity

Prefer primary sources.
Attach evidence to important claims.
Deduplicate companies.
Flag conflicting information.
Return the result as structured data.
```

Expected workflow:

```text
QUESTION
   ↓
PLAN
   ↓
COLLECT
   ↓
PROCESS
   ↓
VERIFY
   ↓
STRUCTURE
   ↓
REPORT
```

---

## 🎯 Code Cubicle 6.0 — PS-01

The project is designed around the **AI-Powered Data Intelligence Platform** direction.

| PS-01 Requirement              | Implementation                  |
| ------------------------------ | ------------------------------- |
| Natural-language understanding | Research query                  |
| Dynamic workflow               | Research planning               |
| Multi-source collection        | Web + local files               |
| Data processing                | Extraction + structuring        |
| Validation                     | Evidence / conflict handling    |
| Traceability                   | Source / evidence relationships |
| Task monitoring                | Activity timeline               |
| Dashboard                      | Research workspace              |
| History                        | Research history                |
| Export                         | Markdown / CSV / JSON           |

---

## 🔒 Security Architecture

```text
Authentication
      ↓
Authorization
      ↓
Encrypted Secret Storage
      ↓
SSRF Protection
      ↓
DNS Rebinding Protection
      ↓
Rate Limiting
      ↓
Sandboxed Browser
      ↓
Background Workers
      ↓
Production Database
```

---

## ⚠️ Responsible Use

Use this project only for lawful and authorized research.

Do not use it to:

* access private systems without authorization
* bypass authentication
* collect restricted/private information
* conduct unauthorized surveillance
* attack systems
* violate applicable laws or service terms

Respect privacy, source licenses and applicable policies.

---

## 🛣️ Roadmap

### Current

* [x] Research workspace
* [x] Research planning
* [x] Gemini integration
* [x] Groq integration
* [x] URL ingestion
* [x] Document ingestion
* [x] Evidence storage
* [x] Research history
* [x] Structured dataset
* [x] Knowledge graph
* [x] Markdown export
* [x] CSV export
* [x] JSON export

### Future

* [ ] Source credibility scoring
* [ ] Claim-level verification
* [ ] Advanced entity resolution
* [ ] Contradiction analysis
* [ ] Semantic retrieval
* [ ] Vector database
* [ ] Browser automation sandbox
* [ ] Multi-agent research roles
* [ ] Authentication
* [ ] Encrypted secret storage
* [ ] Production deployment

---

## 🤝 Contributing

```powershell
git clone https://github.com/Iamhasan69/intelligent-research-copilot.git
cd intelligent-research-copilot

py -m venv .venv
.\.venv\Scripts\Activate.ps1

pip install -r backend\requirements.txt
```

---

## 👤 Project

**Intelligent Research Copilot**

GitHub:

[https://github.com/Iamhasan69/intelligent-research-copilot](https://github.com/Iamhasan69/intelligent-research-copilot)


```
