# Secure Enterprise NLP SaaS Pipeline

A high-performance, asynchronous NLP data extraction engine designed for enterprise SaaS applications handling sensitive corporate or healthcare data. 

This architecture implements a **zero-trust local data-masking layer** that completely sanitizes Personally Identifiable Information (PII) before routing data to public cloud LLM endpoints, combining strict data compliance (GDPR/HIPAA considerations) with low-latency structured JSON analysis.

## 🛠️ Tech Stack & Architecture

- **Compliance Engine:** Microsoft Presidio Analyzer/Anonymizer + spaCy (`en_core_web_lg`) for local, zero-leakage PII identification.
- **NLP Brain:** Google GenAI SDK (`gemini-3.1-flash-lite`) via Google AI Studio for high-speed, cost-optimized extraction.
- **API Framework:** FastAPI (Asynchronous Python backend) with automated OpenAPI/Swagger generation.
- **Data Guarantee:** Pydantic validation mapping exact strict schema constraints to Gemini's Structured Outputs feature.

---

## 🚀 Getting Started

### 1. Prerequisites
Ensure you have Python 3.10+ installed, then clone the repository and install the dependencies:
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_lg
