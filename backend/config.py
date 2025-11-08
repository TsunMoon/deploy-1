import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file
load_dotenv()

class Config:
    """Application configuration"""
    
    # Shared Azure Configuration
    AZURE_OPENAI_API_VERSION = "2024-07-01-preview"
    
    # Azure OpenAI Configuration - Chat Model
    AZURE_OPENAI_ENDPOINT=os.getenv("AZURE_OPENAI_ENDPOINT")
    AZURE_OPENAI_API_KEY=os.getenv("AZURE_OPENAI_API_KEY")
    AZURE_DEPLOYMENT_NAME=os.getenv("AZURE_DEPLOYMENT_NAME")

    # Embedding Model Configuration
    AZURE_EMBEDDING_API_KEY=os.getenv("AZURE_EMBEDDING_API_KEY")
    AZURE_EMBEDDING_ENDPOINT=os.getenv("AZURE_EMBEDDING_ENDPOINT")
    AZURE_EMBEDDING_DEPLOYMENT=os.getenv("AZURE_EMBEDDING_DEPLOYMENT")
    
    # LLM for Query Parsing - Uses specialized LLM for detecting input
    AZURE_OPENAI_LLM_DETECT_INPUT_ENDPOINT = os.getenv(
        "AZURE_OPENAI_LLM_DETECT_INPUT_ENDPOINT", 
        os.getenv("AZURE_OPENAI_ENDPOINT")  # Fallback to main endpoint
    )
    AZURE_OPENAI_LLM_DETECT_INPUT_API_KEY = os.getenv(
        "AZURE_OPENAI_LLM_DETECT_INPUT_API_KEY",
        os.getenv("AZURE_OPENAI_API_KEY")  # Fallback to main API key
    )
    AZURE_OPENAI_LLM_DETECT_INPUT_DEPLOYMENT_NAME = os.getenv(
        "AZURE_OPENAI_LLM_DETECT_INPUT_DEPLOYMENT_NAME",
        "gpt-4o-mini"  # Default to gpt-4o-mini
    )

    # Qdrant Configuration
    QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
    QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")  # Optional for cloud deployment
    QDRANT_COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME", "netflix_movies_tv_shows")
    QDRANT_VECTOR_SIZE = 1536  # Default for text-embedding-3-small
    
    # API Configuration
    CORS_ORIGINS = [
        "http://localhost:3000",
        "http://localhost:3001",
        "https://ai-batch3-chill-dev.vercel.app"
    ]
    
    # # Timeout Configuration (in seconds)
    # OPENAI_TIMEOUT = 60          # Azure OpenAI API timeout
    # REQUEST_TIMEOUT = 120        # Overall request timeout
    
    @classmethod
    def validate(cls):
        """Validate required environment variables"""
        required = [
            "AZURE_OPENAI_ENDPOINT",
            "AZURE_EMBEDDING_ENDPOINT",
            "AZURE_OPENAI_API_KEY",
            "AZURE_EMBEDDING_API_KEY",
        ]
        missing = [var for var in required if not getattr(cls, var)]
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

