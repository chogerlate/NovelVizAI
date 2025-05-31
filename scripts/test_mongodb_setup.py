#!/usr/bin/env python3
"""
Test script to verify MongoDB setup and basic operations
"""

import asyncio
import sys
import os
from pathlib import Path

# Add src to path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from novel_companion.models.mongodb_connection import (
    connect_to_mongodb, 
    disconnect_from_mongodb,
    get_novel_by_title,
    search_novels
)
from novel_companion.models.data_migration import DataMigration
from novel_companion.models.mongodb_operations import (
    NovelOperations,
    AnalyticsOperations
)


async def test_mongodb_setup():
    """Test MongoDB setup and basic operations"""
    
    print("🧪 Testing MongoDB Setup for Novel Companion AI")
    print("=" * 50)
    
    try:
        # Connect to MongoDB
        print("📡 Connecting to MongoDB...")
        await connect_to_mongodb()
        print("✅ Connected successfully!")
        
        # Test 1: Create sample data
        print("\n📝 Test 1: Creating sample data...")
        result = await DataMigration.create_sample_data()
        print(f"✅ Sample data created: {result['message']}")
        print(f"   Novel ID: {result['novel_id']}")
        print(f"   Chapters: {len(result['chapter_ids'])}")
        print(f"   Characters: {len(result['character_ids'])}")
        
        # Test 2: Search novels
        print("\n🔍 Test 2: Searching novels...")
        novels = await search_novels(query="fantasy", limit=5)
        print(f"✅ Found {len(novels)} novels matching 'fantasy'")
        for novel in novels:
            print(f"   - {novel.title} by {novel.author}")
        
        # Test 3: Get novel by title
        print("\n🎯 Test 3: Getting novel by title...")
        novel = await get_novel_by_title("Sample Fantasy Novel")
        if novel:
            print(f"✅ Found novel: {novel.title}")
            print(f"   Author: {novel.author}")
            print(f"   Genres: {', '.join(novel.genres)}")
            print(f"   Rating: {novel.average_rating}")
        
        # Test 4: Get top rated novels
        print("\n⭐ Test 4: Getting top rated novels...")
        top_novels = await NovelOperations.get_top_rated_novels(limit=3)
        print(f"✅ Found {len(top_novels)} top rated novels:")
        for novel in top_novels:
            print(f"   - {novel.title}: {novel.average_rating}⭐")
        
        # Test 5: Get novel statistics
        print("\n📊 Test 5: Getting novel statistics...")
        if novel:
            stats = await AnalyticsOperations.get_novel_statistics(str(novel.id))
            if stats:
                print("✅ Novel statistics:")
                print(f"   Title: {stats['title']}")
                print(f"   Chapters: {stats['chapter_count']}")
                print(f"   Characters: {stats['character_count']}")
                print(f"   Total words: {stats['total_words']}")
                print(f"   Avg chapter length: {stats['average_chapter_length']} words")
        
        # Test 6: Data validation
        print("\n🔍 Test 6: Validating data integrity...")
        validation = await DataMigration.validate_data_integrity()
        print(f"✅ Validation complete:")
        print(f"   Total novels: {validation['total_novels']}")
        print(f"   Total chapters: {validation['total_chapters']}")
        print(f"   Total characters: {validation['total_characters']}")
        print(f"   Issues found: {validation['issues_found']}")
        if validation['issues']:
            for issue in validation['issues']:
                print(f"   ⚠️ {issue}")
        
        print("\n🎉 All tests completed successfully!")
        print("✅ MongoDB setup is working correctly!")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Disconnect from MongoDB
        print("\n🔌 Disconnecting from MongoDB...")
        await disconnect_from_mongodb()
        
    return True


async def test_import_your_data():
    """Test importing your novel metadata"""
    
    print("\n" + "=" * 50)
    print("📥 Testing import of your novel metadata")
    print("=" * 50)
    
    # Check if your JSON file exists
    json_path = "data/novels/novel_meta_data.json"
    if not os.path.exists(json_path):
        print(f"⚠️ Novel metadata file not found: {json_path}")
        print("   This test will be skipped.")
        return
    
    try:
        await connect_to_mongodb()
        
        print(f"📁 Found novel metadata file: {json_path}")
        print("📥 Importing your novel data...")
        
        imported_ids = await DataMigration.import_novels_from_json(json_path)
        
        if imported_ids:
            print(f"✅ Successfully imported {len(imported_ids)} novels!")
            
            # Test search on imported data
            print("\n🔍 Testing search on imported data...")
            korean_novels = await search_novels(limit=5)
            print(f"✅ Found {len(korean_novels)} novels total")
            for novel in korean_novels[:3]:  # Show first 3
                print(f"   - {novel.title} ({novel.original_language})")
        else:
            print("⚠️ No novels were imported")
            
    except Exception as e:
        print(f"❌ Error during import test: {e}")
    
    finally:
        await disconnect_from_mongodb()


async def main():
    """Main test function"""
    print("🚀 Starting MongoDB Setup Tests")
    
    # Test basic setup
    success = await test_mongodb_setup()
    
    if success:
        # Test importing your actual data
        await test_import_your_data()
    
    print("\n" + "=" * 50)
    print("🏁 Testing completed!")


if __name__ == "__main__":
    asyncio.run(main()) 