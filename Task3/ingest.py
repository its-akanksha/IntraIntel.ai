import argparse
import json
import os
import sys
import re
from langchain_chroma import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from langchain_huggingface import HuggingFaceEmbeddings


def extract_field(text: str, field_name: str) -> str:
    """Extract a specific field (Diagnosis, Treatment, Follow-up) from note text."""
    # More robust regex to handle various cases and empty diagnoses
    patterns = [
        # Standard pattern: "Diagnosis: content. Treatment:"
        rf"{field_name}:\s*(.*?)(?=\s+(?:Treatment|Follow-up))",
        # End of text pattern: "Diagnosis: content.$"  
        rf"{field_name}:\s*(.*?)(?:\.|$)",
        # Handle empty diagnosis: "Diagnosis: . Treatment:"
        rf"{field_name}:\s*([^.]*?)(?:\s*\.\s*(?:Treatment|Follow-up)|$)"
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            content = match.group(1).strip().rstrip('.')
            # Skip empty diagnoses (just whitespace or single period)
            if content and content not in ['.', '']:
                return content
    return ""


def ingest(notes_path: str, persist_dir: str):
    """Ingest clinical notes into ChromaDB with Hugging Face embeddings (incremental mode)."""

    # Load notes JSON
    if not os.path.exists(notes_path):
        print(f"❌ Error: Notes file not found at {notes_path}")
        sys.exit(1)

    try:
        with open(notes_path, "r", encoding="utf-8") as f:
            notes = json.load(f)
        if not isinstance(notes, list):
            raise ValueError("JSON must be a list of notes.")
    except Exception as e:
        print(f"❌ Failed to load JSON: {e}")
        sys.exit(1)

    print(f"📥 Loaded {len(notes)} notes from {notes_path}")

    # Convert notes to LangChain Documents with structured metadata
    docs = []
    for note in notes:
        content = note.get("note", "").strip()
        if not content:
            continue

        diagnosis = extract_field(content, "Diagnosis")
        treatment = extract_field(content, "Treatment")
        followup = extract_field(content, "Follow-up")

        metadata = {
            "patient_id": note.get("patient_id", ""),
            "name": note.get("name", ""),
            "age": str(note.get("age", "")),  # Ensure age is string
            "diagnosis": diagnosis.lower() if diagnosis else "",
            "treatment": treatment,
            "followup": followup,
            # Store original full note content for retrieval
            "full_note": content
        }

        docs.append(Document(page_content=content, metadata=metadata))

    if not docs:
        print("⚠️ No valid notes found to ingest.")
        sys.exit(1)

    print(f"📝 Converted {len(docs)} notes into Documents")

    # Split into smaller chunks for embedding
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    texts = splitter.split_documents(docs)
    print(f"✂️ Split into {len(texts)} chunks for embedding")

    # Initialize embeddings
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    # Load or create Chroma collection
    os.makedirs(persist_dir, exist_ok=True)
    db = Chroma(persist_directory=persist_dir, embedding_function=embeddings)

    # Add documents incrementally
    db.add_documents(texts)
    print(f"✅ Ingestion complete. Database saved at: {persist_dir}")
    print(f"📦 Total documents now stored: {db._collection.count()}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest notes into ChromaDB with Hugging Face embeddings")
    parser.add_argument("--notes", required=True, help="Path to notes JSON file")
    parser.add_argument("--persist_dir", required=True, help="Directory to store ChromaDB")
    args = parser.parse_args()

    ingest(args.notes, args.persist_dir)