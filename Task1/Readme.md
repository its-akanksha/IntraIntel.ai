# 🏥 Medical Notes Digitization API

A FastAPI-based service to digitize handwritten medical notes using
**AWS Textract** (OCR) and process them into structured text with
keywords. Notes are stored in MongoDB and can be searched or retrieved.

------------------------------------------------------------------------

## 🚀 Features

-   Upload handwritten medical notes (image/PDF).
-   Extract text using AWS Textract (OCR).
-   Clean and normalize extracted text.
-   Extract relevant **medical keywords** (via rules or Gemini/AI models).
-   Save notes into **MongoDB** with metadata.
-   Search and retrieve notes via API.

------------------------------------------------------------------------

## ⚙️ Setup Instructions

### 1️⃣ Clone the Repository

``` bash
git clone https://github.com/its-akanksha/IntraIntel.ai.git
cd IntraIntel.ai
cd Task 1
```

### 2️⃣ Create Virtual Environment & Install Dependencies

``` bash
python -m venv .venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3️⃣ Environment Variables

Create a `.env` file in the root directory:

``` ini
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
AWS_REGION=ap-south-1
MONGODB_URL=mongodb+srv://user:password@cluster.mongodb.net/
GEMINI_API_KEY=your_gemini_api_key   # optional if using Gemini for keywords
```

### 4️⃣ Run the API

``` bash
uvicorn main:app --reload
```

Visit API docs: 👉 <http://127.0.0.1:8000/docs>

------------------------------------------------------------------------

## 📂 Sample Data

### Input (sample note image)

*(example image goes here if available)*

### Extracted Text (raw)

```
Patient complains of headache and nausea.
BP: 120/80
Medication: Paracetamol 500 mg
```

### Processed Text

```
Patient complains of headache and nausea. Blood pressure: 120/80. Medication: Paracetamol 500mg.
```

### Extracted Keywords

```
["patient", "headache", "nausea", "blood pressure", "medication", "paracetamol"]
```

------------------------------------------------------------------------

## 📡 API Endpoints

### 1. Upload a Note

``` http
POST /upload-note/
```

**Body:** multipart/form-data (file)

**Response:**

``` json
{
  "note_id": "650a7f3...",
  "processed_text": "Patient complains of headache...",
  "keywords": ["headache", "blood pressure"],
  "status": "success"
}
```

------------------------------------------------------------------------

### 2. Search Notes

``` http
GET /search/?keyword=headache&limit=5
```

**Response:**

``` json
{
  "keyword": "headache",
  "results": [
    {"note_id": "...", "processed_text": "Patient complains of headache..."}
  ],
  "count": 1
}
```

------------------------------------------------------------------------

### 3. Get Note by ID

``` http
GET /notes/{note_id}
```

------------------------------------------------------------------------

### 4. List Notes (Paginated)

``` http
GET /notes/?limit=10&skip=0
```

------------------------------------------------------------------------

## 📝 Design Decisions

-   **FastAPI** → Modern async API framework, auto docs, easy to scale.
-   **AWS Textract** → Reliable OCR for handwritten/printed text in
    medical notes.
-   **MongoDB** → Flexible document store, great for unstructured
    medical text + metadata.
-   **Text Processing** → Cleaning + keyword extraction for medical
    relevance. Can use Gemini/AI for richer entity extraction.
-   **Security** → Uses `.env` for secrets (no hardcoding credentials).
-   **Extensibility** → Can add more NLP (e.g., entity recognition,
    ICD-10 coding).
