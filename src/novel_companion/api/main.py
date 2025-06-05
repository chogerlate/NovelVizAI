"""
FastAPI main application for Novel Companion AI - MongoDB Version
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager
import uvicorn
import os
from typing import List, Optional, Dict, Any
from datetime import datetime
from bson import ObjectId

from ..models.mongodb_connection import (
    connect_to_mongodb, 
    disconnect_from_mongodb,
    get_novel_by_id,
    get_novel_by_title,
    get_chapters_by_novel_id,
    get_characters_by_novel_id,
    search_novels
)
from ..models.mongodb_models import Novel, Chapter, Character, ChatHistory
from ..models.mongodb_operations import NovelOperations, ChapterOperations, CharacterOperations
from ..services.openrouter_client import openrouter_client
from ..services.nlp_processor import nlp_processor
from ..config import settings

# Create upload directory if it doesn't exist
os.makedirs(settings.upload_directory, exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan"""
    # Startup
    await connect_to_mongodb()
    print("Novel Companion AI started successfully with MongoDB!")
    yield
    # Shutdown
    await disconnect_from_mongodb()


# Initialize FastAPI app
app = FastAPI(
    title="Novel Companion AI",
    description="AI-driven reading assistant with intelligent chapter summarization, dynamic character mapping, and interactive story companion using MongoDB",
    version="0.2.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Updated Pydantic models for MongoDB
from pydantic import BaseModel, Field, ConfigDict

class NovelCreateRequest(BaseModel):
    """Request model for creating a novel"""
    title: str = Field(..., min_length=1, max_length=200)
    author: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    content: str = Field(..., min_length=100)

class NovelResponse(BaseModel):
    """Response model for novel data"""
    id: str
    title: str
    author: Optional[str] = None
    description: Optional[str] = None
    genres: List[str] = []
    tags: List[str] = []
    average_rating: Optional[float] = None
    vote_count: Optional[int] = None
    year: Optional[int] = None
    status_in_coo: Optional[str] = None
    created_at: datetime
    last_updated: datetime

# Detailed models for chapter analysis data
class ChapterMetadata(BaseModel):
    """Chapter metadata model"""
    novel_id: Optional[str] = None
    chapter_id: Optional[str] = None
    novel_title: Optional[str] = None
    chapter_number: Optional[int] = None
    chapter_title: Optional[str] = None
    word_count: Optional[int] = None
    estimated_reading_time: Optional[int] = None

class EmotionalArc(BaseModel):
    """Emotional arc model"""
    emotion: Optional[str] = None
    intensity: Optional[float] = None

class CharacterSentiment(BaseModel):
    """Character sentiment model"""
    dominant_emotions: Optional[List[str]] = []
    emotional_state: Optional[str] = None

class SentimentAnalysis(BaseModel):
    """Sentiment analysis model"""
    overall_tone: Optional[str] = None
    emotional_arc: Optional[List[EmotionalArc]] = []
    character_sentiments: Optional[Dict[str, CharacterSentiment]] = {}

class ChapterSummary(BaseModel):
    """Chapter summary model"""
    concise: Optional[str] = None
    detailed: Optional[str] = None
    key_events: Optional[List[str]] = []

class Theme(BaseModel):
    """Theme model"""
    theme: Optional[str] = None
    relevance: Optional[float] = None
    evidence: Optional[str] = None

class Foreshadowing(BaseModel):
    """Foreshadowing model"""
    text: Optional[str] = None
    significance: Optional[str] = None

class Symbolism(BaseModel):
    """Symbolism model"""
    symbol: Optional[str] = None
    meaning: Optional[str] = None

class LiteraryElements(BaseModel):
    """Literary elements model"""
    narrative_voice: Optional[str] = None
    foreshadowing: Optional[List[Foreshadowing]] = []
    symbolism: Optional[List[Symbolism]] = []

class ChapterAnalysis(BaseModel):
    """Chapter analysis model"""
    metadata: Optional[ChapterMetadata] = None
    summary: Optional[ChapterSummary] = None
    sentiment_analysis: Optional[SentimentAnalysis] = None
    themes: Optional[List[Theme]] = []
    literary_elements: Optional[LiteraryElements] = None

class CharacterProfile(BaseModel):
    """Character profile model"""
    name: Optional[str] = None
    role: Optional[str] = None
    first_appearance: Optional[str] = None
    description: Optional[str] = None
    key_traits: Optional[List[str]] = []
    quotes: Optional[List[str]] = []
    development_status: Optional[str] = None

class Relationship(BaseModel):
    """Character relationship model"""
    characters: Optional[List[str]] = []
    relationship_type: Optional[str] = None
    dynamics: Optional[str] = None
    significance: Optional[str] = None
    interaction_count: Optional[int] = None
    sentiment: Optional[str] = None

class CharacterMapping(BaseModel):
    """Character mapping model"""
    characters: Optional[List[CharacterProfile]] = []
    relationships: Optional[List[Relationship]] = []

class ChapterContext(BaseModel):
    """Chapter context model"""
    setting: Optional[str] = None
    timeline_position: Optional[str] = None
    narrative_importance: Optional[str] = None

class InteractiveCompanion(BaseModel):
    """Interactive companion model"""
    chapter_context: Optional[ChapterContext] = None
    key_question: Optional[List[str]] = []
    suggested_discussion_point: Optional[List[str]] = []

class ComplexityMetrics(BaseModel):
    """Complexity metrics model"""
    readability_score: Optional[int] = None
    vocabulary_level: Optional[str] = None
    structural_complexity: Optional[str] = None

class PacingShift(BaseModel):
    """Pacing shift model"""
    position: Optional[str] = None
    change: Optional[str] = None

class PacingAnalysis(BaseModel):
    """Pacing analysis model"""
    overall_pace: Optional[str] = None
    significant_shifts: Optional[List[PacingShift]] = []

class EngagementFactors(BaseModel):
    """Engagement factors model"""
    hook: Optional[List[str]] = []
    engagement_score: Optional[float] = None

class ReadingAnalytics(BaseModel):
    """Reading analytics model"""
    complexity_metrics: Optional[ComplexityMetrics] = None
    complexity_metric: Optional[ComplexityMetrics] = None  # Handle both field names
    pacing_analysis: Optional[PacingAnalysis] = None
    engagement_factors: Optional[EngagementFactors] = None
    
    model_config = ConfigDict(extra='allow')

class AnalysisData(BaseModel):
    """Complete analysis data model"""
    chapter_analysis: Optional[ChapterAnalysis] = None
    character_mapping: Optional[CharacterMapping] = None
    interactive_companion: Optional[InteractiveCompanion] = None
    reading_analytics: Optional[ReadingAnalytics] = None
    
    model_config = ConfigDict(extra='allow', populate_by_name=True)

class ChapterResponse(BaseModel):
    """Response model for chapter data"""
    id: str
    novel_id: str
    title: str
    chapter_number: int
    content: Optional[str] = None  # Optional in response, might be too large
    summary: Optional[str] = None
    analysis_data: Optional[AnalysisData] = None
    key_events: List[str] = []
    characters_mentioned: List[str] = []
    themes: List[str] = []
    sentiment_score: Optional[float] = None
    word_count: Optional[int] = None
    reading_time_minutes: Optional[int] = None
    is_processed: bool = False
    processing_timestamp: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

class CharacterResponse(BaseModel):
    """Response model for character data"""
    id: str
    novel_id: str
    name: str
    description: Optional[str] = None
    character_type: Optional[str] = None
    first_appearance_chapter: Optional[int] = None
    relationships: List[Dict[str, str]] = []
    key_traits: List[str] = []
    mentions_count: int = 0
    chapters_appeared: List[int] = []

class ChapterSummaryRequest(BaseModel):
    """Request model for chapter summarization"""
    summary_length: Optional[str] = Field("medium", pattern="^(short|medium|long)$")

class ChapterSummaryResponse(BaseModel):
    """Response model for chapter summarization"""
    chapter_id: str
    summary: str
    key_events: List[str]
    characters_mentioned: List[str]

class ChatRequest(BaseModel):
    """Chat request model"""
    message: str = Field(..., min_length=1, max_length=1000)

class ChatResponse(BaseModel):
    """Chat response model"""
    response: str
    references: List[str] = []
    suggested_questions: List[str] = []

class FileUploadResponse(BaseModel):
    """File upload response"""
    filename: str
    size: int
    message: str
    novel_id: Optional[str] = None


# API Endpoints

@app.post("/api/novels/", response_model=NovelResponse)
async def create_novel(
    novel: NovelCreateRequest,
    background_tasks: BackgroundTasks
):
    """Create a new novel and start processing"""
    try:
        # Create novel in MongoDB
        novel_data = {
            "title": novel.title,
            "author": novel.author,
            "description": novel.description,
            "created_at": datetime.utcnow(),
            "last_updated": datetime.utcnow()
        }
        
        db_novel = await NovelOperations.create_novel(novel_data)
        
        # Add background task to process content
        background_tasks.add_task(process_novel_async, str(db_novel.id), novel.content)
        
        return NovelResponse(
            id=str(db_novel.id),
            title=db_novel.title,
            author=db_novel.author,
            description=db_novel.description,
            genres=db_novel.genres,
            tags=db_novel.tags,
            average_rating=db_novel.average_rating,
            vote_count=db_novel.vote_count,
            year=db_novel.year,
            status_in_coo=db_novel.status_in_coo,
            created_at=db_novel.created_at,
            last_updated=db_novel.last_updated
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating novel: {str(e)}")

@app.get("/api/novels/", response_model=List[NovelResponse])
async def list_novels(
    skip: int = 0, 
    limit: int = 100,
    search: Optional[str] = None,
    author: Optional[str] = None,
    genres: Optional[str] = None,
    tags: Optional[str] = None
):
    """List all novels with optional filtering"""
    try:
        # Parse comma-separated values
        genre_list = genres.split(",") if genres else None
        tag_list = tags.split(",") if tags else None
        
        novels = await search_novels(
            query=search,
            author=author,
            genres=genre_list,
            tags=tag_list,
            skip=skip,
            limit=limit
        )
        
        return [
            NovelResponse(
                id=str(novel.id),
                title=novel.title,
                author=novel.author,
                description=novel.description,
                genres=novel.genres,
                tags=novel.tags,
                average_rating=novel.average_rating,
                vote_count=novel.vote_count,
                year=novel.year,
                status_in_coo=novel.status_in_coo,
                created_at=novel.created_at,
                last_updated=novel.last_updated
            )
            for novel in novels
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing novels: {str(e)}")

@app.get("/api/novels/{novel_id}", response_model=NovelResponse)
async def get_novel(novel_id: str):
    """Get a specific novel"""
    try:
        novel = await get_novel_by_id(novel_id)
        if novel is None:
            raise HTTPException(status_code=404, detail="Novel not found")
        
        return NovelResponse(
            id=str(novel.id),
            title=novel.title,
            author=novel.author,
            description=novel.description,
            genres=novel.genres,
            tags=novel.tags,
            average_rating=novel.average_rating,
            vote_count=novel.vote_count,
            year=novel.year,
            status_in_coo=novel.status_in_coo,
            created_at=novel.created_at,
            last_updated=novel.last_updated
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting novel: {str(e)}")

@app.get("/api/novels/{novel_id}/chapters", response_model=List[ChapterResponse])
async def get_novel_chapters(
    novel_id: str,
    skip: int = 0,
    limit: int = 100,
    include_content: bool = False
):
    """Get chapters for a specific novel"""
    try:
        # Verify novel exists
        novel = await get_novel_by_id(novel_id)
        if not novel:
            raise HTTPException(status_code=404, detail="Novel not found")
        
        chapters = await get_chapters_by_novel_id(novel_id, skip=skip, limit=limit)
        
        return [
            ChapterResponse(
                id=str(chapter.id),
                novel_id=chapter.novel_id,
                title=chapter.title,
                chapter_number=chapter.chapter_number,
                content=chapter.content if include_content else None,
                summary=chapter.summary,
                analysis_data=safe_parse_analysis_data(chapter.analysis_data),
                key_events=chapter.key_events,
                characters_mentioned=chapter.characters_mentioned,
                themes=chapter.themes,
                sentiment_score=chapter.sentiment_score,
                word_count=chapter.word_count,
                reading_time_minutes=chapter.reading_time_minutes,
                is_processed=chapter.is_processed,
                processing_timestamp=chapter.processing_timestamp,
                created_at=chapter.created_at,
                updated_at=chapter.updated_at
            )
            for chapter in chapters
        ]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting chapters: {str(e)}")

@app.get("/api/chapters/{chapter_id}", response_model=ChapterResponse)
async def get_chapter(
    chapter_id: str,
    include_content: bool = True
):
    """Get a specific chapter with all analysis data"""
    try:
        from ..models.mongodb_models import Chapter
        
        chapter = await Chapter.get(chapter_id)
        if not chapter:
            raise HTTPException(status_code=404, detail="Chapter not found")
        
        return ChapterResponse(
            id=str(chapter.id),
            novel_id=chapter.novel_id,
            title=chapter.title,
            chapter_number=chapter.chapter_number,
            content=chapter.content if include_content else None,
            summary=chapter.summary,
            analysis_data=safe_parse_analysis_data(chapter.analysis_data),
            key_events=chapter.key_events,
            characters_mentioned=chapter.characters_mentioned,
            themes=chapter.themes,
            sentiment_score=chapter.sentiment_score,
            word_count=chapter.word_count,
            reading_time_minutes=chapter.reading_time_minutes,
            is_processed=chapter.is_processed,
            processing_timestamp=chapter.processing_timestamp,
            created_at=chapter.created_at,
            updated_at=chapter.updated_at
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting chapter: {str(e)}")

@app.post("/api/upload/", response_model=FileUploadResponse)
async def upload_novel_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    title: Optional[str] = None,
    author: Optional[str] = None
):
    """Upload a novel file"""
    try:
        if file.size and file.size > settings.max_file_size:
            raise HTTPException(status_code=413, detail="File too large")
        
        content = await file.read()
        content_str = content.decode('utf-8')
        
        # Create novel in MongoDB
        novel_data = {
            "title": title or file.filename,
            "author": author,
            "created_at": datetime.utcnow(),
            "last_updated": datetime.utcnow()
        }
        
        db_novel = await NovelOperations.create_novel(novel_data)
        
        # Add background task to process content
        background_tasks.add_task(process_novel_async, str(db_novel.id), content_str)
        
        return FileUploadResponse(
            filename=file.filename,
            size=file.size or 0,
            message="Novel uploaded successfully",
            novel_id=str(db_novel.id)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")

@app.post("/api/chapters/{chapter_id}/summarize", response_model=ChapterSummaryResponse)
async def summarize_chapter(
    chapter_id: str,
    request: ChapterSummaryRequest
):
    """Generate chapter summary"""
    try:
        chapter = await Chapter.get(chapter_id)
        if not chapter:
            raise HTTPException(status_code=404, detail="Chapter not found")
        
        summary_data = await openrouter_client.generate_chapter_summary(
            chapter_content=chapter.content,
            chapter_title=chapter.title,
            summary_length=request.summary_length
        )
        
        # Update chapter with summary
        await ChapterOperations.update_chapter_analysis(
            chapter_id,
            {
                "summary": summary_data.get("summary", ""),
                "key_events": summary_data.get("key_events", []),
                "characters_mentioned": summary_data.get("characters_mentioned", [])
            }
        )
        
        return ChapterSummaryResponse(
            chapter_id=chapter_id,
            summary=summary_data.get("summary", ""),
            key_events=summary_data.get("key_events", []),
            characters_mentioned=summary_data.get("characters_mentioned", [])
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating summary: {str(e)}")

@app.get("/api/novels/{novel_id}/characters", response_model=List[CharacterResponse])
async def get_characters(novel_id: str):
    """Get all characters for a novel"""
    try:
        # Verify novel exists
        novel = await get_novel_by_id(novel_id)
        if not novel:
            raise HTTPException(status_code=404, detail="Novel not found")
        
        characters = await get_characters_by_novel_id(novel_id)
        
        return [
            CharacterResponse(
                id=str(character.id),
                novel_id=character.novel_id,
                name=character.name,
                description=character.description,
                character_type=character.character_type,
                first_appearance_chapter=character.first_appearance_chapter,
                relationships=character.relationships,
                key_traits=character.key_traits,
                mentions_count=character.mentions_count,
                chapters_appeared=character.chapters_appeared
            )
            for character in characters
        ]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting characters: {str(e)}")

@app.post("/api/novels/{novel_id}/chat", response_model=ChatResponse)
async def chat_about_novel(
    novel_id: str,
    request: ChatRequest
):
    """Interactive chat about the novel"""
    try:
        novel = await get_novel_by_id(novel_id)
        if not novel:
            raise HTTPException(status_code=404, detail="Novel not found")
        
        # Get some chapter content for context
        chapters = await get_chapters_by_novel_id(novel_id, limit=5)
        context_content = "\n\n".join([f"Chapter {ch.chapter_number}: {ch.title}\n{ch.summary or ch.content[:500]}" for ch in chapters])
        
        response_data = await openrouter_client.chat_about_story(
            question=request.message,
            novel_context=context_content
        )
        
        # Save chat history
        chat_record = ChatHistory(
            novel_id=novel_id,
            user_message=request.message,
            assistant_response=response_data.get("response", ""),
            context_used={"chapters_used": len(chapters)},
            created_at=datetime.utcnow()
        )
        await chat_record.insert()
        
        return ChatResponse(
            response=response_data.get("response", ""),
            references=response_data.get("references", []),
            suggested_questions=response_data.get("suggested_questions", [])
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in chat: {str(e)}")

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the frontend application"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Novel Companion AI - MongoDB Edition</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
        <div id="app">
            <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
                <div class="container">
                    <a class="navbar-brand" href="#">📚 Novel Companion AI - MongoDB</a>
                </div>
            </nav>
            
            <div class="container mt-4">
                <h1>Welcome to Novel Companion AI</h1>
                <p class="lead">Your intelligent reading assistant powered by MongoDB</p>
                
                <div class="row mt-4">
                    <div class="col-md-4">
                        <div class="card">
                            <div class="card-body">
                                <h5>📝 Advanced Chapter Analysis</h5>
                                <p>AI-powered analysis with detailed insights stored in MongoDB.</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="card">
                            <div class="card-body">
                                <h5>🔍 Powerful Search</h5>
                                <p>Full-text search across novels, chapters, and characters.</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="card">
                            <div class="card-body">
                                <h5>💬 Smart Conversations</h5>
                                <p>Context-aware chat with persistent history.</p>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="mt-4">
                    <a href="/docs" class="btn btn-primary">API Documentation</a>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

async def process_novel_async(novel_id: str, content: str):
    """Background task to process uploaded novel"""
    try:
        # Split content into chapters
        chapters_data = nlp_processor.split_into_chapters(content, f"Novel {novel_id}")
        
        # Create chapters in MongoDB
        for i, chapter_data in enumerate(chapters_data):
            chapter = Chapter(
                novel_id=novel_id,
                title=chapter_data.get("title", f"Chapter {i+1}"),
                chapter_number=i+1,
                content=chapter_data.get("content", ""),
                word_count=len(chapter_data.get("content", "").split()),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            await chapter.insert()
        
        print(f"✅ Processed {len(chapters_data)} chapters for novel {novel_id}")
        
    except Exception as e:
        print(f"❌ Error processing novel {novel_id}: {e}")

def safe_parse_analysis_data(analysis_data_raw: Optional[Dict[str, Any]]) -> Optional[AnalysisData]:
    """Safely parse analysis data with error handling"""
    if not analysis_data_raw:
        return None
    
    try:
        return AnalysisData.model_validate(analysis_data_raw)
    except Exception as e:
        print(f"Warning: Could not parse analysis_data: {e}")
        # Return a basic structure if parsing fails
        return AnalysisData()

def run_server(
    host_override=None, 
    port_override=None, 
    debug_override=None, 
    reload_override=None
):
    """Run the FastAPI server"""
    uvicorn.run(
        "src.novel_companion.api.main:app",
        host=host_override or settings.host,
        port=port_override or settings.port,
        reload=reload_override if reload_override is not None else settings.debug,
        log_level="debug" if (debug_override or settings.debug) else "info"
    ) 