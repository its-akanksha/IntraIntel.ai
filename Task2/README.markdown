# Clinical Record Summarization System

This project provides a FastAPI-based system for summarizing digitized **clinical notes** into structured JSON format using **Google Gemini LLM**.  

It is part of a 4-task repository focusing on AI-driven clinical data processing and retrieval.

---

## 📂 Folder Structure
```
project-root/
│── main.py                # FastAPI application with batch summarization
│── requirements.txt       # Dependencies
│── README.md              # Documentation
├── sample_notes.json      # Example input notes
├── sample_outputs.json    # Example structured outputs
├── Dockerfile
```

---

## 🚀 How to Run

### 1. Clone the repository
```bash
git clone https://github.com/its-akanksha/IntraIntel.ai.git
cd IntraIntel.ai
cd Task2
```

### 2. Create a virtual environment & install dependencies
```bash
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Set up environment variables

Create a `.env` file:
```
GEMINI_API_KEY=your_api_key_here
```

### 4. Start the FastAPI server
```bash
uvicorn main:app --reload
```

### 5. To build image locally
```bash
# Build image
docker build -t task2 .
```

### 6. To run the container
```bash
docker run -d -p 8000:8000 --env GEMINI_API_KEY=your_api_key task2
```


### 5. Test the API
Endpoint:  
```
POST http://127.0.0.1:8000/summarize
```

Sample Payload:
```json
[
  {
    "note_id": "note_001",
    "text": "Patient John Doe, 45-year-old male, presented with chest pain and shortness of breath. Diagnosed with acute myocardial infarction. Administered aspirin and nitroglycerin. Recommended coronary angiography. Schedule follow-up in 1 week."
  },
  {
    "note_id": "note_002",
    "text": "Jane Smith, female, 60 years old, reports persistent cough and fever. Diagnosis: Community-acquired pneumonia. Prescribed antibiotics (amoxicillin). Follow-up appointment in 10 days to monitor recovery."
  }
]
```

---

## ✅ Sample JSON Output
```json
[
  {
    "note_id": "note_001",
    "patient": "John Doe",
    "diagnosis": "acute myocardial infarction",
    "treatment": "aspirin, nitroglycerin, coronary angiography",
    "follow_up": "1 week"
  },
  {
    "note_id": "note_002",
    "patient": "Jane Smith",
    "diagnosis": "community-acquired pneumonia",
    "treatment": "amoxicillin",
    "follow_up": "10 days"
  }
]
```

---

## 🔹 LLM Choice & Justification
This project uses **Google Gemini (via the `google-generativeai` SDK)** as the Large Language Model (LLM).  

**Why Gemini?**
- **Structured JSON outputs**: Gemini handles instructions for JSON schema adherence better than many open-source models.
- **Low latency**: Responses are typically faster than Hugging Face pipelines.
- **Flexibility**: Can handle both short and long clinical notes without truncation.
- **Reliability**: Cloud-hosted model avoids downloading large checkpoints like BART/T5.  

Alternative models like **BART** were considered, but Gemini was chosen for **production-readiness and schema compliance**.

---

## 🧠 Thought Process & Design Decisions
1. **Batch Processing**: API supports multiple notes in one request for efficiency.  
2. **Schema Enforcement**: Strict JSON schema with keys `patient`, `diagnosis`, `treatment`, `follow_up`.  
3. **Error Handling**: If Gemini outputs invalid JSON, fallback ensures `"Unknown"` placeholders.  
4. **Extensibility**: Modular design for future integration with RAG pipelines or EHR systems.  

---

## 🔧 AI Tool Usage
- **ChatGPT & Copilot**: Assisted with designing FastAPI endpoints and JSON parsing logic.  
- **Gemini**: Used for summarization of free-text clinical notes into structured data.  

---

## 📊 Example Workflow
1. User uploads raw clinical notes.  
2. FastAPI sends each note to Gemini LLM.  
3. Gemini returns structured JSON summary.  
4. API responds with batch results.  

---

