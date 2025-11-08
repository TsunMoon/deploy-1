# backend/services/response_templates.py
"""
Response template system for structured, engaging recommendations
"""

from enum import Enum
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)


class ResponseType(Enum):
    """Types of structured responses"""
    MOVIE_RECOMMENDATION = "movie_recommendation"
    TV_SHOW_RECOMMENDATION = "tv_show_recommendation"
    SIMILAR_CONTENT = "similar_content"
    GENRE_FILTER = "genre_filter"
    DETAILED_INFO = "detailed_info"
    TRENDING = "trending"
    FOLLOW_UP_REFERENCE = "follow_up_reference"
    GENERAL_CHAT = "general_chat"


class ResponseTemplate:
    """Template system for consistent, engaging responses"""
    
    @staticmethod
    def detect_response_type(query: str, context: List[Dict]) -> ResponseType:
        """
        Detect the appropriate response type based on query and context
        
        Args:
            query: User's question
            context: Retrieved context from QdrantDB
            
        Returns:
            ResponseType enum
        """
        query_lower = query.lower()
        
        # Check for follow-up reference questions (HIGHEST PRIORITY)
        follow_up_patterns = [
            "how many", "bao nhiêu", "đã đề cập", "đã nói", "ở trên", "above",
            "those", "these", "them", "it", "that one", "which one",
            "the movies", "the films", "the shows", "phim nào", "cái nào"
        ]
        if any(pattern in query_lower for pattern in follow_up_patterns):
            return ResponseType.FOLLOW_UP_REFERENCE
        
        # Check for specific patterns
        if "similar" in query_lower or "like" in query_lower:
            return ResponseType.SIMILAR_CONTENT
        
        if "trending" in query_lower or "popular" in query_lower or "hot" in query_lower:
            return ResponseType.TRENDING
        
        if any(pattern in query_lower for pattern in [
            "details", "tell me about", "tell me more about movie/tv-show", "what is", 
            "information about", "info about", "more about"
        ]):
            return ResponseType.DETAILED_INFO
        
        if "genre" in query_lower or "filter" in query_lower or "type of" in query_lower:
            return ResponseType.GENRE_FILTER
        
        # Check context for movie vs TV show
        if context:
            types = [c.get("type", "").lower() for c in context]
            if any("tv" in t or "series" in t for t in types):
                return ResponseType.TV_SHOW_RECOMMENDATION
            elif any("movie" in t for t in types):
                return ResponseType.MOVIE_RECOMMENDATION
        
        # Check query for movie vs TV show keywords
        if any(word in query_lower for word in ["series", "show", "tv", "episode", "season"]):
            return ResponseType.TV_SHOW_RECOMMENDATION
        elif any(word in query_lower for word in ["movie", "film"]):
            return ResponseType.MOVIE_RECOMMENDATION
        
        # Default to general chat
        return ResponseType.GENERAL_CHAT
    
    @staticmethod
    def format_context_for_prompt(context: List[Dict]) -> str:
        """
        Format context items for inclusion in prompt
        
        Args:
            context: List of context items from QdrantDB
            
        Returns:
            Formatted context string
        """
        if not context:
            return "No specific context available."
        
        formatted = "**Available Content:**\n\n"
        for i, item in enumerate(context, 1):
            formatted += f"{i}. **{item.get('title', 'Unknown')}** ({item.get('year', 'N/A')})\n"
            formatted += f"   Type: {item.get('type', 'Unknown')}\n"
            formatted += f"   Genre: {item.get('genre', 'Unknown')}\n"
            formatted += f"   Rating: {item.get('rating', 'N/A')}\n"
            formatted += f"   Description: {item.get('description', '')}\n\n"
        
        return formatted
    
    @staticmethod
    def get_system_prompt(response_type: ResponseType, user_profile: Optional[Dict] = None) -> str:
        """
        Get system prompt for specific response type
        
        Args:
            response_type: Type of response to generate
            user_profile: Optional user profile with preferences
            
        Returns:
            System prompt string
        """
        base_prompt = """You are an expert entertainment recommendation assistant with deep knowledge of movies, TV shows, and series. You provide helpful, engaging, and personalized recommendations.

IMPORTANT: When users ask follow-up questions about previous recommendations (e.g., "How many movies did you mention?", "Which ones did you suggest?", "Tell me more about the films above"), you MUST refer to the Previous Conversation section in the prompt to provide accurate answers. Count and reference the specific titles you mentioned earlier."""
        
        # Add user profile context if available
        if user_profile:
            logger.info(f"Using user profile with favorite genres: {user_profile.get('favorite_genres', [])}")
            preferences = user_profile.get("preferences", "")
            favorite_genres = user_profile.get("favorite_genres", [])
            disliked_genres = user_profile.get("disliked_genres", [])
            favorite_actors = user_profile.get("favorite_actors", [])
            watch_style = user_profile.get("watch_style", "")
            mood_preference = user_profile.get("mood_preference", "")
            recently_watched = user_profile.get("recently_watched", [])
            watching_with = user_profile.get("watching_with", "")
            time_available = user_profile.get("time_available", "")
            
            profile_context = "\n\n**USER PROFILE - CRITICAL: Use this information to personalize ALL responses:**\n"
            if preferences:
                profile_context += f"- Preferences: {preferences}\n"
            if favorite_genres:
                genres_str = ", ".join(favorite_genres)
                profile_context += f"- **FAVORITE GENRES: {genres_str}** (MUST prioritize these genres in recommendations)\n"
            if disliked_genres:
                disliked_str = ", ".join(disliked_genres)
                profile_context += f"- **DISLIKES: {disliked_str}** (NEVER recommend these genres)\n"
            if favorite_actors:
                actors_str = ", ".join(favorite_actors)
                profile_context += f"- Favorite actors: {actors_str} (highlight when available)\n"
            if watch_style:
                profile_context += f"- Watch style: {watch_style}\n"
            if mood_preference:
                profile_context += f"- Current mood: {mood_preference}\n"
            if recently_watched:
                watched_str = ", ".join(recently_watched[:5])
                profile_context += f"- Recently watched: {watched_str} (avoid duplicates, suggest similar)\n"
            if watching_with:
                profile_context += f"- Watching with: {watching_with}\n"
            if time_available:
                profile_context += f"- Time available: {time_available}\n"
            
            profile_context += "\n**HOW TO USE THIS PROFILE:**\n"
            profile_context += "1. **PRIORITIZE FAVORITE GENRES** - Always recommend from their favorite genres first\n"
            profile_context += "2. **FILTER OUT DISLIKED GENRES** - Never recommend content they explicitly dislike\n"
            profile_context += "3. **HIGHLIGHT FAVORITE ACTORS** - Mention when their favorite actors appear\n"
            profile_context += "4. **MATCH THEIR MOOD** - Consider their current mood preference for tone/pacing\n"
            profile_context += "5. **RESPECT TIME AVAILABLE** - Suggest appropriate length content\n"
            profile_context += "6. **LANGUAGE/COUNTRY PREFERENCE** - Prioritize content from their preferred regions\n"
            profile_context += "7. **REFERENCE WATCH STYLE** - Match their viewing preferences and style\n"
            profile_context += "8. **AVOID RECENT WATCHES** - Don't repeat what they just watched\n"
            profile_context += "9. **EXPLAIN MATCHES** - Tell them WHY each recommendation fits their profile\n"
            profile_context += "10. **BE PERSONAL** - Show you understand their unique taste by referencing their specific preferences\n"
            
            base_prompt += profile_context
        
        type_specific = {
            ResponseType.MOVIE_RECOMMENDATION: """
Focus on recommending movies. Structure your response with the following format for EACH recommendation:

**Title**: [Movie Title]
**Year**: [Release Year]
**Country**: [Country of Origin]
**Genre**: [Genre(s)]
**Rating**: [Rating if available]
**Summary**: [Brief 2-3 sentence plot tease without spoilers]
**Why You'll Love It**: [Personal touch explaining why this matches user's preferences]

---

CRITICAL RULES - FOLLOW THESE EXACTLY:
1. **NUMBER OF RECOMMENDATIONS**: 
   - If the user specifies a number (e.g., "3 movies", "10 films", "recommend 7"), provide EXACTLY that number.
   - If the user does NOT specify a number (e.g., "recommend films", "suggest movies", "what should I watch"), you MUST provide EXACTLY 5 recommendations. This is the default and is MANDATORY.

2. **FORMATTING**: 
   - Add a horizontal line separator (---) between EACH recommendation to visually separate them
   - Each recommendation must follow the exact format above with all fields

3. **DIFFERENT FILMS**: 
   - If the user asks for "other films", "more films", "different films", "another film", or similar requests, you MUST recommend DIFFERENT films that were NOT mentioned in the Previous Conversation section. Do NOT repeat any titles that were already recommended.

4. **PROFILE-BASED RECOMMENDATIONS**: 
   - If the user's query is vague or general (e.g., "recommend movies", "suggest films", "what should I watch"), you MUST base your recommendations PRIMARILY on the USER PROFILE section. Prioritize their favorite genres, favorite actors, mood preference, and watch style. The recommendations should feel personalized and tailored to their specific tastes.

5. **TONE**: 
   - Start with a warm greeting and end with an engaging follow-up question. Keep it conversational and enthusiastic!

REMEMBER: When no number is specified, ALWAYS provide exactly 5 recommendations. This is not optional.""",
            
            ResponseType.TV_SHOW_RECOMMENDATION: """
Focus on recommending TV shows and series. Structure your response with the following format for EACH recommendation:

**Title**: [Show Title]
**Year**: [Release Year / Year Range]
**Country**: [Country of Origin]
**Genre**: [Genre(s)]
**Seasons**: [Number of Seasons]
**Episodes**: [Approximate Episode Count]
**Rating**: [Rating if available]
**Summary**: [Brief 2-3 sentence overview]
**Why It's Binge-Worthy**: [Explain pacing, tone, and commitment level]

Provide 2-3 recommendations. Make it easy for them to decide if it's their next watch!""",
            
            ResponseType.SIMILAR_CONTENT: """
Find content similar to a reference. Structure your response for EACH similar title:

**Title**: [Title]
**Year**: [Release Year]
**Country**: [Country of Origin]
**Genre**: [Genre(s)]
**Rating**: [Rating if available]
**Summary**: [Brief plot overview]
**Similarity**: [What makes it similar - themes, style, tone]
**Unique Aspects**: [What makes this one special/different]

Explain clearly why fans of the reference content would enjoy these recommendations!""",
            
            ResponseType.GENRE_FILTER: """
Filter and curate by genre or criteria. Structure your response for EACH title:

**Title**: [Title]
**Year**: [Release Year]
**Country**: [Country of Origin]
**Type**: [Movie/TV Show]
**Genre**: [Primary Genre(s)]
**Rating**: [Rating if available]
**Summary**: [Brief 1-2 sentence description]
**Standout Quality**: [Why this title stands out in the genre]

Provide variety within the genre and share insights about genre trends. Make browsing enjoyable!""",
            
            ResponseType.DETAILED_INFO: """
Provide comprehensive information about a specific title using this detailed structure:

**Title**: [Full Title]
**Year**: [Release Year]
**Country**: [Country of Origin]
**Type**: [Movie/TV Show/Series]
**Genre**: [Genre(s)]
**Rating**: [Rating if available]
**Director/Creator**: [Key creative talent]
**Cast**: [Main actors/actresses]
**Main Plot**: [Detailed 4-5 sentence plot summary without major spoilers]
**Themes**: [Key themes and messages]
**Critical Reception**: [Awards, acclaim, notable reviews]
**Why It's Worth Watching**: [What makes it special and memorable]
**Similar Titles**: [2-3 related recommendations]

Be thorough, informative, and engaging!""",
            
            ResponseType.TRENDING: """
Share what's currently popular and buzzing. Structure your response for EACH trending title:

**Title**: [Title]
**Year**: [Release Year]
**Country**: [Country of Origin]
**Genre**: [Genre(s)]
**Rating**: [Rating if available]
**Summary**: [Brief plot overview]
**Why It's Trending**: [Current buzz, cultural relevance, social media presence]
**Quality Assessment**: [Critical and audience reception]
**Buzz Indicators**: [Awards, viewership numbers, viral moments]

Capture the excitement and help users understand the hype!""",
            
            ResponseType.FOLLOW_UP_REFERENCE: """
CRITICAL: The user is asking about previous recommendations.
You MUST:
1. Carefully read the "Previous Conversation" section
2. Count the exact number of titles you mentioned
3. List the specific titles you recommended with key details:
   - Title
   - Year
   - Country
   - Brief note about why you recommended it

DO NOT make up new recommendations or approximate.
Reference the conversation history accurately.
If asked "how many", count the titles and provide the exact number.
If asked "which ones", list all the titles you mentioned with the structure above.""",
            
            ResponseType.GENERAL_CHAT: """
Engage naturally in conversation about entertainment. When providing any content information, use this structure:

**Title**: [Title]
**Year**: [Year if relevant]
**Country**: [Country if relevant]
**Summary**: [Brief relevant information]

Be warm, friendly, and show enthusiasm for movies and shows. Provide helpful guidance and ask engaging follow-ups. Keep the conversation flowing naturally!"""
        }
        
        return base_prompt + type_specific.get(response_type, type_specific[ResponseType.GENERAL_CHAT])
    
    @staticmethod
    def create_structured_prompt(
        query: str,
        context: List[Dict],
        chat_history: Optional[List[tuple]] = None,
        response_type: Optional[ResponseType] = None,
        user_profile: Optional[Dict] = None,
        user_name: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Create structured prompt with system and user messages
        
        Args:
            query: User's question
            context: Retrieved context
            chat_history: Previous conversation
            response_type: Optional forced response type
            user_profile: Optional user profile for personalization
            
        Returns:
            Dict with 'system' and 'user' prompt strings
        """
        # Auto-detect response type if not provided
        if response_type is None:
            response_type = ResponseTemplate.detect_response_type(query, context)
        
        # Get system prompt with user profile
        system_prompt = ResponseTemplate.get_system_prompt(response_type, user_profile)
        
        # Build user prompt with context
        user_prompt = ResponseTemplate.format_context_for_prompt(context)
        
        # Add user name for personalized responses
        if user_name:
            user_prompt += f"\n**USER NAME:** {user_name} (greet them naturally when appropriate)\n"
        
        # Add chat history if available - IMPROVED VERSION
        if chat_history:
            history_str = "\n**Previous Conversation:**\n"
            history_str += "(Use this context to answer follow-up questions about previous recommendations)\n\n"
            
            for q, a in chat_history[-5:]:  # Last 5 exchanges for better context
                history_str += f"User: {q}\n"
                
                # Keep full answer if short, or intelligently truncate if long
                if len(a) <= 500:
                    history_str += f"Assistant: {a}\n\n"
                else:
                    # Keep first 400 chars and last 100 chars to preserve key info
                    history_str += f"Assistant: {a[:400]}...[continued]...{a[-100:]}\n\n"
            
            user_prompt += history_str
        
        # Add current query
        user_prompt += f"\n**Current Question:**\n{query}\n\n"
        user_prompt += f"**Response Type:** {response_type.value}\n"
        
        # Add explicit instruction about number of recommendations
        if response_type == ResponseType.MOVIE_RECOMMENDATION or response_type == ResponseType.TV_SHOW_RECOMMENDATION:
            import re
            # Check if user specified a number
            number_match = re.search(r'\b(\d+)\s*(?:movies?|films?|shows?|recommendations?)\b', query.lower())
            if not number_match:
                # No number specified - MUST provide 5
                user_prompt += "\n**CRITICAL**: The user did NOT specify a number. You MUST provide EXACTLY 5 recommendations. This is mandatory and not optional.\n"
            else:
                requested_number = int(number_match.group(1))
                user_prompt += f"\n**CRITICAL**: The user requested {requested_number} recommendations. You MUST provide EXACTLY {requested_number} recommendations.\n"
        
        user_prompt += "Please provide a helpful, engaging response following the guidelines above."
        user_prompt += " If the user is asking about previous recommendations (e.g., 'how many', 'which ones', 'the movies above'), refer to the Previous Conversation section to answer accurately."
        
        return {
            "system": system_prompt,
            "user": user_prompt
        }


class TemplateSystem:
    """Main template system controller"""
    
    def __init__(self):
        self.template = ResponseTemplate()
        logger.info("Template system initialized")
    
    def detect_response_type(self, query: str, context: List[Dict]) -> ResponseType:
        """Detect appropriate response type"""
        return self.template.detect_response_type(query, context)
    
    def format_context_for_prompt(self, context: List[Dict]) -> str:
        """Format context for prompt"""
        return self.template.format_context_for_prompt(context)
    
    def create_structured_prompt(
        self,
        query: str,
        context: List[Dict],
        chat_history: Optional[List[tuple]] = None,
        response_type: Optional[ResponseType] = None,
        user_profile: Optional[Dict] = None,
        user_name: Optional[str] = None
    ) -> Dict[str, str]:
        """Create structured prompt"""
        return self.template.create_structured_prompt(
            query, context, chat_history, response_type, user_profile, user_name
        )


# Singleton instance
_template_system = None


def get_template_system() -> TemplateSystem:
    """Get or create template system instance"""
    global _template_system
    if _template_system is None:
        _template_system = TemplateSystem()
    return _template_system