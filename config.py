import os
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import List, Optional

class Settings(BaseSettings):
    # API Configuration
    anthropic_api_key: str
    
    # Flask Configuration
    flask_env: str = "development"
    flask_debug: bool = True
    secret_key: str = "dev-secret-key-change-in-production"
    
    # Database Configuration
    database_url: str = "sqlite:///ai_rag_bot.db"
    
    # RAG Configuration
    vector_db_path: str = "./data/vector_db"
    max_chunk_size: int = 1000
    chunk_overlap: int = 200
    max_documents: int = 1000
    embedding_model: str = "all-MiniLM-L6-v2"
    
    # Chat Configuration
    max_conversation_history: int = 50
    default_model: str = "claude-3-sonnet-20240229"
    max_tokens: int = 4000
    temperature: float = 0.7
    
    # File Upload Configuration
    max_file_size: str = "50MB"
    allowed_extensions: List[str] = ["pdf", "txt", "docx", "md", "html", "csv", "json"]
    upload_folder: str = "./static/uploads"
    
    # Security
    cors_origins: List[str] = ["http://localhost:5000", "http://127.0.0.1:5000"]
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "./logs/app.log"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Create necessary directories
        Path(self.vector_db_path).mkdir(parents=True, exist_ok=True)
        Path(self.upload_folder).mkdir(parents=True, exist_ok=True)
        Path(os.path.dirname(self.log_file)).mkdir(parents=True, exist_ok=True)

# Global settings instance
settings = Settings()

# Helper functions
def get_max_file_size_bytes() -> int:
    """Convert max file size string to bytes"""
    size_str = settings.max_file_size.upper()
    if size_str.endswith('MB'):
        return int(size_str[:-2]) * 1024 * 1024
    elif size_str.endswith('KB'):
        return int(size_str[:-2]) * 1024
    elif size_str.endswith('GB'):
        return int(size_str[:-2]) * 1024 * 1024 * 1024
    else:
        return int(size_str)

def is_allowed_file(filename: str) -> bool:
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in settings.allowed_extensions
