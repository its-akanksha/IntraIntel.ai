from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from typing import List, Dict, Optional
from config import settings
import logging

logger = logging.getLogger(__name__)

class DatabaseService:
    def __init__(self):
        self.client = None
        self.db = None
        self.collection = None
    
    async def connect(self):
        """Connect to MongoDB"""
        try:
            self.client = AsyncIOMotorClient(settings.MONGODB_URL)
            self.db = self.client.medical_notes
            self.collection = self.db.notes
            
            # Ensure text index exists (idempotent)
            await self.collection.create_index([
                ("processed_text", "text"),
                ("keywords", "text")
            ])
            
            logger.info("Connected to MongoDB successfully")
        except Exception as e:
            logger.error(f"MongoDB connection failed: {e}")
            raise
    
    async def disconnect(self):
        """Disconnect from MongoDB"""
        if self.client:
            self.client.close()
    
    async def save_note(self, note_data: Dict) -> ObjectId:
        """Save processed note to database"""
        try:
            result = await self.collection.insert_one(note_data)
            return result.inserted_id
        except Exception as e:
            logger.error(f"Failed to save note: {e}")
            raise
    
    async def search_notes(self, keyword: str, limit: int = 10) -> List[Dict]:
        """Search notes by keyword using text index, fallback to regex"""
        try:
            results = []

            # First try text search (fastest if index exists)
            cursor = self.collection.find({"$text": {"$search": keyword}}).limit(limit)
            async for doc in cursor:
                doc["_id"] = str(doc["_id"])
                doc["created_at"] = doc["created_at"].isoformat()
                results.append(doc)

            # If no results, fallback to regex search
            if not results:
                cursor = self.collection.find({
                    "$or": [
                        {"keywords": {"$regex": keyword, "$options": "i"}},
                        {"processed_text": {"$regex": keyword, "$options": "i"}}
                    ]
                }).limit(limit)

                async for doc in cursor:
                    doc["_id"] = str(doc["_id"])
                    doc["created_at"] = doc["created_at"].isoformat()
                    results.append(doc)

            return results
        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise
    
    async def get_note(self, note_id: str) -> Optional[Dict]:
        """Get note by ID"""
        try:
            doc = await self.collection.find_one({"_id": ObjectId(note_id)})
            if doc:
                doc["_id"] = str(doc["_id"])
                doc["created_at"] = doc["created_at"].isoformat()
            return doc
        except Exception as e:
            logger.error(f"Failed to get note: {e}")
            return None
    
    async def list_notes(self, limit: int = 10, skip: int = 0) -> List[Dict]:
        """List notes with pagination"""
        try:
            cursor = (
                self.collection.find()
                .skip(skip)
                .limit(limit)
                .sort("created_at", -1)
            )
            results = []
            
            async for doc in cursor:
                doc["_id"] = str(doc["_id"])
                doc["created_at"] = doc["created_at"].isoformat()
                results.append(doc)
            
            return results
        except Exception as e:
            logger.error(f"Failed to list notes: {e}")
            raise
