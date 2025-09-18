from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from collections import Counter
import os
import re

# Initialize
DB_PATH = "./chroma_db"
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

if not os.path.exists(DB_PATH):
    raise FileNotFoundError(f"Database not found at {DB_PATH}. Run ingest.py first.")

db = Chroma(persist_directory=DB_PATH, embedding_function=embeddings)
app = FastAPI(title="Clinical RAG API")

class QueryIn(BaseModel):
    q: str

# Helper functions
def find_by_diagnosis(diagnosis: str):
    """Search patients by diagnosis (case-insensitive, multiple strategies)."""
    diagnosis_lower = diagnosis.lower().strip()
    all_data = db._collection.get(include=['metadatas', 'documents'])
    
    matches = []
    seen_patients = set()
    
    for doc_content, metadata in zip(all_data['documents'], all_data['metadatas']):
        if not metadata:
            continue
            
        patient_id = metadata.get("patient_id", "")
        if patient_id in seen_patients:
            continue
            
        doc_diag = metadata.get("diagnosis", "").lower()
        full_note = metadata.get("full_note", doc_content).lower()
        
        # Match strategies: direct diagnosis, full text, medical variations
        is_match = (
            diagnosis_lower in doc_diag or 
            diagnosis_lower in full_note or
            (diagnosis_lower == "headache" and any(t in full_note for t in ["headache", "migraine", "cephalgia"])) or
            (diagnosis_lower == "diabetes" and any(t in full_note for t in ["diabetes", "diabetic", "blood glucose"]))
        )
        
        if is_match:
            seen_patients.add(patient_id)
            matches.append({
                "patient_id": patient_id,
                "name": metadata.get("name", ""),
                "age": metadata.get("age", ""),
                "diagnosis": metadata.get("diagnosis", ""),
                "note": metadata.get("full_note", doc_content)
            })
    
    return matches

def most_common_treatment():
    """Find most frequently prescribed treatment."""
    all_data = db._collection.get(include=['metadatas'])
    treatments = []
    seen_patients = set()
    
    for metadata in all_data['metadatas']:
        if not metadata:
            continue
        patient_id = metadata.get("patient_id", "")
        treatment = metadata.get("treatment", "")
        
        if treatment and patient_id not in seen_patients:
            seen_patients.add(patient_id)
            treatments.append(treatment)
    
    if not treatments:
        return {"error": "No treatments found"}
    
    most_common, frequency = Counter(treatments).most_common(1)[0]
    return {
        "most_common_treatment": most_common,
        "frequency": frequency,
        "total_analyzed": len(treatments)
    }

def extract_diagnosis_from_query(query: str) -> str:
    """Extract diagnosis from natural language query."""
    query_lower = query.lower()
    
    # Try regex patterns first
    patterns = [
        r"which patients.*?(?:have|had|with)\s+([^?]+)",
        r"patients.*?(?:diagnosed with|have|had)\s+([^?]+)",
        r"who.*?(?:has|have|had)\s+([^?]+)"
    ]
    
    for pattern in patterns:
        match = re.search(pattern, query_lower)
        if match:
            return re.sub(r'\b(the|a|an)\b', '', match.group(1).strip()).strip()
    
    # Fallback to medical terms
    medical_terms = ["pneumonia", "diabetes", "hypertension", "copd", "appendicitis", 
                    "myocardial infarction", "alzheimer", "endometriosis", "osteoarthritis",
                    "anxiety", "depression", "migraine", "headache"]
    
    for term in medical_terms:
        if term in query_lower:
            return term
    return ""

# API Endpoints
@app.get("/")
def root():
    return {"message": "Clinical RAG API", "endpoints": ["/which_patients", "/most_common_treatment", "/query", "/debug/patients"]}

@app.get("/which_patients")
def which_patients(diagnosis: str):
    if not diagnosis:
        raise HTTPException(status_code=400, detail="Provide ?diagnosis=...")
    matches = find_by_diagnosis(diagnosis)
    return {"diagnosis_searched": diagnosis, "matches": matches, "count": len(matches)}

@app.get("/most_common_treatment")
def get_most_common_treatment():
    return most_common_treatment()

@app.post("/query")
def query(q: QueryIn):
    """Handle natural language queries."""
    qtxt = q.q.lower().strip()
    
    # Diagnosis queries
    if any(word in qtxt for word in ["which patients", "who has", "who have", "patients with", "diagnosed with"]):
        diagnosis = extract_diagnosis_from_query(qtxt)
        if diagnosis:
            matches = find_by_diagnosis(diagnosis)
            return {"intent": "which_patients", "diagnosis": diagnosis, "matches": matches, "count": len(matches)}
        return {"error": "Could not extract diagnosis. Try: 'Which patients have pneumonia?'"}
    
    # Treatment queries
    elif "most" in qtxt and "treatment" in qtxt:
        return {"intent": "most_common_treatment", **most_common_treatment()}
    
    # Semantic search
    else:
        try:
            results = db.similarity_search(q.q, k=3)
            return {
                "intent": "semantic_search",
                "results": [{"content": doc.page_content, "metadata": doc.metadata} for doc in results]
            }
        except:
            return {"error": "Query failed. Try specific questions about patients or treatments."}

@app.get("/debug/patients")
def debug_patients():
    """Show all patients and extracted data."""
    try:
        all_data = db._collection.get(include=['metadatas'])
        patients = {}
        
        for metadata in all_data['metadatas']:
            if not metadata:
                continue
            patient_id = metadata.get("patient_id", "")
            if patient_id and patient_id not in patients:
                patients[patient_id] = {
                    "patient_id": patient_id,
                    "name": metadata.get("name", ""),
                    "diagnosis": metadata.get("diagnosis", ""),
                    "treatment": metadata.get("treatment", "")
                }
        
        return {"total_patients": len(patients), "patients": list(patients.values())}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)