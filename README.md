# Intelligent Research Copilot — Complete Agent

A local-first AI research workspace for the Code Cubicle 6.0 PS-01 direction: natural-language requirement → planning → multi-source discovery → URL/file ingestion → evidence processing → verification → deduplication → structured dataset → report → knowledge graph → export.

## What makes this an agent, not a chat wrapper
- Planner creates subquestions, search queries, source preferences, deliverables and verification rules.
- Discovery uses provider-native web grounding/browser search when available.
- Explicit URLs are fetched and parsed into evidence.
- Local PDF/DOCX/TXT/MD/CSV/JSON/LOG files are ingested.
- Evidence is persisted per research run with provenance.
- Synthesis asks the model for structured dataset rows, entities, relationships, evidence, conflicts and limitations.
- Research history is stored in SQLite.
- Exports: Markdown, CSV and JSON.
- Provider settings support Gemini and Groq with runtime verification and model selection.

## Current provider integrations
Gemini supports Google Search grounding through the current Gemini API. Groq uses its OpenAI-compatible APIs; GPT-OSS 20B/120B can use Groq's Responses API browser search. The app falls back to normal model generation for models without browser search.

## Run on Windows PowerShell
```powershell
cd "D:\Ddownload\Intelligent_Research_Copilot"
py -m venv .venv
Set-ExecutionPolicy -Scope Process Bypass
.\.venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```
Open http://127.0.0.1:8000

## Configure
Open **Settings**, choose Gemini or Groq, paste your key, choose a model, and click **Verify & Connect**. Keys are stored by this local app in SQLite for the current local installation. Do not commit the database or keys to GitHub.

## Example research
> Find 10 Indian cybersecurity companies working on AI security. For each, identify product focus, founders, public funding information and recent activity. Prefer primary sources, cite evidence, deduplicate companies, and flag conflicting information.

## Project structure
```text
backend/
  main.py
  services/
    agent.py       # planner + research workflow
    providers.py   # Gemini/Groq adapters
    scanner.py     # URL and document ingestion
    db.py          # SQLite persistence
frontend/
  index.html
  app.js
  styles.css
storage/           # local database
 data/uploads/     # local uploaded files
```

## Security notes
This is intended for local/authorized research. URL fetching blocks common private/local address ranges. File uploads are limited to common research formats and 20 MB per file. API keys should never be placed in frontend JavaScript or committed to source control.

## Next production hardening
For public deployment, replace local plaintext key storage with a secrets manager/encrypted vault, add authentication, stronger SSRF/DNS-rebinding protection, background job queues, rate limits, object storage, PostgreSQL, vector retrieval, browser automation with sandboxing, and provider-specific citation normalization.
