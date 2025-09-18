import os
import json
import logging
from typing import List
from concurrent.futures import ThreadPoolExecutor, TimeoutError

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import google.generativeai as genai

from dotenv import load_dotenv

load_dotenv()

# ---------------- Logging ----------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("main")

# ---------------- Gemini Config ----------------
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise RuntimeError("❌ GEMINI_API_KEY not set in environment")

genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")

# ---------------- Data Models ----------------
class ClinicalNote(BaseModel):
    note_id: str
    text: str

class SummaryOutput(BaseModel):
    note_id: str
    patient: str
    diagnosis: str
    treatment: str
    follow_up: str

# ---------------- Helper Functions ----------------
def call_model(prompt: str) -> str:
    """Call Gemini and return raw response text."""
    response = model.generate_content([prompt])
    return response.text.strip()

def process_note(note: ClinicalNote) -> SummaryOutput:
    """Summarize one clinical note into structured JSON."""
    logger.info(f"Processing note ID: {note.note_id}")

    prompt = f"""
    You are a medical assistant. Summarize the following clinical note
    into JSON with these exact keys: patient, diagnosis, treatment, follow_up.

    Rules:
    - patient → ONLY the patient name
    - diagnosis → concise condition
    - treatment → short phrase or list of meds
    - follow_up → follow up time or instructions or "Unknown"

    Clinical Note:
    {note.text}
    """

    executor = ThreadPoolExecutor(max_workers=1)
    try:
        future = executor.submit(call_model, prompt)
        summary_text = future.result(timeout=30)  

        # Remove ```json fences if present
        if summary_text.startswith("```"):
            summary_text = summary_text.split("\n", 1)[1].rsplit("```", 1)[0].strip()

        structured_summary = json.loads(summary_text)

    except TimeoutError:
        logger.error(f"⏱ Timeout for note {note.note_id}")
        structured_summary = {}
    except Exception as e:
        logger.error(f"❌ Error for note {note.note_id}: {e}")
        structured_summary = {}

    return SummaryOutput(
        note_id=note.note_id,
        patient=structured_summary.get("patient", "Unknown"),
        diagnosis=structured_summary.get("diagnosis", "Unknown"),
        treatment=structured_summary.get("treatment", "Unknown"),
        follow_up=structured_summary.get("follow_up", "Unknown"),
    )

# ---------------- FastAPI App ----------------
app = FastAPI(
    title="Clinical Record Summarization API",
    description="Batch summarization of clinical notes into structured JSON using Gemini.",
    version="1.0.0",
)

@app.post("/summarize", response_model=List[SummaryOutput])
async def summarize_notes(notes: List[ClinicalNote]):
    """Summarize a batch of clinical notes."""
    try:
        results = [process_note(note) for note in notes]
        return results
    except Exception as e:
        logger.error(f"Error processing batch: {e}")
        raise HTTPException(status_code=500, detail="Summarization failed")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
