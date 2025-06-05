# MongoDB Setup Guide for Novel Companion AI

This guide will help you set up MongoDB for the Novel Companion AI project, which uses several collections to store novel data, chapter content, and comprehensive analysis results.

## Prerequisites

1. **MongoDB Installation**
   ```bash
   # Ubuntu/Debian
   sudo apt-get install mongodb
   
   # macOS with Homebrew
   brew install mongodb-community
   
   # Or use Docker
   docker run -d -p 27017:27017 --name mongodb mongo:latest
   ```

2. **Python Dependencies**
   ```bash
   # Install additional MongoDB dependencies
   uv add motor pymongo beanie pydantic
   ```

## Database Structure

### Collections

1. **novels** - Stores novel metadata
2. **chapters** - Stores chapter content and comprehensive analysis
3. **characters** - Stores detailed character information and relationships
4. **chat_history** - Stores user chat interactions
5. **analyses** - Stores AI analysis results

### Novel Document Schema

```json
{
  "_id": "ObjectId",
  "title": "Novel Title",
  "type": "Web Novel",
  "originalLanguage": "Korean",
  "author": "Author Name",
  "artist": "Artist Name",
  "description": "Novel description...",
  "genres": ["Action", "Fantasy"],
  "tags": ["Magic", "Adventure"],
  "averageRating": 4.6,
  "voteCount": 2298,
  "year": 2018,
  "statusInCOO": "Completed",
  "chaptersInCOO": {
    "mainStory": 516,
    "epilogue": 35,
    "sideStories": 299
  },
  "isCompletelyTranslated": true,
  "originalPublisher": ["Munpia", "Naver"],
  "englishPublisher": ["Ize Press"],
  "associatedNames": ["ORV", "전독시"],
  "relatedSeries": [
    {
      "title": "Related Novel",
      "relation": "Sequel"
    }
  ],
  "lastUpdated": "2025-01-24T10:30:00Z",
  "createdAt": "2025-01-24T10:30:00Z"
}
```

### Chapter Document Schema with Analysis Data

```json
{
  "_id": "ObjectId",
  "novelId": "ObjectId (reference to novel)",
  "title": "Chapter Title",
  "chapterNumber": 1,
  "content": "Chapter content text...",
  "summary": "AI-generated summary",
  "analysis_data": {
    "chapter_analysis": {
      "metadata": {
        "novel_id": "string",
        "chapter_id": "string",
        "novel_title": "string",
        "chapter_number": 1,
        "chapter_title": "string",
        "word_count": 2500,
        "estimated_reading_time": 13
      },
      "summary": {
        "concise": "Brief chapter summary",
        "detailed": "Detailed chapter analysis",
        "key_events": ["Event 1", "Event 2"]
      },
      "sentiment_analysis": {
        "overall_tone": "Positive",
        "emotional_arc": [
          {
            "emotion": "Hope",
            "intensity": 0.8
          }
        ],
        "character_sentiments": {
          "Character Name": {
            "dominant_emotions": ["Determined", "Anxious"],
            "emotional_state": "Complex"
          }
        }
      },
      "themes": [
        {
          "theme": "Redemption",
          "relevance": 0.9,
          "evidence": "Supporting text from chapter"
        }
      ],
      "literary_elements": {
        "narrative_voice": "Third Person Limited",
        "foreshadowing": [
          {
            "text": "Relevant quote",
            "significance": "Hints at future event"
          }
        ],
        "symbolism": [
          {
            "symbol": "Object or concept",
            "meaning": "Symbolic interpretation"
          }
        ]
      }
    },
    "character_mapping": {
      "characters": [
        {
          "name": "Character Name",
          "role": "Protagonist",
          "first_appearance": "Chapter reference",
          "description": "Character description",
          "key_traits": ["Brave", "Intelligent"],
          "quotes": ["Memorable quote"],
          "development_status": "Evolving"
        }
      ],
      "relationships": [
        {
          "characters": ["Character A", "Character B"],
          "relationship_type": "Allies",
          "dynamics": "Complex",
          "significance": "Plot-critical",
          "interaction_count": 5,
          "sentiment": "Positive"
        }
      ]
    },
    "interactive_companion": {
      "chapter_context": {
        "setting": "Location and time",
        "timeline_position": "Early story",
        "narrative_importance": "High"
      },
      "key_question": [
        "Discussion question about chapter"
      ],
      "suggested_discussion_point": [
        "Topic for reader engagement"
      ]
    },
    "reading_analytics": {
      "complexity_metrics": {
        "readability_score": 75,
        "vocabulary_level": "Advanced",
        "structural_complexity": "Moderate"
      },
      "pacing_analysis": {
        "overall_pace": "Fast",
        "significant_shifts": [
          {
            "position": "Mid-chapter",
            "change": "Acceleration"
          }
        ]
      },
      "engagement_factors": {
        "hook": ["Opening hook description"],
        "engagement_score": 8.5
      }
    }
  },
  "keyEvents": ["Event 1", "Event 2"],
  "charactersMentioned": ["Character A", "Character B"],
  "themes": ["friendship", "adventure"],
  "sentimentScore": 0.75,
  "wordCount": 2500,
  "readingTimeMinutes": 13,
  "isProcessed": true,
  "processingTimestamp": "2025-01-24T10:30:00Z",
  "createdAt": "2025-01-24T10:30:00Z",
  "updatedAt": "2025-01-24T10:30:00Z"
}
```

## API Endpoints

### Chapter Analysis Endpoints

1. **Get Chapters List**
   ```http
   GET /api/novels/{novel_id}/chapters?skip=0&limit=100&include_content=false
   ```
   - Returns paginated list of chapters with analysis
   - `include_content=false` omits full chapter text for lighter responses

2. **Get Single Chapter**
   ```http
   GET /api/chapters/{chapter_id}?include_content=true
   ```
   - Returns complete chapter data with analysis
   - `include_content=true` includes full chapter text

### Response Models

The API uses Pydantic models for validation and serialization:

```python
class ChapterResponse(BaseModel):
    id: str
    novel_id: str
    title: str
    chapter_number: int
    content: Optional[str] = None
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
```

## Configuration

1. **Environment Variables**
   
   Copy `.env.example` to `.env` and configure MongoDB settings:
   ```bash
   MONGODB_URL=mongodb://localhost:27017
   MONGODB_DATABASE=novel_companion
   MONGODB_NOVELS_COLLECTION=novels
   MONGODB_CHAPTERS_COLLECTION=chapters
   ```

2. **Connection Setup**
   ```python
   from novel_companion.models.mongodb_connection import connect_to_mongodb
   
   # Connect to MongoDB
   await connect_to_mongodb()
   ```

## Data Import/Export

### Import Novel Data

```python
from novel_companion.models.data_migration import DataMigration

# Import from JSON
await DataMigration.import_novels_from_json("path/to/novels.json")

# Import chapters with analysis
await DataMigration.import_chapters_from_text_files(
    novel_id="novel_object_id",
    chapters_directory="path/to/chapters/",
    chapter_pattern="chapter_*.txt"
)
```

### Export Data

```python
# Export novels and analysis to JSON
await DataMigration.export_novels_to_json("backup_novels.json")
await DataMigration.export_chapters_to_json("backup_chapters.json")
```

## Indexes

The system creates these indexes for optimal performance:

### Novel Collection Indexes
- Text index on `title`
- Index on `author`, `genres`, `tags`
- Index on `averageRating`, `year`, `statusInCOO`

### Chapter Collection Indexes
- Index on `novelId`, `chapterNumber`
- Compound unique index on `(novelId, chapterNumber)`
- Text index on `title`
- Index on `isProcessed`, `processingTimestamp`

## Performance Optimization

1. **Query Optimization**
   - Use `include_content=false` for chapter lists
   - Implement pagination for large result sets
   - Use projection to limit returned fields

2. **Analysis Data Handling**
   - Analysis data is stored as nested documents
   - Use safe parsing with error handling
   - Optional fields reduce storage requirements

3. **Connection Pooling**
   - Motor handles connection pooling automatically
   - Configure pool size based on load

## Security Considerations

1. **Data Validation**
   - All inputs validated through Pydantic models
   - Flexible schema with ConfigDict settings
   - Safe parsing of analysis data

2. **Error Handling**
   - Graceful fallback for parsing errors
   - Detailed error logging
   - Safe default values for missing fields

## Production Deployment

For production environments:

1. **MongoDB Atlas Setup**
   ```bash
   MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/novel_companion
   ```

2. **Data Backup**
   ```bash
   # Backup MongoDB database
   mongodump --db novel_companion --out backup/
   
   # Restore MongoDB database
   mongorestore backup/novel_companion/
   ```

3. **Monitoring**
   - Monitor analysis processing status
   - Track API response times
   - Set up alerts for processing failures 