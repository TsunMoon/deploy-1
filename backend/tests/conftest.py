"""
Pytest configuration and fixtures for backend tests
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, MagicMock
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import app
from services.langchain_service import LangChainRecommendationService
from services.qdrant_service import QdrantService
from services.memory_service import ConversationMemory


@pytest.fixture
def client():
    """FastAPI test client"""
    return TestClient(app)


@pytest.fixture
def mock_qdrant_service():
    """Mock QdrantService for testing"""
    mock_service = Mock(spec=QdrantService)
    
    # Mock search results
    mock_service.search.return_value = [
        {
            "title": "Inception",
            "description": "A thief who steals corporate secrets through the use of dream-sharing technology",
            "genre": "Sci-Fi, Thriller",
            "year": "2010",
            "type": "Movie",
            "rating": "PG-13",
            "score": 0.95
        },
        {
            "title": "The Matrix",
            "description": "A computer hacker learns about the true nature of his reality",
            "genre": "Sci-Fi, Action",
            "year": "1999",
            "type": "Movie",
            "rating": "R",
            "score": 0.92
        }
    ]
    
    # Mock collection stats
    mock_service.get_collection_stats.return_value = {
        "total_points": 100,
        "vectors_count": 100,
        "indexed_vectors_count": 100
    }
    
    return mock_service


@pytest.fixture
def mock_langchain_service():
    """Mock LangChainService for testing"""
    mock_service = Mock(spec=LangChainRecommendationService)
    
    # Mock recommendation response
    mock_service.get_recommendation.return_value = {
        "answer": "🎬 Based on your interest in thrillers, I recommend Inception...",
        "sources": [
            {
                "title": "Inception",
                "description": "A thief who steals corporate secrets",
                "genre": "Sci-Fi, Thriller",
                "year": "2010",
                "type": "Movie",
                "rating": "PG-13"
            }
        ],
        "chat_history": [("recommend a thriller", "I recommend Inception...")],
        "response_type": "movie_recommendation",
        "include_audio": True
    }
    
    # Mock function calling
    mock_service.chat_with_functions.return_value = (
        "Here are the details about Inception...",
        [("tell me about inception", "Here are the details...")]
    )
    
    # Mock specific functions
    mock_service._get_film_details.return_value = "Inception is a 2010 science fiction thriller..."
    mock_service._filter_by_genre.return_value = "Here are thriller movies..."
    mock_service._get_similar_titles.return_value = "Movies similar to Inception..."
    mock_service._get_trending_recommendations.return_value = "Trending movies right now..."
    
    mock_service.functions = []
    
    return mock_service


@pytest.fixture
def mock_tts_service():
    """Mock TTSService for testing"""
    mock_service = Mock()
    mock_service.generate_and_save_audio.return_value = "/audio/test_audio.wav"
    return mock_service


@pytest.fixture
def mock_memory_service():
    """Mock MemoryService for testing"""
    mock_service = Mock(spec=ConversationMemory)
    
    # Mock history storage
    mock_service.get_history.return_value = [
        ("What are some good thrillers?", "I recommend Inception and The Dark Knight..."),
        ("Tell me more about Inception", "Inception is a 2010 film directed by Christopher Nolan...")
    ]
    
    mock_service.add_message.return_value = None
    mock_service.clear_session.return_value = None
    
    return mock_service


@pytest.fixture
def sample_chat_history():
    """Sample chat history for testing"""
    return [
        {"question": "What are good thriller movies?", "answer": "I recommend Inception..."},
        {"question": "Tell me more", "answer": "Inception is a mind-bending thriller..."}
    ]


@pytest.fixture
def sample_langchain_request():
    """Sample LangChain request payload"""
    return {
        "query": "Recommend a thriller movie",
        "chat_history": [],
        "session_id": "test_session_123",
        "use_functions": False,
        "use_template": True,
        "use_llm_parsing": True,
        "response_type": None
    }


@pytest.fixture
def sample_login_credentials():
    """Sample login credentials for testing"""
    return {
        "valid": {
            "email": "congdanh.official@gmail.com",
            "password": "congdanh@123"
        },
        "invalid": {
            "email": "wrong@example.com",
            "password": "wrongpassword"
        }
    }


# Cleanup after tests
@pytest.fixture(autouse=True)
def cleanup():
    """Cleanup after each test"""
    yield
    # Any cleanup code here
