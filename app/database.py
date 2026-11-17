from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.config import settings


class DatabaseManager:
    """Manages asynchronous connections and collections in MongoDB."""

    def __init__(self, uri: str, db_name: str):
        self.client: Optional[AsyncIOMotorClient] = None
        self.db: Optional[AsyncIOMotorDatabase] = None
        self.uri = uri
        self.db_name = db_name

    async def connect(self):
        self.client = AsyncIOMotorClient(self.uri)
        self.db = self.client[self.db_name]
        # Create indexes for high-speed lookup
        await self.db.conversations.create_index("session_id")
        await self.db.datasets.create_index("dataset_id", unique=True)
        print(" Connected to MongoDB successfully!")

    async def disconnect(self):
        if self.client:
            self.client.close()
            print(" Disconnected from MongoDB.")

    async def append_message(
        self, session_id: str, role: str, content: str, tool_calls: Optional[List[Dict[str, Any]]] = None
    ):
        doc = {
            "session_id": session_id,
            "role": role,
            "content": content,
            "tool_calls": tool_calls or [],
            "created_at": datetime.now(timezone.utc),
        }
        await self.db.conversations.insert_one(doc)

    async def get_history(self, session_id: str, limit: int = 15) -> List[Dict[str, Any]]:
        cursor = (
            self.db.conversations.find({"session_id": session_id})
            .sort("created_at", 1)
            .limit(limit)
        )
        return await cursor.to_list(length=limit)

    async def store_dataset_metadata(self, dataset_id: str, filename: str, filepath: str, columns: List[str]):
        doc = {
            "dataset_id": dataset_id,
            "filename": filename,
            "filepath": filepath,
            "columns": columns,
            "created_at": datetime.now(timezone.utc),
        }
        await self.db.datasets.insert_one(doc)

    async def get_dataset_metadata(self, dataset_id: str) -> Optional[Dict[str, Any]]:
        return await self.db.datasets.find_one({"dataset_id": dataset_id})


db_manager = DatabaseManager(settings.MONGODB_URI, settings.DATABASE_NAME)