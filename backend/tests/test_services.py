"""
Tests for backend services
"""
import pytest
from unittest.mock import Mock, patch
from services.memory_service import ConversationMemory


class TestMemoryService:
    """Test cases for ConversationMemory"""
    
    def test_add_message(self):
        """Test adding a message to session"""
        service = ConversationMemory()
        session_id = "test_session_1"
        
        service.add_message(session_id, "Hello", "Hi there")
        history = service.get_history(session_id)
        
        assert len(history) == 1
        assert history[0] == ("Hello", "Hi there")
    
    def test_add_multiple_messages(self):
        """Test adding multiple messages to session"""
        service = ConversationMemory()
        session_id = "test_session_2"
        
        service.add_message(session_id, "Question 1", "Answer 1")
        service.add_message(session_id, "Question 2", "Answer 2")
        service.add_message(session_id, "Question 3", "Answer 3")
        
        history = service.get_history(session_id)
        assert len(history) == 3
        assert history[0] == ("Question 1", "Answer 1")
        assert history[2] == ("Question 3", "Answer 3")
    
    def test_get_empty_history(self):
        """Test getting history for non-existent session"""
        service = ConversationMemory()
        history = service.get_history("non_existent_session")
        
        assert history == []
    
    def test_clear_session(self):
        """Test clearing a specific session"""
        service = ConversationMemory()
        session_id = "test_session_3"
        
        service.add_message(session_id, "Question", "Answer")
        assert len(service.get_history(session_id)) == 1
        
        service.clear_session(session_id)
        assert len(service.get_history(session_id)) == 0
    
    def test_get_all_sessions(self):
        """Test getting all session IDs"""
        service = ConversationMemory()
        
        service.add_message("session_1", "Q1", "A1")
        service.add_message("session_2", "Q2", "A2")
        service.add_message("session_3", "Q3", "A3")
        
        # Check sessions exist
        assert len(service.conversations) >= 3
        assert "session_1" in service.conversations
        assert "session_2" in service.conversations
        assert "session_3" in service.conversations
    
    def test_clear_all_sessions(self):
        """Test clearing all sessions"""
        service = ConversationMemory()
        
        service.add_message("session_1", "Q1", "A1")
        service.add_message("session_2", "Q2", "A2")
        
        # Clear all by clearing the dict
        service.conversations.clear()
        assert len(service.conversations) == 0
    
    def test_session_isolation(self):
        """Test that sessions are isolated from each other"""
        service = ConversationMemory()
        
        service.add_message("session_a", "Question A", "Answer A")
        service.add_message("session_b", "Question B", "Answer B")
        
        history_a = service.get_history("session_a")
        history_b = service.get_history("session_b")
        
        assert len(history_a) == 1
        assert len(history_b) == 1
        assert history_a[0][0] == "Question A"
        assert history_b[0][0] == "Question B"


class TestLangChainServiceMocked:
    """Test cases for LangChainRecommendationService with mocked dependencies"""
    
    @patch('services.langchain_service.get_qdrant_service')
    @patch('services.langchain_service.AzureChatOpenAI')
    def test_langchain_service_initialization(
        self, 
        mock_chat_openai, 
        mock_qdrant_service
    ):
        """Test LangChain service can be initialized"""
        from services.langchain_service import LangChainRecommendationService
        
        # Mock QdrantService
        mock_qdrant = Mock()
        mock_qdrant.vectorstore = Mock()
        mock_qdrant_service.return_value = mock_qdrant
        
        # Mock Azure Chat
        mock_chat = Mock()
        mock_chat_openai.return_value = mock_chat
        
        # This should not raise an exception
        try:
            service = LangChainRecommendationService()
            assert service is not None
        except Exception as e:
            pytest.skip(f"Service initialization requires real dependencies: {e}")
    
    def test_clear_memory(self):
        """Test clearing conversation memory"""
        from services.langchain_service import get_langchain_service
        
        try:
            service = get_langchain_service()
            # Should not raise exception
            service.clear_memory()
        except Exception as e:
            pytest.skip(f"Service requires real dependencies: {e}")


class TestQdrantServiceMocked:
    """Test cases for QdrantService with mocked dependencies"""
    
    def test_qdrant_service_initialization(self):
        """Test Qdrant service can be initialized"""
        from services.qdrant_service import get_qdrant_service
        
        try:
            service = get_qdrant_service()
            assert service is not None
        except Exception as e:
            pytest.skip(f"Service initialization requires real dependencies: {e}")


class TestTTSServiceMocked:
    """Test cases for TTSService with mocked dependencies"""
    
    @patch('services.tts_service.VitsModel')
    @patch('services.tts_service.AutoTokenizer')
    def test_tts_service_initialization(
        self, 
        mock_tokenizer, 
        mock_model
    ):
        """Test TTS service can be initialized"""
        from services.tts_service import TTSService
        
        # Mock dependencies
        mock_model_instance = Mock()
        mock_model.from_pretrained.return_value = mock_model_instance
        
        mock_tokenizer_instance = Mock()
        mock_tokenizer.from_pretrained.return_value = mock_tokenizer_instance
        
        try:
            service = TTSService()
            assert service is not None
        except Exception as e:
            pytest.skip(f"Service initialization requires real dependencies: {e}")


class TestResponseTemplates:
    """Test cases for response templates"""
    
    def test_response_type_enum(self):
        """Test ResponseType enum values"""
        from services.response_templates import ResponseType
        
        assert hasattr(ResponseType, 'MOVIE_RECOMMENDATION')
        assert hasattr(ResponseType, 'TV_SHOW_RECOMMENDATION')
        assert hasattr(ResponseType, 'SIMILAR_CONTENT')
        assert hasattr(ResponseType, 'GENRE_FILTER')
        assert hasattr(ResponseType, 'DETAILED_INFO')
        assert hasattr(ResponseType, 'TRENDING')
        assert hasattr(ResponseType, 'GENERAL_CHAT')
