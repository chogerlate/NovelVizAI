"""
MongoDB models for Novel Companion AI using Beanie
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from beanie import Document, Indexed
from pydantic import BaseModel, Field
from pymongo import IndexModel, ASCENDING, TEXT
from bson import ObjectId
from pydantic import ConfigDict


class RelatedSeries(BaseModel):
    """Related series model"""
    title: str
    relation: str


class ChaptersInfo(BaseModel):
    """Chapters information model"""
    main_story: int = Field(alias="mainStory")
    epilogue: Optional[int] = None
    side_stories: Optional[int] = Field(None, alias="sideStories")


class Novel(Document):
    """Novel document model for MongoDB"""
    
    # Basic Information
    title: Indexed(str)
    type: Optional[str] = None
    original_language: Optional[str] = Field(None, alias="originalLanguage")
    author: Optional[str] = None
    artist: Optional[str] = None
    description: Optional[str] = None
    
    # Classification
    genres: List[str] = []
    tags: List[str] = []
    
    # Ratings and Statistics
    average_rating: Optional[float] = Field(None, alias="averageRating")
    vote_count: Optional[int] = Field(None, alias="voteCount")
    total_reading_lists: Optional[int] = Field(None, alias="totalReadingLists")
    
    # Publication Information
    year: Optional[int] = None
    status_in_coo: Optional[str] = Field(None, alias="statusInCOO")  # Status in Country of Origin
    chapters_in_coo: Optional[ChaptersInfo] = Field(None, alias="chaptersInCOO")
    is_completely_translated: Optional[bool] = Field(None, alias="isCompletelyTranslated")
    
    # Publishers
    original_publisher: List[str] = Field([], alias="originalPublisher")
    english_publisher: List[str] = Field([], alias="englishPublisher")
    
    # Related Information
    associated_names: List[str] = Field([], alias="associatedNames")
    related_series: List[RelatedSeries] = Field([], alias="relatedSeries")
    
    # Metadata
    last_updated: datetime = Field(default_factory=datetime.utcnow, alias="lastUpdated")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "novels"
        indexes = [
            IndexModel([("title", TEXT)], name="title_text_index"),
            IndexModel([("author", ASCENDING)], name="author_index"),
            IndexModel([("genres", ASCENDING)], name="genres_index"),
            IndexModel([("tags", ASCENDING)], name="tags_index"),
            IndexModel([("average_rating", ASCENDING)], name="rating_index"),
            IndexModel([("year", ASCENDING)], name="year_index"),
            IndexModel([("status_in_coo", ASCENDING)], name="status_index"),
            IndexModel([("created_at", ASCENDING)], name="created_at_index"),
        ]


class Chapter(Document):
    """Chapter document model for MongoDB"""
    
    # Basic Information
    novel_id: Indexed(str)  # Changed to str to avoid ObjectId issues
    title: str
    chapter_number: int
    
    # Content
    content: str  # The actual chapter text content
    summary: Optional[str] = None
    analysis_data: Optional[Dict[str, Any]] = None # To store the full LLM analysis
    
    # Analysis Results
    key_events: List[str] = []
    characters_mentioned: List[str] = []
    themes: List[str] = []
    sentiment_score: Optional[float] = None
    
    # Metadata
    word_count: Optional[int] = None
    reading_time_minutes: Optional[int] = None
    
    # Processing Status
    is_processed: bool = False
    processing_timestamp: Optional[datetime] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "chapters"
        indexes = [
            IndexModel([("novel_id", ASCENDING)], name="novel_id_index"),
            IndexModel([("chapter_number", ASCENDING)], name="chapter_number_index"),
            IndexModel([("novel_id", ASCENDING), ("chapter_number", ASCENDING)], name="novel_chapter_index", unique=True),
            IndexModel([("title", TEXT)], name="chapter_title_text_index"),
            IndexModel([("created_at", ASCENDING)], name="chapter_created_at_index"),
            IndexModel([("is_processed", ASCENDING)], name="processed_index"),
        ]


class Character(Document):
    """Character document model for MongoDB"""
    
    # Basic Information
    novel_id: Indexed(str)  # Changed to str to avoid ObjectId issues
    name: Indexed(str)
    description: Optional[str] = None
    
    # Character Details
    character_type: Optional[str] = None  # protagonist, antagonist, supporting, minor
    first_appearance_chapter: Optional[int] = None
    last_appearance_chapter: Optional[int] = None
    
    # Relationships and Traits
    relationships: List[Dict[str, str]] = []  # [{"character": "Name", "relationship": "friend"}]
    key_traits: List[str] = []
    aliases: List[str] = []
    
    # Statistics
    mentions_count: int = 0
    chapters_appeared: List[int] = []
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "characters"
        indexes = [
            IndexModel([("novel_id", ASCENDING)], name="character_novel_id_index"),
            IndexModel([("name", TEXT)], name="character_name_text_index"),
            IndexModel([("character_type", ASCENDING)], name="character_type_index"),
            IndexModel([("mentions_count", ASCENDING)], name="mentions_count_index"),
        ]


class ChatHistory(Document):
    """Chat history document model for MongoDB"""
    
    novel_id: Indexed(str)  # Changed to str to avoid ObjectId issues
    user_message: str
    assistant_response: str
    context_used: Dict[str, Any] = {}  # Store context references
    model_used: Optional[str] = None
    response_time_ms: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "chat_history"
        indexes = [
            IndexModel([("novel_id", ASCENDING)], name="chat_novel_id_index"),
            IndexModel([("created_at", ASCENDING)], name="chat_created_at_index"),
        ]


class Analysis(Document):
    """Analysis results document model for MongoDB"""
    
    novel_id: Indexed(str)  # Changed to str to avoid ObjectId issues
    analysis_type: str  # themes, plot, style, characters, sentiment
    results: Dict[str, Any] = {}  # Store analysis results
    insights: List[str] = []  # Store insights
    confidence_score: Optional[float] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "analyses"
        indexes = [
            IndexModel([("novel_id", ASCENDING)], name="analysis_novel_id_index"),
            IndexModel([("analysis_type", ASCENDING)], name="analysis_type_index"),
            IndexModel([("created_at", ASCENDING)], name="analysis_created_at_index"),
        ]


# Export all models
__all__ = [
    "Novel",
    "Chapter", 
    "Character",
    "ChatHistory",
    "Analysis",
    "RelatedSeries",
    "ChaptersInfo"
] 