from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import uvicorn
from services.textract import TextractService
from services.text_processor import TextProcessor
from services.database import DatabaseService
from config import settings
import os
from datetime import datetime

app = FastAPI(title="Medical Notes Digitization API", version="1.0.0")

# Initialize services
textract_service = TextractService()
text_processor = TextProcessor()
db_service = DatabaseService()

@app.on_event("startup")
async def startup_event():
    await db_service.connect()

@app.on_event("shutdown")
async def shutdown_event():
    await db_service.disconnect()

@app.post("/upload-note/")
async def upload_note(file: UploadFile = File(...)):
    """Upload and process handwritten medical note"""
    try:
        # Save uploaded file temporarily
        temp_path = f"temp_{file.filename}"
        with open(temp_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Extract text using Textract
        raw_text = textract_service.extract_text(temp_path)
        
        # Clean and process text
        processed_text = text_processor.clean_text(raw_text)
        keywords = text_processor.extract_keywords(processed_text)
        
        # Save to database
        note_data = {
            "filename": file.filename,
            "raw_text": raw_text,
            "processed_text": processed_text,
            "keywords": keywords,
            "created_at": datetime.utcnow(),
            "file_size": len(content)
        }
        
        note_id = await db_service.save_note(note_data)
        
        # Cleanup
        os.remove(temp_path)
        
        return {
            "note_id": str(note_id),
            "processed_text": processed_text,
            "keywords": keywords,
            "status": "success"
        }
        
    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/search/")
async def search_notes(keyword: str, limit: int = 10):
    """Search notes by keyword"""
    try:
        results = await db_service.search_notes(keyword, limit)
        return {
            "keyword": keyword,
            "results": results,
            "count": len(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/notes/{note_id}")
async def get_note(note_id: str):
    """Get specific note by ID"""
    try:
        note = await db_service.get_note(note_id)
        if not note:
            raise HTTPException(status_code=404, detail="Note not found")
        return note
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/notes/")
async def list_notes(limit: int = 10, skip: int = 0):
    """List all notes with pagination"""
    try:
        notes = await db_service.list_notes(limit, skip)
        return {
            "notes": notes,
            "count": len(notes)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)