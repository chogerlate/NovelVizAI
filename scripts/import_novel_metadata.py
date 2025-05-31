#!/usr/bin/env python3
"""
Script to import novel metadata from JSON into MongoDB
"""

import asyncio
import sys
import os
from pathlib import Path

# Add src to path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from novel_companion.models.mongodb_connection import connect_to_mongodb, disconnect_from_mongodb
from novel_companion.models.data_migration import DataMigration


async def main():
    """Main function to import novel metadata"""
    
    # Default path to the novel metadata file
    default_json_path = "data/novels/novel_meta_data.json"
    
    # Allow custom path as command line argument
    json_path = sys.argv[1] if len(sys.argv) > 1 else default_json_path
    
    if not os.path.exists(json_path):
        print(f"❌ JSON file not found: {json_path}")
        print(f"Usage: python {sys.argv[0]} [path_to_json_file]")
        sys.exit(1)
    
    print(f"🚀 Starting import from: {json_path}")
    print("📡 Connecting to MongoDB...")
    
    try:
        # Connect to MongoDB
        await connect_to_mongodb()
        
        # Import novels from JSON
        print("📥 Importing novel metadata...")
        imported_ids = await DataMigration.import_novels_from_json(json_path)
        
        if imported_ids:
            print(f"\n🎉 Successfully imported {len(imported_ids)} novels!")
            print("📋 Novel IDs:")
            for i, novel_id in enumerate(imported_ids, 1):
                print(f"  {i}. {novel_id}")
        else:
            print("\n❌ No novels were imported.")
    
    except Exception as e:
        print(f"❌ Error during import: {e}")
        sys.exit(1)
    
    finally:
        # Disconnect from MongoDB
        print("\n🔌 Disconnecting from MongoDB...")
        await disconnect_from_mongodb()
        print("✅ Import completed!")


if __name__ == "__main__":
    asyncio.run(main()) 