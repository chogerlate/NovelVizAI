"""
Configuration management for Novel Companion AI
"""

import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""
    
    # API Configuration
    openrouter_api_key: str = ""
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    deepseek_model: str = "deepseek/deepseek-r1:free"
    
    # Server Configuration
    host: str = "localhost"
    port: int = 8000
    debug: bool = True
    
    # Database Configuration (SQLite - legacy)
    database_url: str = "sqlite:///./novel_companion.db"
    
    # MongoDB Configuration
    mongodb_url: str = "mongodb://localhost:27017"
    mongodb_database: str = "novel_companion"
    mongodb_novels_collection: str = "novels"
    mongodb_chapters_collection: str = "chapters"
    
    # File Upload Configuration
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    upload_directory: str = "./uploads"
    allowed_file_types: str = "txt,pdf,epub,docx"
    
    # NLP Configuration
    spacy_model: str = "en_core_web_sm"
    max_chunk_size: int = 4000  # For text processing
    use_gpu: bool = False
    
    # Application Settings
    log_level: str = "INFO"
    
    # Chat Settings
    max_chat_history: int = 50
    default_model: str = "openai/gpt-3.5-turbo"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings() 