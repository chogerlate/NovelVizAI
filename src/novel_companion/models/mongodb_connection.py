"""
MongoDB connection and initialization for Novel Companion AI
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from typing import Optional

from ..config import settings
from .mongodb_models import Novel, Chapter, Character, ChatHistory, Analysis


class MongoDBManager:
    """MongoDB connection manager"""
    
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.database = None
        
    async def connect(self):
        """Connect to MongoDB and initialize Beanie"""
        try:
            # Create MongoDB client
            self.client = AsyncIOMotorClient(settings.mongodb_url)
            
            # Get database
            self.database = self.client[settings.mongodb_database]
            
            # Test connection
            await self.client.admin.command('ping')
            print(f"✅ Connected to MongoDB: {settings.mongodb_database}")
            
            # Initialize Beanie with document models
            await init_beanie(
                database=self.database,
                document_models=[Novel, Chapter, Character, ChatHistory, Analysis]
            )
            print("✅ Beanie initialized with document models")
            
        except Exception as e:
            print(f"❌ Failed to connect to MongoDB: {e}")
            raise
    
    async def disconnect(self):
        """Disconnect from MongoDB"""
        if self.client:
            self.client.close()
            print("✅ Disconnected from MongoDB")
    
    async def create_indexes(self):
        """Create additional custom indexes if needed"""
        try:
            # You can add custom indexes here if needed beyond the model definitions
            print("✅ Custom indexes created successfully")
        except Exception as e:
            print(f"⚠️ Error creating custom indexes: {e}")
    
    async def health_check(self) -> bool:
        """Check if MongoDB connection is healthy"""
        try:
            await self.client.admin.command('ping')
            return True
        except Exception:
            return False


# Global MongoDB manager instance
mongodb_manager = MongoDBManager()


# Helper functions for FastAPI lifespan events
async def connect_to_mongodb():
    """Connect to MongoDB (use in FastAPI startup)"""
    await mongodb_manager.connect()
    await mongodb_manager.create_indexes()


async def disconnect_from_mongodb():
    """Disconnect from MongoDB (use in FastAPI shutdown)"""
    await mongodb_manager.disconnect()


# Utility functions for common operations
async def get_novel_by_id(novel_id: str) -> Optional[Novel]:
    """Get a novel by its ID"""
    try:
        return await Novel.get(novel_id)
    except Exception:
        return None


async def get_novel_by_title(title: str) -> Optional[Novel]:
    """Get a novel by its title"""
    return await Novel.find_one(Novel.title == title)


async def get_chapters_by_novel_id(novel_id: str, skip: int = 0, limit: int = 100) -> list[Chapter]:
    """Get chapters for a specific novel"""
    return await Chapter.find(
        Chapter.novel_id == novel_id
    ).sort("chapter_number").skip(skip).limit(limit).to_list()


async def get_characters_by_novel_id(novel_id: str) -> list[Character]:
    """Get characters for a specific novel"""
    return await Character.find(Character.novel_id == novel_id).to_list()


async def search_novels(
    query: str = None,
    genres: list[str] = None,
    tags: list[str] = None,
    author: str = None,
    skip: int = 0,
    limit: int = 20
) -> list[Novel]:
    """Search novels with various filters"""
    filters = []
    
    if query:
        # Text search on title and description
        filters.append({"$text": {"$search": query}})
    
    if author:
        filters.append({"author": {"$regex": author, "$options": "i"}})
    
    if genres:
        filters.append({"genres": {"$in": genres}})
    
    if tags:
        filters.append({"tags": {"$in": tags}})
    
    # Combine filters
    if filters:
        query_filter = {"$and": filters} if len(filters) > 1 else filters[0]
        return await Novel.find(query_filter).skip(skip).limit(limit).to_list()
    else:
        return await Novel.find_all().skip(skip).limit(limit).to_list()


# Export main components
__all__ = [
    "mongodb_manager",
    "connect_to_mongodb", 
    "disconnect_from_mongodb",
    "get_novel_by_id",
    "get_novel_by_title",
    "get_chapters_by_novel_id",
    "get_characters_by_novel_id",
    "search_novels"
] 