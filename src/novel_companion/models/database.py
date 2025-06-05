"""
Database models for Novel Companion AI
"""

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey, Enum, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

from ..config import settings

# Database setup
engine = create_engine(settings.database_url, echo=settings.debug)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class NovelStatusEnum(enum.Enum):
    """Novel status enumeration"""
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"


class CharacterTypeEnum(enum.Enum):
    """Character type enumeration"""
    PROTAGONIST = "protagonist"
    ANTAGONIST = "antagonist"
    SUPPORTING = "supporting"
    MINOR = "minor"


class Novel(Base):
    """Novel database model"""
    __tablename__ = "novels"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, index=True)
    type = Column(String(50), nullable=True)  # Web Novel, Light Novel, etc.
    original_language = Column(String(50), nullable=True)
    author = Column(String(100), nullable=True)
    artist = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    content = Column(Text, nullable=False)
    genres = Column(JSON, nullable=True)  # Store as JSON array
    tags = Column(JSON, nullable=True)  # Store as JSON array
    average_rating = Column(String(10), nullable=True)  # Store as string to handle decimals
    vote_count = Column(Integer, nullable=True)
    total_reading_lists = Column(Integer, nullable=True)
    year = Column(Integer, nullable=True)
    status_in_coo = Column(String(50), nullable=True)  # Ongoing, Completed, etc.
    chapters_in_coo = Column(Integer, nullable=True)
    is_completely_translated = Column(String(10), nullable=True)  # Store as string for boolean
    original_publisher = Column(JSON, nullable=True)  # Store as JSON array
    english_publisher = Column(JSON, nullable=True)  # Store as JSON array
    associated_names = Column(JSON, nullable=True)  # Store as JSON array
    related_series = Column(JSON, nullable=True)  # Store as JSON array
    status = Column(Enum(NovelStatusEnum), default=NovelStatusEnum.UPLOADED)
    last_updated = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
    
    # Relationships
    chapters = relationship("Chapter", back_populates="novel", cascade="all, delete-orphan")
    characters = relationship("Character", back_populates="novel", cascade="all, delete-orphan")
    
    @property
    def chapter_count(self):
        return len(self.chapters)
    
    @property
    def character_count(self):
        return len(self.characters)


class Chapter(Base):
    """Chapter database model"""
    __tablename__ = "chapters"
    
    id = Column(Integer, primary_key=True, index=True)
    novel_id = Column(Integer, ForeignKey("novels.id"), nullable=False)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    summary = Column(Text, nullable=True)
    chapter_number = Column(Integer, nullable=False)
    key_events = Column(JSON, nullable=True)  # Store as JSON array
    characters_mentioned = Column(JSON, nullable=True)  # Store as JSON array
    analysis_data = Column(JSON, nullable=True)  # Store analysis results as JSON
    themes = Column(JSON, nullable=True)  # Store as JSON array
    sentiment_score = Column(Float, nullable=True)
    word_count = Column(Integer, nullable=True)
    reading_time_minutes = Column(Integer, nullable=True)
    is_processed = Column(Boolean, default=False)
    processing_timestamp = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
    
    # Relationships
    novel = relationship("Novel", back_populates="chapters")


class Character(Base):
    """Character database model"""
    __tablename__ = "characters"
    
    id = Column(Integer, primary_key=True, index=True)
    novel_id = Column(Integer, ForeignKey("novels.id"), nullable=False)
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    character_type = Column(Enum(CharacterTypeEnum), default=CharacterTypeEnum.SUPPORTING)
    first_appearance_chapter = Column(Integer, nullable=True)
    relationships = Column(JSON, nullable=True)  # Store as JSON array
    key_traits = Column(JSON, nullable=True)  # Store as JSON array
    mentions_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    novel = relationship("Novel", back_populates="characters")


class ChatHistory(Base):
    """Chat history database model"""
    __tablename__ = "chat_history"
    
    id = Column(Integer, primary_key=True, index=True)
    novel_id = Column(Integer, ForeignKey("novels.id"), nullable=False)
    user_message = Column(Text, nullable=False)
    assistant_response = Column(Text, nullable=False)
    context_used = Column(JSON, nullable=True)  # Store context references
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Analysis(Base):
    """Analysis results database model"""
    __tablename__ = "analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    novel_id = Column(Integer, ForeignKey("novels.id"), nullable=False)
    analysis_type = Column(String(50), nullable=False)  # themes, plot, style, characters
    results = Column(JSON, nullable=False)  # Store analysis results as JSON
    insights = Column(JSON, nullable=True)  # Store insights as JSON array
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# Database utility functions
def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)


def drop_tables():
    """Drop all database tables"""
    Base.metadata.drop_all(bind=engine) 