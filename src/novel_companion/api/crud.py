"""
CRUD operations for Novel Companion AI
"""

from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime

from ..models import database, schemas


# Novel CRUD operations
def create_novel(db: Session, novel: schemas.NovelCreate) -> database.Novel:
    """Create a new novel"""
    db_novel = database.Novel(
        title=novel.title,
        author=novel.author,
        description=novel.description,
        content=novel.content,
        status=database.NovelStatusEnum.UPLOADED
    )
    db.add(db_novel)
    db.commit()
    db.refresh(db_novel)
    return db_novel


def get_novel(db: Session, novel_id: int) -> Optional[database.Novel]:
    """Get a novel by ID"""
    return db.query(database.Novel).filter(database.Novel.id == novel_id).first()


def get_novels(db: Session, skip: int = 0, limit: int = 100) -> List[database.Novel]:
    """Get all novels with pagination"""
    return db.query(database.Novel).offset(skip).limit(limit).all()


def update_novel_status(db: Session, novel_id: int, status: str) -> bool:
    """Update novel processing status"""
    db_novel = db.query(database.Novel).filter(database.Novel.id == novel_id).first()
    if db_novel:
        db_novel.status = database.NovelStatusEnum(status)
        db_novel.updated_at = datetime.utcnow()
        db.commit()
        return True
    return False


def delete_novel(db: Session, novel_id: int) -> bool:
    """Delete a novel"""
    db_novel = db.query(database.Novel).filter(database.Novel.id == novel_id).first()
    if db_novel:
        db.delete(db_novel)
        db.commit()
        return True
    return False


def get_novel_count(db: Session) -> int:
    """Get total number of novels"""
    return db.query(database.Novel).count()


# Chapter CRUD operations
def create_chapter(db: Session, novel_id: int, chapter_data: Dict[str, Any]) -> database.Chapter:
    """Create a new chapter"""
    db_chapter = database.Chapter(
        novel_id=novel_id,
        title=chapter_data["title"],
        content=chapter_data["content"],
        chapter_number=chapter_data["chapter_number"]
    )
    db.add(db_chapter)
    db.commit()
    db.refresh(db_chapter)
    return db_chapter


def get_chapter(db: Session, chapter_id: int) -> Optional[database.Chapter]:
    """Get a chapter by ID"""
    return db.query(database.Chapter).filter(database.Chapter.id == chapter_id).first()


def get_chapters_by_novel(db: Session, novel_id: int) -> List[database.Chapter]:
    """Get all chapters for a novel"""
    return db.query(database.Chapter).filter(
        database.Chapter.novel_id == novel_id
    ).order_by(database.Chapter.chapter_number).all()


def update_chapter_summary(
    db: Session, 
    chapter_id: int, 
    summary: str, 
    key_events: List[str], 
    characters_mentioned: List[str]
) -> bool:
    """Update chapter summary and analysis"""
    db_chapter = db.query(database.Chapter).filter(database.Chapter.id == chapter_id).first()
    if db_chapter:
        db_chapter.summary = summary
        db_chapter.key_events = key_events
        db_chapter.characters_mentioned = characters_mentioned
        db.commit()
        return True
    return False


# Character CRUD operations
def create_character(db: Session, novel_id: int, character_data: Dict[str, Any]) -> database.Character:
    """Create a new character"""
    
    # Map character type from string to enum
    character_type_mapping = {
        "protagonist": database.CharacterTypeEnum.PROTAGONIST,
        "antagonist": database.CharacterTypeEnum.ANTAGONIST,
        "supporting": database.CharacterTypeEnum.SUPPORTING,
        "minor": database.CharacterTypeEnum.MINOR
    }
    
    character_type = character_type_mapping.get(
        character_data.get("character_type", "supporting").lower(),
        database.CharacterTypeEnum.SUPPORTING
    )
    
    db_character = database.Character(
        novel_id=novel_id,
        name=character_data["name"],
        description=character_data.get("description", ""),
        character_type=character_type,
        key_traits=character_data.get("key_traits", []),
        relationships=character_data.get("relationships", [])
    )
    db.add(db_character)
    db.commit()
    db.refresh(db_character)
    return db_character


def get_character(db: Session, character_id: int) -> Optional[database.Character]:
    """Get a character by ID"""
    return db.query(database.Character).filter(database.Character.id == character_id).first()


def get_characters_by_novel(db: Session, novel_id: int) -> List[database.Character]:
    """Get all characters for a novel"""
    return db.query(database.Character).filter(
        database.Character.novel_id == novel_id
    ).order_by(database.Character.mentions_count.desc()).all()


def update_character_appearance(db: Session, character_id: int, chapter_number: int) -> bool:
    """Update character's first appearance chapter"""
    db_character = db.query(database.Character).filter(database.Character.id == character_id).first()
    if db_character and (not db_character.first_appearance_chapter or chapter_number < db_character.first_appearance_chapter):
        db_character.first_appearance_chapter = chapter_number
        db.commit()
        return True
    return False


# Chat History CRUD operations
def create_chat_history(
    db: Session, 
    novel_id: int, 
    user_message: str, 
    assistant_response: str,
    context_used: Optional[List[str]] = None
) -> database.ChatHistory:
    """Create a new chat history entry"""
    db_chat = database.ChatHistory(
        novel_id=novel_id,
        user_message=user_message,
        assistant_response=assistant_response,
        context_used=context_used or []
    )
    db.add(db_chat)
    db.commit()
    db.refresh(db_chat)
    return db_chat


def get_recent_chat_history(db: Session, novel_id: int, limit: int = 10) -> List[database.ChatHistory]:
    """Get recent chat history for a novel"""
    return db.query(database.ChatHistory).filter(
        database.ChatHistory.novel_id == novel_id
    ).order_by(database.ChatHistory.created_at.desc()).limit(limit).all()


# Analysis CRUD operations
def create_analysis(
    db: Session, 
    novel_id: int, 
    analysis_type: str, 
    results: Dict[str, Any],
    insights: Optional[List[str]] = None
) -> database.Analysis:
    """Create a new analysis entry"""
    db_analysis = database.Analysis(
        novel_id=novel_id,
        analysis_type=analysis_type,
        results=results,
        insights=insights or []
    )
    db.add(db_analysis)
    db.commit()
    db.refresh(db_analysis)
    return db_analysis


def get_analysis(db: Session, novel_id: int, analysis_type: str) -> Optional[database.Analysis]:
    """Get analysis by novel and type"""
    return db.query(database.Analysis).filter(
        database.Analysis.novel_id == novel_id,
        database.Analysis.analysis_type == analysis_type
    ).first()


def get_analyses_by_novel(db: Session, novel_id: int) -> List[database.Analysis]:
    """Get all analyses for a novel"""
    return db.query(database.Analysis).filter(
        database.Analysis.novel_id == novel_id
    ).order_by(database.Analysis.created_at.desc()).all()


# Utility functions
def search_novels(db: Session, query: str, limit: int = 10) -> List[database.Novel]:
    """Search novels by title or author"""
    return db.query(database.Novel).filter(
        database.Novel.title.contains(query) | 
        database.Novel.author.contains(query)
    ).limit(limit).all()


def get_popular_characters(db: Session, novel_id: int, limit: int = 5) -> List[database.Character]:
    """Get most mentioned characters in a novel"""
    return db.query(database.Character).filter(
        database.Character.novel_id == novel_id
    ).order_by(database.Character.mentions_count.desc()).limit(limit).all()


def update_character_mentions(db: Session, character_id: int, increment: int = 1) -> bool:
    """Update character mention count"""
    db_character = db.query(database.Character).filter(database.Character.id == character_id).first()
    if db_character:
        db_character.mentions_count += increment
        db.commit()
        return True
    return False 