import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List
from google import genai
from google.genai import types
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine

app = FastAPI(title="Secure Enterprise NLP SaaS Pipeline")

# Initialize Local PII Masking Engines
analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()

# Initialize Google GenAI Client
# Ensure you set your environment variable: export GEMINI_API_KEY="your_key"
client = genai.Client()

# Define the Pydantic schema matching your Google AI Studio configuration
class AnalysisResponse(BaseModel):
    summary: str = Field(description="A concise, 2-sentence executive summary of the document.")
    urgency_level: str = Field(description="The determined urgency: LOW, MEDIUM, HIGH, CRITICAL")
    key_metrics: List[str] = Field(description="Any specific quantities, dates, or operational metrics found.")
    action_items: List[str] = Field(description="Clear, actionable next steps extracted from the text.")

class TextInput(BaseModel):
    text: str

def anonymize_text(raw_text: str) -> str:
    """Masks names, phone numbers, email addresses, and cryptographic keys locally."""
    results = analyzer.analyze(text=raw_text, language="en")
    # Fixed the argument name below from analyze_results to analyzer_results
    anonymized_result = anonymizer.anonymize(text=raw_text, analyzer_results=results)
    return anonymized_result.text

@app.post("/api/analyze", response_model=AnalysisResponse)
async def process_document(payload: TextInput):
    if not payload.text.strip():
        raise HTTPException(status_code=400, detail="Text payload cannot be empty.")
    
    try:
        # Step 1: Local Anonymization (Compliance Layer)
        safe_text = anonymize_text(payload.text)
        
        # Step 2: High-Performance Extraction via Gemini 3.5 Flash
        response = client.models.generate_content(
            model='gemini-3.1-flash-lite',
            contents=safe_text,
            config=types.GenerateContentConfig(
                system_instruction=(
                    "You are a precise enterprise SaaS data extraction engine designed for automated workflow pipelines. "
                    "Your task is to analyze the provided pre-anonymized medical/enterprise text and extract critical operational insights. "
                    "You must strictly adhere to the user-provided schema. Do not include any conversational filler. Return only the raw structured data."
                ),
                # Enforces strict JSON matching your Pydantic schema
                response_mime_type="application/json",
                response_schema=AnalysisResponse,
                temperature=0.1, # Low temperature for consistent deterministic extractions
            ),
        )
        
        # The response.text is guaranteed to perfectly fit the AnalysisResponse schema
        return AnalysisResponse.model_validate_json(response.text)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)