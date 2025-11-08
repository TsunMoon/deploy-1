# backend/routers/langchain_recommendation.py
"""
Enhanced recommendation router with response template system
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, field_validator
from typing import Any, List, Optional, Tuple, Union
from services.langchain_service import get_langchain_service
from services.memory_service import get_memory_service
from services.query_parser_service import get_query_parser_service
from services.response_templates import ResponseType
from routers.auth import get_user_profile
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v2", tags=["langchain-recommendations"])


# Request/Response Models
class ConversationMessage(BaseModel):
    """Single conversation message"""
    question: str
    answer: str


class LangChainRequest(BaseModel):
    """Request for LangChain recommendation"""
    query: str = Field(..., min_length=1, description="User's question")
    chat_history: List[ConversationMessage] = Field(
        default_factory=list,
        description="Previous conversation history"
    )
    session_id: Optional[str] = Field(
        default=None,
        description="Session ID for conversation memory"
    )
    user_id: Optional[str] = Field(
        default=None,
        description="User ID to load user profile for personalized recommendations"
    )
    use_functions: bool = Field(
        default=False,
        description="Enable Azure OpenAI function calling"
    )
    use_template: bool = Field(
        default=True,
        description="Use structured response templates for better formatting"
    )
    use_llm_parsing: bool = Field(
        default=True,
        description="Use LLM to optimize query for better search results"
    )
    response_type: Optional[str] = Field(
        default=None,
        description="Force specific response type (movie_recommendation, tv_show_recommendation, etc.)"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "Recommend a thriller movie similar to Inception",
                "chat_history": [],
                "session_id": "session_1762078185591_sypmmdf4ht",
                "use_functions": False,
                "use_template": True,
                "use_llm_parsing": True,
                "response_type": None
            }
        }


class Source(BaseModel):
    """Source document metadata"""
    title: str = Field(..., description="Title of the content")
    description: str = Field(..., description="Description/synopsis")
    genre: str = Field(..., description="Genre categories")
    year: Union[str, int] = Field(..., description="Release year", examples=["2021", 2021])
    type: Optional[str] = Field(None, description="Content type (movie/show)")
    rating: Optional[str] = Field(None, description="Content rating")

    @field_validator('year', mode='before')
    @classmethod
    def convert_year_to_str(cls, v):
        return str(v)


class UserProfile(BaseModel):
    """User profile information"""
    preferences: Optional[str] = Field(None, description="User preferences")
    favorite_genres: Optional[List[str]] = Field(None, description="Favorite genres")
    disliked_genres: Optional[List[str]] = Field(None, description="Disliked genres")
    favorite_actors: Optional[List[str]] = Field(None, description="Favorite actors")
    watch_style: Optional[str] = Field(None, description="Watch style")
    mood_preference: Optional[str] = Field(None, description="Mood preference")
    recently_watched: Optional[List[str]] = Field(None, description="Recently watched")
    watching_with: Optional[str] = Field(None, description="Watching with")
    time_available: Optional[str] = Field(None, description="Time available")
    language_preference: Optional[str] = Field(None, description="Language preference")


class LangChainResponse(BaseModel):
    """Response from LangChain recommendation"""
    answer: str = Field(..., description="AI-generated recommendation")
    audio_url: Optional[str] = Field(None, description="URL to audio response")
    sources: List[Source] = Field(
        default_factory=list,
        description="Source documents used"
    )
    chat_history: List[ConversationMessage] = Field(
        default_factory=list,
        description="Updated conversation history"
    )
    function_called: Optional[str] = Field(
        None,
        description="Name of function called (if any)"
    )
    response_type: str = Field(
        default="default",
        description="Type of response template used"
    )
    user_profile: Optional[UserProfile] = Field(
        None,
        description="User profile used for personalization"
    )
    user_name: Optional[str] = Field(
        None,
        description="User name for personalized responses"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "answer": "🎬 Hey Cong Danh! Since you love action-packed movies...",
                "audio_url": None,
                "sources": [
                    {
                        "title": "Inception",
                        "description": "A thief who steals corporate secrets...",
                        "genre": "Sci-Fi, Thriller",
                        "year": "2010",
                        "type": "Movie",
                        "rating": "PG-13"
                    }
                ],
                "chat_history": [],
                "function_called": None,
                "response_type": "movie_recommendation",
                "user_profile": {
                    "preferences": "Love action-packed movies...",
                    "favorite_genres": ["action", "anime", "thriller"],
                    "favorite_actors": ["Tom Cruise", "Keanu Reeves"]
                },
                "user_name": "Cong Danh"
            }
        }


@router.post("/recommendation", response_model=LangChainResponse)
async def get_langchain_recommendation(request: LangChainRequest):
    """
    Get entertainment recommendation using LangChain with structured templates
    
    Features:
    - Structured response templates for consistent formatting
    - QdrantDB semantic search for relevant context
    - Conversational memory for context-aware responses
    - Azure OpenAI function calling for extended capabilities
    
    Response Types:
    - movie_recommendation: Structured movie suggestions
    - tv_show_recommendation: Series recommendations with episode info
    - similar_content: Find titles similar to a reference
    - genre_filter: Filtered lists by genre/criteria
    - detailed_info: Complete information about a title
    - trending: What's popular now
    - general_chat: Natural conversation
    """
    # Initialize all variables at function scope
    answer = None
    updated_history = []
    sources = []
    function_called = None
    response_type = "default"
    result = {}
    audio_url = None
    history_tuples = []

    try:
        logger.info(f"Received LangChain request: {request.query[:50]}...")
        
        # Check if query is movie-related
        query_parser = get_query_parser_service()
        if not query_parser.is_movie_related(request.query):
            logger.warning(f"Non-movie related query detected: {request.query[:50]}...")
            
            # Return error response for out-of-scope questions
            out_of_scope_messages = [
                "Xin lỗi, tôi chỉ có thể hỗ trợ về phim ảnh và chương trình TV trên Netflix. 🎬",
                "Bạn có thể hỏi tôi về:",
                "• Gợi ý phim hoặc series",
                "• Thông tin về diễn viên, đạo diễn",
                "• Tìm phim theo thể loại, năm phát hành",
                "• So sánh các bộ phim",
                "",
                "Sorry, I can only help with movies and TV shows on Netflix. 🎬",
                "You can ask me about:",
                "• Movie or series recommendations",
                "• Actor, director information",
                "• Finding content by genre, year",
                "• Comparing films"
            ]
            
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "out_of_scope",
                    "message": "\n".join(out_of_scope_messages),
                    "query": request.query,
                    "suggestion": "Please ask about movies, TV shows, or entertainment content."
                }
            )
        
        # Get services
        langchain_service = get_langchain_service()
        memory_service = get_memory_service()
        
        # Get user profile if user_id provided
        user_profile = None
        user_name = None
        if request.user_id:
            user_profile = get_user_profile(request.user_id)
            if user_profile:
                logger.info(f"Loaded user profile for user {request.user_id}: {user_profile.get('preferences', 'N/A')}")
                # Get user name for personalized greeting
                from routers.auth import get_user_by_id
                user_data = get_user_by_id(request.user_id)
                user_name = user_data.get("name") if user_data else None
        
        # Get conversation history from memory if session_id provided
        if request.session_id:
            # Load history from memory
            history_tuples = memory_service.get_history(request.session_id)
            logger.info(f"Loaded {len(history_tuples)} messages from session {request.session_id}")
        
        # Merge with provided chat_history if any
        if request.chat_history:
            history_from_request = [
                (msg.question, msg.answer)
                for msg in request.chat_history
            ]
            # Combine, avoiding duplicates
            history_tuples = history_tuples + history_from_request
        
        # Get recommendation
        if request.use_functions:
            # Use function calling
            answer, updated_history = langchain_service.chat_with_functions(
                request.query,
                history_tuples,
                user_profile=user_profile,
                user_name=user_name
            )
            sources = []
            function_called = "function_call_detected"
            response_type = "function_call"
        else:
            # Use standard retrieval with templates
            result = langchain_service.get_recommendation(
                query=request.query,
                chat_history=history_tuples,
                use_template=request.use_template,
                use_llm_parsing=request.use_llm_parsing,
                user_profile=user_profile,
                user_name=user_name
            )
            answer = result["answer"]
            sources = result["sources"]
            updated_history = result["chat_history"]
            function_called = None
            response_type = result.get("response_type", "default")
        
        # Save conversation to memory if session_id provided
        if request.session_id:
            memory_service.add_message(request.session_id, request.query, answer)
            logger.info(f"Saved conversation to session {request.session_id}")
        
        # Convert history back to messages
        chat_messages = [
            ConversationMessage(question=q, answer=a)
            for q, a in updated_history
        ]        # Ensure we have a valid answer
        if not answer:
            raise ValueError("No answer was generated")

        # Build response
        # Convert year to string in sources
        for s in sources:
            if 'year' in s:
                s['year'] = str(s['year'])

        # Convert user_profile to UserProfile model if available
        user_profile_model = None
        if user_profile:
            user_profile_model = UserProfile(**user_profile)

        response = LangChainResponse(
            answer=answer,
            audio_url=audio_url,
            sources=[Source(**s) for s in sources],
            chat_history=chat_messages,
            function_called=function_called,
            response_type=response_type,
            user_profile=user_profile_model,
            user_name=user_name
        )
        
        logger.info(f"Successfully generated {response_type} recommendation")
        return response
        
    except Exception as e:
        logger.error(f"Failed to process LangChain request: {e}")
        # Return a proper error response
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate recommendation: {str(e)}"
        )


@router.get("/session-history/{session_id}")
async def get_session_history(session_id: str):
    """
    Get conversation history for a specific session
    """
    try:
        memory_service = get_memory_service()
        history = memory_service.get_history(session_id)
        
        # Convert to messages format
        messages = [
            {"question": q, "answer": a}
            for q, a in history
        ]
        
        return {
            "session_id": session_id,
            "message_count": len(messages),
            "messages": messages
        }
    except Exception as e:
        logger.error(f"Failed to get session history: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get session history: {str(e)}"
        )


@router.post("/clear-memory")
async def clear_conversation_memory(session_id: Optional[str] = None):
    """
    Clear the conversation memory
    
    If session_id is provided, clears only that session.
    Otherwise, clears the LangChain memory (legacy behavior).
    """
    try:
        if session_id:
            # Clear specific session
            memory_service = get_memory_service()
            memory_service.clear_session(session_id)
            return {"message": f"Session {session_id} cleared successfully"}
        else:
            # Clear LangChain memory (legacy)
            langchain_service = get_langchain_service()
            langchain_service.clear_memory()
            return {"message": "Conversation memory cleared successfully"}
    except Exception as e:
        logger.error(f"Failed to clear memory: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to clear memory: {str(e)}"
        )


# Function-specific endpoints for direct function calls
@router.get("/film/{title}")
async def get_film_details(title: str):
    """
    Get detailed information about a specific film
    
    Returns structured information including:
    - Title, year, type, genre
    - Rating and duration
    - Full description
    - Why to watch it
    - Similar recommendations
    """
    try:
        langchain_service = get_langchain_service()
        result = langchain_service._get_film_details(title)
        return {
            "result": result,
            "title": title,
            "response_type": "detailed_info"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/filter-by-genre")
async def filter_by_genre(
    genres: List[str],
    min_year: Optional[int] = None
):
    """
    Filter films by genre and optional minimum year
    
    Returns curated list with:
    - Titles matching genre criteria
    - Year filter applied if specified
    - Descriptions and ratings
    - Genre insights
    """
    try:
        langchain_service = get_langchain_service()
        result = langchain_service._filter_by_genre(genres, min_year)
        return {
            "result": result,
            "genres": genres,
            "min_year": min_year,
            "response_type": "genre_filter"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/similar/{title}")
async def get_similar_titles(
    title: str,
    num_results: int = 5
):
    """
    Get titles similar to a given film
    
    Returns:
    - Similar titles based on genre, theme, style
    - Comparison to reference title
    - What makes each unique
    - Quality indicators
    """
    try:
        langchain_service = get_langchain_service()
        result = langchain_service._get_similar_titles(title, num_results)
        return {
            "result": result,
            "reference_title": title,
            "num_results": num_results,
            "response_type": "similar_content"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trending/{category}")
async def get_trending(category: str):
    """
    Get trending recommendations
    
    Categories:
    - movies: Trending films
    - tv_shows: Trending series
    - all: Both movies and shows
    
    Returns:
    - Currently popular titles
    - Why they're trending
    - Ratings and buzz indicators
    - Trend insights
    """
    try:
        if category not in ["movies", "tv_shows", "all"]:
            raise HTTPException(
                status_code=400,
                detail="Category must be 'movies', 'tv_shows', or 'all'"
            )
        
        langchain_service = get_langchain_service()
        result = langchain_service._get_trending_recommendations(category)
        return {
            "result": result,
            "category": category,
            "response_type": "trending"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/response-types")
async def get_available_response_types():
    """
    Get list of available response types and their descriptions
    
    Use this to understand what template formats are available
    """
    return {
        "response_types": [
            {
                "type": "movie_recommendation",
                "description": "Structured movie suggestions with personalized reasons",
                "features": ["Personalized greeting", "2-3 recommendations", "Plot teases", "Follow-up questions"]
            },
            {
                "type": "tv_show_recommendation",
                "description": "Series recommendations with episode/season info",
                "features": ["Season counts", "Binge-worthiness notes", "Viewing commitment info"]
            },
            {
                "type": "similar_content",
                "description": "Find titles similar to a reference",
                "features": ["Similarity explanations", "Unique aspects", "Quality indicators"]
            },
            {
                "type": "genre_filter",
                "description": "Filtered lists by genre and criteria",
                "features": ["Curated lists", "Genre insights", "Year filtering", "Variety within genre"]
            },
            {
                "type": "detailed_info",
                "description": "Complete information about a specific title",
                "features": ["Full metadata", "Cast/crew", "Critical reception", "Why to watch"]
            },
            {
                "type": "trending",
                "description": "Currently popular and buzzing content",
                "features": ["Trend explanations", "Social proof", "Current relevance"]
            },
            {
                "type": "general_chat",
                "description": "Natural conversational responses",
                "features": ["Warm tone", "Helpful guidance", "Entertainment enthusiasm"]
            }
        ],
        "usage": "Set 'response_type' in request to force a specific template, or leave null for auto-detection"
    }


@router.get("/health")
async def langchain_health_check():
    """Health check for LangChain service with template system status"""
    try:
        langchain_service = get_langchain_service()
        return {
            "status": "healthy",
            "service": "LangChain Recommendation Service",
            "vectorstore": "QdrantDB",
            "llm": "Azure OpenAI",
            "functions_available": len(langchain_service.functions),
            "template_system": "enabled",
            "response_types": 7
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=503,
            detail=f"Service unavailable: {str(e)}"
        )