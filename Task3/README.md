# Mini RAG Clinical QA Project

## Project Overview

This project demonstrates a minimal Retrieval-Augmented Generation (RAG) system for clinical notes. It uses **Hugging Face embeddings** (sentence-transformers) to convert notes into vectors and **Chroma** as the vector database. FastAPI serves the API endpoints for querying clinical notes with intelligent diagnosis and treatment analysis.

## Folder Structure

```
rag_mini_project/
│
├── sample_data/notes.json                 # Clinical notes in JSON format
├── chroma_db/                             # Persisted vector database (auto-created after ingest)
├── ingest.py                              # Script to ingest notes into ChromaDB 
├── main.py                                # FastAPI server for querying the RAG system
├── requirements.txt                       # Python dependencies
└── README.md                              # Project documentation
```

## Setup & Installation

1. Clone the repository and navigate to the project folder:

```bash
git clone https://github.com/its-akanksha/IntraIntel.ai.git
cd IntraIntel.ai
cd Task3
```

2. Create a virtual environment and activate it:

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

## Sample Data Format

The clinical notes should be in JSON format with the following structure:

```json
[
  {
    "patient_id": "P001",
    "name": "John Doe", 
    "age": 45,
    "note": "Patient presents with chest pain. Diagnosis: Acute myocardial infarction. Treatment: Aspirin, Nitroglycerin. Follow-up: Cardiology in 2 weeks."
  }
]
```

## Ingest Notes into ChromaDB

Run the ingestion script to create vector embeddings for your notes:

```bash
python ingest.py --notes sample_data/notes.json --persist_dir ./chroma_db
```

The script will:
- Extract structured fields (Diagnosis, Treatment, Follow-up) from note text
- Create embeddings using Hugging Face's `sentence-transformers/all-MiniLM-L6-v2` model
- Store everything in ChromaDB for fast retrieval

After successful ingestion, `chroma_db/` will contain your persisted vector database.

## Running the API

Start the FastAPI server:

```bash
uvicorn main:app --reload
```

The API will be available at `http://127.0.0.1:8000` with interactive docs at `http://127.0.0.1:8000/docs`.

## API Endpoints

### 1. Root endpoint
```
GET /
```
Returns API information and available endpoints.

### 2. Search patients by diagnosis
```
GET /which_patients?diagnosis=<DIAGNOSIS>
```

Examples:
```
http://127.0.0.1:8000/which_patients?diagnosis=headache
http://127.0.0.1:8000/which_patients?diagnosis=diabetes  
http://127.0.0.1:8000/which_patients?diagnosis=pneumonia
```

**Features:**
- Case-insensitive search
- Searches both extracted diagnosis fields and full note content
- Handles medical term variations (headache/migraine, diabetes/diabetic)
- Returns patient details with extracted diagnosis information

### 3. Get most common treatment
```
GET /most_common_treatment
```
Returns the most frequently prescribed treatment across all patients.

### 4. Natural language query endpoint
```
POST /query
```

Body example:
```json
{ "q": "Which patients had pneumonia?" }
```

**Supported query types:**
- `"Which patients have diabetes?"`
- `"Who was diagnosed with headache?"`
- `"What treatment was prescribed most frequently?"`
- `"Tell me about chest pain patients"` (semantic search)

### 5. Debug endpoint
```
GET /debug/patients
```
Shows all patients and their extracted diagnosis/treatment data for troubleshooting.

## Key Features

### **Smart Diagnosis Matching**
The system uses multiple strategies to find patients:
1. **Direct match** in extracted diagnosis field
2. **Full-text search** in original note content  
3. **Medical term variations** (e.g., headache → migraine, diabetes → diabetic)
4. **Symptom-based matching** for cases where formal diagnosis extraction failed

### **Robust Field Extraction**
- Handles various clinical note formats
- Extracts Diagnosis, Treatment, and Follow-up information
- Manages empty or malformed diagnosis fields
- Preserves original note content for fallback search

### **Incremental Data Processing**
- Avoids duplicate results from document chunking
- Tracks unique patients across multiple document chunks
- Efficient metadata storage and retrieval

## Example Usage

1. **Ingest your clinical notes:**
```bash
python ingest.py --notes sample_data/notes.json --persist_dir ./chroma_db
```

2. **Start the API server:**
```bash
python main.py
```

3. **Query for patients with specific conditions:**
```bash
# Using GET endpoint
curl "http://127.0.0.1:8000/which_patients?diagnosis=headache"

# Using natural language POST endpoint  
curl -X POST "http://127.0.0.1:8000/query" \
     -H "Content-Type: application/json" \
     -d '{"q": "Which patients have diabetes?"}'
```

4. **Find most common treatments:**
```bash
curl "http://127.0.0.1:8000/most_common_treatment"
```

5. **Debug data extraction:**
```bash
curl "http://127.0.0.1:8000/debug/patients"
```

## Notes & Design Decisions

- **Embeddings**: Uses Hugging Face's `sentence-transformers/all-MiniLM-L6-v2` for fast, local embeddings (no API key required)
- **Vector Database**: ChromaDB provides efficient similarity search and metadata filtering
- **Text Processing**: Robust regex patterns handle various clinical note formats
- **API Design**: RESTful endpoints with both structured and natural language query support
- **Error Handling**: Comprehensive error handling with helpful debugging endpoints
- **Performance**: Optimized to avoid duplicate processing and provide fast responses

## Troubleshooting

If queries return no results:

1. **Check data ingestion:** Use `/debug/patients` to verify diagnosis extraction
2. **Verify database:** Ensure `chroma_db/` folder exists and contains data
3. **Test different terms:** Try variations like "diabetes" vs "diabetic"
4. **Check logs:** The ingestion script shows extraction statistics

## Requirements

- Python 3.8+
- FastAPI
- LangChain
- ChromaDB  
- Hugging Face Transformers
- sentence-transformers

See `requirements.txt` for complete dependency list.
