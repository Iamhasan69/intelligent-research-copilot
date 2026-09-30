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