import os
from pathlib import Path
from typing import List, Optional

class Settings:
    def __init__(self):
        # Load from environment variables
        self.anthropic_api_key = os.getenv('ANTHROPIC_API_KEY', '')
        
        # Flask Configuration
        self.flask_env = os.getenv('FLASK_ENV', 'development')
        self.flask_debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
        self.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
        
        # Database Configuration
        self.database_url = os.getenv('DATABASE_URL', 'sqlite:///ai_rag_bot.db')
        
        # RAG Configuration
        self.vector_db_path = os.getenv('VECTOR_DB_PATH', './data/vector_db')
        self.max_chunk_size = int(os.getenv('MAX_CHUNK_SIZE', '1000'))
        self.chunk_overlap = int(os.getenv('CHUNK_OVERLAP', '200'))
        self.max_documents = int(os.getenv('MAX_DOCUMENTS', '1000'))
        self.embedding_model = os.getenv('EMBEDDING_MODEL', 'all-MiniLM-L6-v2')
        
        # Chat Configuration
        self.max_conversation_history = int(os.getenv('MAX_CONVERSATION_HISTORY', '50'))
        self.default_model = os.getenv('DEFAULT_MODEL', 'claude-3-sonnet-20240229')
        self.max_tokens = int(os.getenv('MAX_TOKENS', '4000'))
        self.temperature = float(os.getenv('TEMPERATURE', '0.7'))
        
        # File Upload Configuration
        self.max_file_size = os.getenv('MAX_FILE_SIZE', '50MB')
        self.allowed_extensions = os.getenv('ALLOWED_EXTENSIONS', 'pdf,txt,docx,md,html,csv,json').split(',')
        self.upload_folder = os.getenv('UPLOAD_FOLDER', './static/uploads')
        
        # Security
        cors_origins_str = os.getenv('CORS_ORIGINS', 'http://localhost:5000,http://127.0.0.1:5000')
        self.cors_origins = cors_origins_str.split(',')
        
        # Logging
        self.log_level = os.getenv('LOG_LEVEL', 'INFO')
        self.log_file = os.getenv('LOG_FILE', './logs/app.log')
        
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
