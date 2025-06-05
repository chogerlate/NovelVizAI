"""
Data migration utilities for importing novel data into MongoDB
"""

import json
import asyncio
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

from .mongodb_models import Novel, Chapter, Character
from .mongodb_connection import connect_to_mongodb, disconnect_from_mongodb


class DataMigration:
    """Data migration utilities"""
    
    @staticmethod
    async def import_novels_from_json(json_file_path: str) -> List[str]:
        """Import novels from JSON file"""
        imported_ids = []
        
        try:
            with open(json_file_path, 'r', encoding='utf-8') as file:
                novels_data = json.load(file)
            
            if not isinstance(novels_data, list):
                novels_data = [novels_data]
            
            for novel_data in novels_data:
                try:
                    # Remove MongoDB ObjectId() placeholder if present
                    if '_id' in novel_data:
                        del novel_data['_id']
                    
                    # Convert ISODate strings to datetime objects
                    if 'lastUpdated' in novel_data:
                        if isinstance(novel_data['lastUpdated'], str):
                            novel_data['lastUpdated'] = datetime.fromisoformat(
                                novel_data['lastUpdated'].replace('Z', '+00:00')
                            )
                    
                    # Create novel
                    novel = Novel(**novel_data)
                    saved_novel = await novel.insert()
                    imported_ids.append(str(saved_novel.id))
                    
                    print(f"✅ Imported novel: {novel_data.get('title', 'Unknown')}")
                    
                except Exception as e:
                    print(f"❌ Failed to import novel {novel_data.get('title', 'Unknown')}: {e}")
                    continue
            
            print(f"\n✅ Import completed. {len(imported_ids)} novels imported successfully.")
            return imported_ids
            
        except Exception as e:
            print(f"❌ Error reading JSON file: {e}")
            return []
    
    @staticmethod
    async def import_chapters_from_text_files(
        novel_id: str, 
        chapters_directory: str,
        chapter_pattern: str = "chapter_*.txt"
    ) -> List[str]:
        """Import chapters from text files"""
        imported_ids = []
        chapters_path = Path(chapters_directory)
        
        if not chapters_path.exists():
            print(f"❌ Chapters directory not found: {chapters_directory}")
            return []
        
        # Find chapter files
        chapter_files = list(chapters_path.glob(chapter_pattern))
        chapter_files.sort()  # Sort to maintain order
        
        for i, chapter_file in enumerate(chapter_files, 1):
            try:
                with open(chapter_file, 'r', encoding='utf-8') as file:
                    content = file.read()
                
                # Extract title from filename or content
                title = chapter_file.stem.replace('_', ' ').title()
                if content.startswith('#'):
                    # Try to extract title from first line if it's a header
                    first_line = content.split('\n')[0]
                    if first_line.startswith('#'):
                        title = first_line.strip('#').strip()
                        content = '\n'.join(content.split('\n')[1:]).strip()
                
                # Calculate word count
                word_count = len(content.split())
                reading_time = max(1, word_count // 200)  # Assume 200 words per minute
                
                chapter_data = {
                    "novel_id": novel_id,
                    "title": title,
                    "chapter_number": i,
                    "content": content,
                    "word_count": word_count,
                    "reading_time_minutes": reading_time,
                    "is_processed": False
                }
                
                chapter = Chapter(**chapter_data)
                saved_chapter = await chapter.insert()
                imported_ids.append(str(saved_chapter.id))
                
                print(f"✅ Imported chapter {i}: {title}")
                
            except Exception as e:
                print(f"❌ Failed to import chapter from {chapter_file}: {e}")
                continue
        
        print(f"\n✅ Chapter import completed. {len(imported_ids)} chapters imported.")
        return imported_ids
    
    @staticmethod
    async def create_sample_data() -> Dict[str, Any]:
        """Create sample data for testing"""
        # Sample novel data
        sample_novel = {
            "title": "Sample Fantasy Novel",
            "type": "Web Novel",
            "original_language": "English",
            "author": "Sample Author",
            "description": "A sample fantasy novel for testing the MongoDB setup.",
            "genres": ["Fantasy", "Adventure", "Magic"],
            "tags": ["Magic System", "Heroes", "Quest"],
            "average_rating": 4.5,
            "vote_count": 100,
            "year": 2024,
            "status_in_coo": "Ongoing",
            "is_completely_translated": True
        }
        
        # Create novel
        novel = Novel(**sample_novel)
        saved_novel = await novel.insert()
        novel_id = str(saved_novel.id)
        
        # Sample chapters
        sample_chapters = [
            {
                "novel_id": novel_id,
                "title": "The Beginning",
                "chapter_number": 1,
                "content": "In a world where magic flows like rivers and heroes are born from legends...",
                "word_count": 2500,
                "reading_time_minutes": 13,
                "key_events": ["Hero's introduction", "Magic discovery"],
                "characters_mentioned": ["Alex", "Mentor"],
                "is_processed": True
            },
            {
                "novel_id": novel_id,
                "title": "First Trial",
                "chapter_number": 2,
                "content": "The first trial tested not just strength, but the hero's resolve...",
                "word_count": 3000,
                "reading_time_minutes": 15,
                "key_events": ["First trial", "New abilities"],
                "characters_mentioned": ["Alex", "Trial Master"],
                "is_processed": True
            }
        ]
        
        chapter_ids = []
        for chapter_data in sample_chapters:
            chapter = Chapter(**chapter_data)
            saved_chapter = await chapter.insert()
            chapter_ids.append(str(saved_chapter.id))
        
        # Sample characters
        sample_characters = [
            {
                "novel_id": novel_id,
                "name": "Alex",
                "description": "The protagonist, a young mage discovering their powers",
                "character_type": "protagonist",
                "first_appearance_chapter": 1,
                "key_traits": ["brave", "curious", "magical talent"],
                "mentions_count": 15,
                "chapters_appeared": [1, 2]
            },
            {
                "novel_id": novel_id,
                "name": "Mentor",
                "description": "Wise old wizard who guides Alex",
                "character_type": "supporting",
                "first_appearance_chapter": 1,
                "key_traits": ["wise", "experienced", "patient"],
                "mentions_count": 8,
                "chapters_appeared": [1]
            }
        ]
        
        character_ids = []
        for character_data in sample_characters:
            character = Character(**character_data)
            saved_character = await character.insert()
            character_ids.append(str(saved_character.id))
        
        return {
            "novel_id": novel_id,
            "chapter_ids": chapter_ids,
            "character_ids": character_ids,
            "message": "Sample data created successfully"
        }
    
    @staticmethod
    async def validate_data_integrity() -> Dict[str, Any]:
        """Validate data integrity across collections"""
        issues = []
        
        # Check for orphaned chapters
        all_novels = await Novel.find_all().to_list()
        novel_ids = [str(novel.id) for novel in all_novels]
        
        all_chapters = await Chapter.find_all().to_list()
        for chapter in all_chapters:
            if str(chapter.novel_id) not in novel_ids:
                issues.append(f"Orphaned chapter: {chapter.title} (ID: {chapter.id})")
        
        # Check for orphaned characters
        all_characters = await Character.find_all().to_list()
        for character in all_characters:
            if str(character.novel_id) not in novel_ids:
                issues.append(f"Orphaned character: {character.name} (ID: {character.id})")
        
        # Check for missing required fields
        for novel in all_novels:
            if not novel.title:
                issues.append(f"Novel missing title (ID: {novel.id})")
        
        return {
            "total_novels": len(all_novels),
            "total_chapters": len(all_chapters),
            "total_characters": len(all_characters),
            "issues_found": len(issues),
            "issues": issues
        }
    
    @staticmethod
    async def export_novels_to_json(output_file: str) -> bool:
        """Export all novels to JSON file"""
        try:
            novels = await Novel.find_all().to_list()
            novels_data = []
            
            for novel in novels:
                novel_dict = novel.dict(by_alias=True)
                # Convert ObjectId to string
                novel_dict['_id'] = str(novel.id)
                # Convert datetime to ISO string
                if 'lastUpdated' in novel_dict:
                    novel_dict['lastUpdated'] = novel_dict['lastUpdated'].isoformat()
                if 'created_at' in novel_dict:
                    novel_dict['created_at'] = novel_dict['created_at'].isoformat()
                
                novels_data.append(novel_dict)
            
            with open(output_file, 'w', encoding='utf-8') as file:
                json.dump(novels_data, file, indent=2, ensure_ascii=False)
            
            print(f"✅ Exported {len(novels_data)} novels to {output_file}")
            return True
            
        except Exception as e:
            print(f"❌ Export failed: {e}")
            return False


# CLI helper functions
async def run_migration():
    """Run data migration from command line"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python -m data_migration [import|sample|validate|export]")
        return
    
    command = sys.argv[1]
    
    await connect_to_mongodb()
    
    try:
        if command == "import" and len(sys.argv) > 2:
            json_file = sys.argv[2]
            await DataMigration.import_novels_from_json(json_file)
        
        elif command == "sample":
            result = await DataMigration.create_sample_data()
            print(f"Sample data created: {result}")
        
        elif command == "validate":
            result = await DataMigration.validate_data_integrity()
            print(f"Validation results: {result}")
        
        elif command == "export" and len(sys.argv) > 2:
            output_file = sys.argv[2]
            await DataMigration.export_novels_to_json(output_file)
        
        else:
            print("Invalid command or missing arguments")
    
    finally:
        await disconnect_from_mongodb()


if __name__ == "__main__":
    asyncio.run(run_migration()) 