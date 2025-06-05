"""
MongoDB operations and example queries for Novel Companion AI
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

from .mongodb_models import Novel, Chapter, Character, ChatHistory, Analysis


class NovelOperations:
    """Operations for Novel collection"""
    
    @staticmethod
    async def create_novel(novel_data: dict) -> Novel:
        """Create a new novel"""
        novel = Novel(**novel_data)
        return await novel.insert()
    
    @staticmethod
    async def update_novel(novel_id: str, update_data: dict) -> Optional[Novel]:
        """Update a novel"""
        novel = await Novel.get(novel_id)
        if novel:
            for key, value in update_data.items():
                setattr(novel, key, value)
            novel.last_updated = datetime.utcnow()
            await novel.save()
            return novel
        return None
    
    @staticmethod
    async def delete_novel(novel_id: str) -> bool:
        """Delete a novel and all related data"""
        try:
            # Delete related chapters
            await Chapter.find(Chapter.novel_id == novel_id).delete()
            
            # Delete related characters
            await Character.find(Character.novel_id == novel_id).delete()
            
            # Delete related chat history
            await ChatHistory.find(ChatHistory.novel_id == novel_id).delete()
            
            # Delete related analyses
            await Analysis.find(Analysis.novel_id == novel_id).delete()
            
            # Delete the novel
            novel = await Novel.get(novel_id)
            if novel:
                await novel.delete()
                return True
            return False
        except Exception:
            return False
    
    @staticmethod
    async def get_novels_by_genre(genre: str, limit: int = 20) -> List[Novel]:
        """Get novels by genre"""
        return await Novel.find(Novel.genres.in_([genre])).limit(limit).to_list()
    
    @staticmethod
    async def get_novels_by_rating_range(min_rating: float, max_rating: float = 5.0) -> List[Novel]:
        """Get novels within rating range"""
        return await Novel.find(
            Novel.average_rating >= min_rating,
            Novel.average_rating <= max_rating
        ).to_list()
    
    @staticmethod
    async def get_top_rated_novels(limit: int = 10) -> List[Novel]:
        """Get top rated novels"""
        return await Novel.find(
            Novel.average_rating != None
        ).sort(-Novel.average_rating).limit(limit).to_list()
    
    @staticmethod
    async def get_novels_by_year_range(start_year: int, end_year: int) -> List[Novel]:
        """Get novels published in year range"""
        return await Novel.find(
            Novel.year >= start_year,
            Novel.year <= end_year
        ).to_list()
    
    @staticmethod
    async def get_completed_novels() -> List[Novel]:
        """Get completed novels"""
        return await Novel.find(Novel.status_in_coo == "Completed").to_list()


class ChapterOperations:
    """Operations for Chapter collection"""
    
    @staticmethod
    async def create_chapter(chapter_data: dict) -> Chapter:
        """Create a new chapter"""
        chapter = Chapter(**chapter_data)
        return await chapter.insert()
    
    @staticmethod
    async def get_chapter_by_number(novel_id: str, chapter_number: int) -> Optional[Chapter]:
        """Get specific chapter by number"""
        return await Chapter.find_one(
            Chapter.novel_id == novel_id,
            Chapter.chapter_number == chapter_number
        )
    
    @staticmethod
    async def update_chapter_analysis(chapter_id: str, analysis_data: dict) -> Optional[Chapter]:
        """Update chapter with analysis results"""
        chapter = await Chapter.get(chapter_id)
        if chapter:
            for key, value in analysis_data.items():
                setattr(chapter, key, value)
            chapter.is_processed = True
            chapter.processing_timestamp = datetime.utcnow()
            chapter.updated_at = datetime.utcnow()
            await chapter.save()
            return chapter
        return None
    
    @staticmethod
    async def get_unprocessed_chapters(limit: int = 100) -> List[Chapter]:
        """Get chapters that haven't been processed yet"""
        return await Chapter.find(
            Chapter.is_processed == False
        ).limit(limit).to_list()
    
    @staticmethod
    async def get_chapters_with_character(novel_id: str, character_name: str) -> List[Chapter]:
        """Get chapters where a specific character is mentioned"""
        return await Chapter.find(
            Chapter.novel_id == novel_id,
            Chapter.characters_mentioned.in_([character_name])
        ).to_list()
    
    @staticmethod
    async def search_chapters_by_content(novel_id: str, search_term: str) -> List[Chapter]:
        """Search chapters by content"""
        return await Chapter.find(
            Chapter.novel_id == novel_id,
            {"$text": {"$search": search_term}}
        ).to_list()


class CharacterOperations:
    """Operations for Character collection"""
    
    @staticmethod
    async def create_character(character_data: dict) -> Character:
        """Create a new character"""
        character = Character(**character_data)
        return await character.insert()
    
    @staticmethod
    async def update_character_mentions(character_id: str, chapter_number: int) -> Optional[Character]:
        """Update character mentions count and chapters appeared"""
        character = await Character.get(character_id)
        if character:
            character.mentions_count += 1
            if chapter_number not in character.chapters_appeared:
                character.chapters_appeared.append(chapter_number)
            character.updated_at = datetime.utcnow()
            await character.save()
            return character
        return None
    
    @staticmethod
    async def get_main_characters(novel_id: str) -> List[Character]:
        """Get main characters (protagonist and antagonist)"""
        return await Character.find(
            Character.novel_id == novel_id,
            Character.character_type.in_(["protagonist", "antagonist"])
        ).to_list()
    
    @staticmethod
    async def get_most_mentioned_characters(novel_id: str, limit: int = 10) -> List[Character]:
        """Get most frequently mentioned characters"""
        return await Character.find(
            Character.novel_id == novel_id
        ).sort(-Character.mentions_count).limit(limit).to_list()


class AnalyticsOperations:
    """Analytics and aggregation operations"""
    
    @staticmethod
    async def get_novel_statistics(novel_id: str) -> Dict[str, Any]:
        """Get comprehensive statistics for a novel"""
        try:
            # Get novel
            novel = await Novel.get(novel_id)
            if not novel:
                return {}
            
            # Count chapters
            chapter_count = await Chapter.find(Chapter.novel_id == novel_id).count()
            
            # Count characters
            character_count = await Character.find(Character.novel_id == novel_id).count()
            
            # Get total word count
            pipeline = [
                {"$match": {"novel_id": novel_id}},
                {"$group": {"_id": None, "total_words": {"$sum": "$word_count"}}}
            ]
            word_count_result = await Chapter.aggregate(pipeline).to_list(1)
            total_words = word_count_result[0]["total_words"] if word_count_result else 0
            
            # Get average chapter length
            avg_word_count = total_words / chapter_count if chapter_count > 0 else 0
            
            # Get character type distribution
            character_pipeline = [
                {"$match": {"novel_id": novel_id}},
                {"$group": {"_id": "$character_type", "count": {"$sum": 1}}}
            ]
            character_distribution = await Character.aggregate(character_pipeline).to_list()
            
            return {
                "novel_id": novel_id,
                "title": novel.title,
                "author": novel.author,
                "chapter_count": chapter_count,
                "character_count": character_count,
                "total_words": total_words,
                "average_chapter_length": round(avg_word_count, 2),
                "character_type_distribution": {item["_id"]: item["count"] for item in character_distribution},
                "genres": novel.genres,
                "tags": novel.tags,
                "average_rating": novel.average_rating,
                "created_at": novel.created_at
            }
        except Exception as e:
            print(f"Error getting novel statistics: {e}")
            return {}
    
    @staticmethod
    async def get_reading_progress(novel_id: str, current_chapter: int) -> Dict[str, Any]:
        """Get reading progress statistics"""
        try:
            total_chapters = await Chapter.find(Chapter.novel_id == novel_id).count()
            progress_percentage = (current_chapter / total_chapters * 100) if total_chapters > 0 else 0
            
            return {
                "current_chapter": current_chapter,
                "total_chapters": total_chapters,
                "progress_percentage": round(progress_percentage, 2),
                "chapters_remaining": total_chapters - current_chapter
            }
        except Exception:
            return {}
    
    @staticmethod
    async def get_popular_genres() -> List[Dict[str, Any]]:
        """Get most popular genres across all novels"""
        try:
            pipeline = [
                {"$unwind": "$genres"},
                {"$group": {"_id": "$genres", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}},
                {"$limit": 20}
            ]
            return await Novel.aggregate(pipeline).to_list()
        except Exception:
            return []
    
    @staticmethod
    async def get_recently_updated_novels(days: int = 7, limit: int = 10) -> List[Novel]:
        """Get recently updated novels"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        return await Novel.find(
            Novel.last_updated >= cutoff_date
        ).sort(-Novel.last_updated).limit(limit).to_list()


# Example usage and sample queries
class SampleQueries:
    """Sample MongoDB queries for reference"""
    
    @staticmethod
    async def complex_novel_search():
        """Example of complex novel search"""
        # Find Korean fantasy novels with rating > 4.0, published after 2015
        novels = await Novel.find(
            Novel.original_language == "Korean",
            Novel.genres.in_(["Fantasy"]),
            Novel.average_rating > 4.0,
            Novel.year > 2015
        ).sort(-Novel.average_rating).to_list()
        
        return novels
    
    @staticmethod
    async def character_relationship_analysis(novel_id: str):
        """Analyze character relationships in a novel"""
        characters = await Character.find(
            Character.novel_id == novel_id,
            Character.relationships != []
        ).to_list()
        
        # Build relationship graph
        relationships = {}
        for char in characters:
            relationships[char.name] = char.relationships
            
        return relationships
    
    @staticmethod
    async def chapter_sentiment_analysis(novel_id: str):
        """Get sentiment progression through chapters"""
        chapters = await Chapter.find(
            Chapter.novel_id == novel_id,
            Chapter.sentiment_score != None
        ).sort("chapter_number").to_list()
        
        sentiment_progression = [
            {
                "chapter": ch.chapter_number,
                "title": ch.title,
                "sentiment": ch.sentiment_score
            }
            for ch in chapters
        ]
        
        return sentiment_progression


# Export all operation classes
__all__ = [
    "NovelOperations",
    "ChapterOperations", 
    "CharacterOperations",
    "AnalyticsOperations",
    "SampleQueries"
] 