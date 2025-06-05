# Novel Companion AI 📚🤖

An intelligent AI-powered companion for novel analysis, character mapping, and interactive storytelling assistance. Built with FastAPI, SQLAlchemy, and modern NLP techniques.

## ✨ Features

### 📖 Novel Management
- **Upload & Process**: Support for multiple formats (TXT, PDF, EPUB, DOCX)
- **Chapter Segmentation**: Automatic chapter detection and organization
- **Content Analysis**: Deep analysis of themes, plot structure, and writing style

### 👥 Character Analysis
- **Character Extraction**: Automatic identification of characters using NLP
- **Relationship Mapping**: Visualize character relationships and interactions
- **Character Profiles**: Detailed character descriptions and development tracking
- **Network Analysis**: Interactive character relationship networks

### 💬 Interactive Chat
- **Novel-Specific Chat**: Ask questions about specific novels
- **Context-Aware Responses**: AI responses based on novel content
- **Reference Citations**: Responses include relevant text references
- **Suggested Questions**: AI-generated follow-up questions

### 📊 Advanced Analytics
- **Theme Analysis**: Identify and analyze major themes
- **Plot Structure**: Analyze narrative structure and pacing
- **Writing Style**: Examine author's writing patterns and techniques
- **Chapter Summaries**: Generate intelligent chapter summaries

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- [uv](https://docs.astral.sh/uv/) package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/NovelVizAI.git
   cd NovelVizAI
   ```

2. **Install dependencies**
   ```bash
   uv sync
   ```

3. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your OpenRouter API key
   ```

4. **Test the installation**
   ```bash
   uv run test_setup.py
   ```

5. **Start the application**
   ```bash
   novel-companion
   ```

6. **Open your browser**
   Navigate to `http://localhost:8000`

## 🔧 Configuration

### Environment Variables

Create a `.env` file based on `env.example`:

```env
# OpenRouter API Configuration
OPENROUTER_API_KEY=your_api_key_here
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1

# Database Configuration
DATABASE_URL=sqlite:///./novel_companion.db

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=false

# File Upload Settings
MAX_FILE_SIZE=10485760  # 10MB
ALLOWED_FILE_TYPES=txt,pdf,epub,docx

# NLP Settings
SPACY_MODEL=en_core_web_sm
USE_GPU=false

# Chat Settings
MAX_CHAT_HISTORY=50
DEFAULT_MODEL=openai/gpt-3.5-turbo
```

### Getting an OpenRouter API Key

1. Visit [OpenRouter](https://openrouter.ai/)
2. Sign up for an account
3. Navigate to the API Keys section
4. Generate a new API key
5. Add it to your `.env` file

## 📚 Usage

### 1. Upload a Novel

```bash
curl -X POST "http://localhost:8000/novels/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@your_novel.txt" \
  -F "title=Your Novel Title" \
  -F "author=Author Name"
```

### 2. Analyze Characters

```bash
curl -X POST "http://localhost:8000/novels/{novel_id}/analyze/characters"
```

### 3. Chat About the Novel

```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "novel_id": 1,
    "message": "What are the main themes in this novel?"
  }'
```

### 4. Generate Chapter Summary

```bash
curl -X POST "http://localhost:8000/chapters/{chapter_id}/summarize" \
  -H "Content-Type: application/json" \
  -d '{
    "summary_length": "medium"
  }'
```

## 🏗️ Architecture

```
src/novel_companion/
├── api/                 # FastAPI routes and endpoints
│   ├── main.py         # Main FastAPI application
│   ├── novels.py       # Novel management endpoints
│   ├── characters.py   # Character analysis endpoints
│   ├── chat.py         # Chat functionality
│   └── analysis.py     # Analysis endpoints
├── models/             # Data models and schemas
│   ├── database.py     # SQLAlchemy models
│   └── schemas.py      # Pydantic schemas
├── services/           # Business logic and external services
│   ├── openrouter_client.py  # OpenRouter API client
│   ├── nlp_processor.py      # NLP processing
│   ├── file_processor.py     # File handling
│   └── analysis_service.py   # Analysis logic
├── utils/              # Utility functions
│   ├── text_processing.py    # Text utilities
│   └── visualization.py      # Data visualization
└── config.py           # Configuration management
```

## 🧪 Testing

Run the test suite:

```bash
# Run setup verification
uv run test_setup.py

# Run unit tests (when available)
uv run pytest

# Run with coverage
uv run pytest --cov=novel_companion
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup

```bash
# Install development dependencies
uv sync --dev

# Install pre-commit hooks
pre-commit install

# Run linting
uv run ruff check .
uv run ruff format .

# Run type checking
uv run mypy src/
```

## 📄 API Documentation

Once the server is running, visit:
- **Interactive API Docs**: `http://localhost:8000/docs`
- **ReDoc Documentation**: `http://localhost:8000/redoc`
- **OpenAPI Schema**: `http://localhost:8000/openapi.json`

## 🔍 Supported File Formats

- **TXT**: Plain text files
- **PDF**: Portable Document Format
- **EPUB**: Electronic Publication format
- **DOCX**: Microsoft Word documents

## 🎯 Roadmap

- [ ] **Enhanced NLP**: Support for multiple languages
- [ ] **Advanced Visualizations**: Interactive plot diagrams
- [ ] **Export Features**: PDF reports and visualizations
- [ ] **Collaborative Features**: Multi-user novel analysis
- [ ] **Plugin System**: Extensible analysis modules
- [ ] **Mobile App**: React Native companion app

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) for the excellent web framework
- [spaCy](https://spacy.io/) for natural language processing
- [OpenRouter](https://openrouter.ai/) for AI model access
- [SQLAlchemy](https://sqlalchemy.org/) for database management

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/NovelVizAI/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/NovelVizAI/discussions)

---

Made with ❤️ for writers, readers, and literature enthusiasts.
