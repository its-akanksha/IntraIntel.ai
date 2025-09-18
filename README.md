## Overview

This repository contains the implementation of **Tasks 1--4** as
outlined in the project requirements.\
The system digitizes handwritten medical notes, summarizes them into
structured clinical records, enables semantic search via a RAG pipeline,
and deploys services in a cloud-native environment.

------------------------------------------------------------------------

## 📌 Tasks

### ✅ Task 1: Handwritten Notes Digitization & Indexing

-   Used **AWS Textract** for handwritten OCR extraction (sample dummy
    handwritten notes included in repository).
-   Cleaned extracted text and stored structured output in
    **MongoDB** and **ChromaDB** (for vector search).
-   Implemented a **FastAPI** search service to query notes by keywords.

------------------------------------------------------------------------

### ✅ Task 2: Clinical Record Summarization with an LLM

-   Used **Gemini Free Tier** to summarize extracted notes into
    structured JSON format.
-   Fields: `Patient`, `Diagnosis`, `Treatment`, `Follow-up`.
-   Batch processing pipeline included.

------------------------------------------------------------------------

### ✅ Task 3: Mini RAG Agent

-   Ingested several notes into **ChromaDB**.
-   Used **LangChain** to enable query processing.
-   Built a REST API that answers:
    -   "Which patients had X diagnosis?"
    -   "What treatment was prescribed most frequently?"

------------------------------------------------------------------------

### ✅ Task 4: Cloud-Native Deployment

-   Containerized service using **Docker** (`Dockerfile` provided).
-   Deployed via **AWS EC2 (Free Tier)**.
-   Public endpoint provided in
    `Task4.md`.
    
------------------------------------------------------------------------

## 📂 Repo Structure

    ├── Task1/               # OCR + Indexing pipeline
    ├── Task2/               # Summarization with LLM
    ├── Task3/               # RAG pipeline + chatbot
    ├── Task4.md             # Docker + Cloud deployment configs
    ├── README.md            # Project documentation

------------------------------------------------------------------------

## 🛠️ Setup & Installation

Clone the repo and install dependencies:

``` bash
git clone https://github.com/your-username/medical-notes-ai.git
cd IntraIntel.ai
```
Run services (example for FastAPI):

``` bash
uvicorn task1.app:app --reload
```

------------------------------------------------------------------------

## 📖 Documentation

Each task folder contains its own README with usage details and sample
outputs.

------------------------------------------------------------------------

## ✅ Status

**All tasks completed successfully.**
