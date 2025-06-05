"""
Pydantic models for Novel Companion AI
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class NovelStatus(str, Enum):
    """Novel processing status"""
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"


class CharacterType(str, Enum):
    """Character type classification"""
    PROTAGONIST = "protagonist"
    ANTAGONIST = "antagonist"
    SUPPORTING = "supporting"
    MINOR = "minor"


class NovelBase(BaseModel):
    """Base novel model"""
    title: str = Field(..., min_length=1, max_length=200)
    author: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)


class NovelCreate(NovelBase):
    """Novel creation model"""
    content: str = Field(..., min_length=100)


class NovelUpdate(BaseModel):
    """Novel update model"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    author: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)


class Novel(NovelBase):
    """Novel response model"""
    id: int
    status: NovelStatus
    created_at: datetime
    updated_at: datetime
    chapter_count: int = 0
    character_count: int = 0
    
    class Config:
        from_attributes = True


class ChapterBase(BaseModel):
    """Base chapter model"""
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=50)
    chapter_number: int = Field(..., ge=1)


class ChapterCreate(ChapterBase):
    """Chapter creation model"""
    novel_id: int


class Chapter(ChapterBase):
    """Chapter response model"""
    id: int
    novel_id: int
    summary: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class CharacterBase(BaseModel):
    """Base character model"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    character_type: CharacterType = CharacterType.SUPPORTING


class CharacterCreate(CharacterBase):
    """Character creation model"""
    novel_id: int


class Character(CharacterBase):
    """Character response model"""
    id: int
    novel_id: int
    first_appearance_chapter: Optional[int] = None
    relationships: List[str] = Field(default_factory=list)
    key_traits: List[str] = Field(default_factory=list)
    created_at: datetime
    
    class Config:
        from_attributes = True


class ChapterSummaryRequest(BaseModel):
    """Request model for chapter summarization"""
    chapter_id: int
    summary_length: Optional[str] = Field("medium", pattern="^(short|medium|long)$")


class ChapterSummaryResponse(BaseModel):
    """Response model for chapter summarization"""
    chapter_id: int
    summary: str
    key_events: List[str]
    characters_mentioned: List[str]


class CharacterMappingResponse(BaseModel):
    """Response model for character mapping"""
    novel_id: int
    characters: List[Character]
    relationships: List[Dict[str, Any]]
    character_network: Dict[str, Any]


class ChatMessage(BaseModel):
    """Chat message model"""
    role: str = Field(..., pattern="^(user|assistant)$")
    content: str = Field(..., min_length=1)
    timestamp: Optional[datetime] = None


class ChatRequest(BaseModel):
    """Chat request model"""
    novel_id: int
    message: str = Field(..., min_length=1, max_length=1000)
    context: Optional[List[str]] = Field(default_factory=list)


class ChatResponse(BaseModel):
    """Chat response model"""
    response: str
    references: List[str] = Field(default_factory=list)
    suggested_questions: List[str] = Field(default_factory=list)


class AnalysisRequest(BaseModel):
    """General analysis request"""
    novel_id: int
    analysis_type: str = Field(..., pattern="^(themes|plot|style|characters)$")
    

class AnalysisResponse(BaseModel):
    """General analysis response"""
    analysis_type: str
    results: Dict[str, Any]
    insights: List[str]


class FileUploadResponse(BaseModel):
    """File upload response"""
    filename: str
    size: int
    message: str
    novel_id: Optional[int] = None


class ErrorResponse(BaseModel):
    """Error response model"""
    error: str
    detail: Optional[str] = None
    code: Optional[str] = None 