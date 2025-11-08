"""
Enhanced recommendation service using LangChain with Response Templates
"""

# Updated imports for LangChain new structure
from typing import List, Dict, Optional, Tuple
import json
import logging
from langchain_community.vectorstores import Qdrant
from langchain_openai import AzureOpenAIEmbeddings, AzureChatOpenAI
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from config import Config
from .response_templates import ResponseTemplate, ResponseType, get_template_system
from .qdrant_service import get_qdrant_service
from qdrant_client import QdrantClient

logger = logging.getLogger(__name__)


class LangChainRecommendationService:
    """Advanced recommendation service with LangChain and structured templates"""
    
    def __init__(self):
        self.embeddings = None
        self.vectorstore = None
        self.llm = None
        self.retrieval_chain = None
        self.message_history = None
        self.functions = []
        self.template_system = get_template_system()
        self._initialize()
    
    def _initialize(self):
        """Initialize LangChain components"""
        try:
            # 1. Setup Azure OpenAI Embeddings
            logger.info("Initializing Azure OpenAI Embeddings...")
            self.embeddings = AzureOpenAIEmbeddings(
                deployment=Config.AZURE_EMBEDDING_DEPLOYMENT,
                model=Config.AZURE_EMBEDDING_DEPLOYMENT,
                api_key=Config.AZURE_EMBEDDING_API_KEY,
                azure_endpoint=Config.AZURE_EMBEDDING_ENDPOINT,
                api_version=Config.AZURE_OPENAI_API_VERSION
            )
            
            # 2. Connect to existing QdrantDB
            logger.info("Connecting to QdrantDB vectorstore...")
            self.qdrant_client = QdrantClient(
                url=Config.QDRANT_URL,
                api_key=Config.QDRANT_API_KEY
            )
            
            # Initialize Qdrant vector store
            self.vectorstore = Qdrant(
                client=self.qdrant_client,
                collection_name=Config.QDRANT_COLLECTION_NAME,
                embeddings=self.embeddings
            )
            # 3. Setup Azure Chat Model
            logger.info("Initializing Azure ChatOpenAI...")
            self.llm = AzureChatOpenAI(
                azure_deployment=Config.AZURE_DEPLOYMENT_NAME,
                model=Config.AZURE_DEPLOYMENT_NAME,
                api_key=Config.AZURE_OPENAI_API_KEY,
                azure_endpoint=Config.AZURE_OPENAI_ENDPOINT,
                api_version=Config.AZURE_OPENAI_API_VERSION,
                temperature=1,
                max_retries=2
            )
            
            # 4. Setup Conversation Memory
            self.message_history = ChatMessageHistory()
            
            # 5. Define Azure OpenAI Functions
            self._define_functions()
            
            logger.info("LangChain service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize LangChain service: {e}")
            raise
    
    def get_recommendation(
        self, 
        query: str,
        chat_history: Optional[List[Tuple[str, str]]] = None,
        use_template: bool = True,
        use_llm_parsing: bool = True,
        user_profile: Optional[Dict] = None,
        user_name: Optional[str] = None
    ) -> Dict:
        """
        Get recommendation using LangChain with structured templates
        
        Args:
            query: User's question
            chat_history: Optional list of (question, answer) tuples
            use_template: Whether to use structured response templates
            use_llm_parsing: Use LLM to optimize query for better search (default: True)
            
        Returns:
            Dict with answer, sources, and metadata
        """
        try:
            # Get qdrant service for enhanced search
            qdrant_service = get_qdrant_service()
            
            # 1. Use enhanced search with LLM query parsing
            logger.info(f"Searching QdrantDB for: {query[:50]}...")
            
            # Detect if query is vague/general (no specific details)
            query_lower = query.lower()
            vague_query_indicators = [
                'recommend', 'suggest', 'show me', 'give me', 'find me',
                'what', 'any', 'some', 'movies', 'films', 'shows',
                'gợi ý', 'đề xuất', 'tìm', 'phim', 'phim gì'
            ]
            has_specific_details = any(keyword in query_lower for keyword in [
                'genre', 'year', 'actor', 'director', 'country', 'rating',
                'action', 'comedy', 'drama', 'thriller', 'horror', 'romance',
                'thể loại', 'năm', 'diễn viên', 'đạo diễn'
            ])
            
            is_vague_query = any(indicator in query_lower for indicator in vague_query_indicators) and not has_specific_details
            
            # Enhance query with comprehensive user profile information
            enhanced_query = query
            query_enhancements = []
            
            if user_profile:
                # If query is vague, make profile the PRIMARY driver
                if is_vague_query:
                    logger.info("Detected vague query - using profile as primary recommendation driver")
                    
                    # Build profile-based query as primary
                    profile_parts = []
                    
                    # Add favorite genres as primary
                    if user_profile.get('favorite_genres'):
                        favorite_genres = [g for g in user_profile.get('favorite_genres', []) if g]
                        if favorite_genres:
                            genres_str = ", ".join(favorite_genres)
                            profile_parts.append(f"{genres_str} movies")
                            logger.info(f"Using favorite genres as primary: {genres_str}")
                    
                    # Add favorite actors
                    if user_profile.get('favorite_actors'):
                        favorite_actors = [a for a in user_profile.get('favorite_actors', []) if a]
                        if favorite_actors:
                            actors_str = ", ".join(favorite_actors[:3])  # Use more actors for vague queries
                            profile_parts.append(f"starring {actors_str}")
                            logger.info(f"Using favorite actors: {actors_str}")
                    
                    # Add mood preference
                    if user_profile.get('mood_preference'):
                        mood = user_profile.get('mood_preference', '')
                        if mood:
                            profile_parts.append(mood)
                            logger.info(f"Using mood preference: {mood}")
                    
                    # Add watch style
                    if user_profile.get('watch_style'):
                        watch_style = user_profile.get('watch_style', '')
                        if watch_style and len(watch_style) < 80:
                            profile_parts.append(watch_style)
                    
                    # If we have profile parts, use them as the primary query
                    if profile_parts:
                        enhanced_query = " ".join(profile_parts)
                        logger.info(f"Profile-based query created: {enhanced_query}")
                    else:
                        # Fallback: use original query with enhancements
                        if user_profile.get('favorite_genres'):
                            favorite_genres = [g for g in user_profile.get('favorite_genres', []) if g]
                            if favorite_genres:
                                genres_str = ", ".join(favorite_genres[:3])
                                query_enhancements.append(f"{genres_str} genres")
                else:
                    # Query has specific details - enhance with profile as secondary
                    # Add favorite genres (filter out None/empty values)
                    if user_profile.get('favorite_genres'):
                        favorite_genres = [g for g in user_profile.get('favorite_genres', []) if g]
                        if favorite_genres:
                            genres_str = ", ".join(favorite_genres[:3])  # Use top 3 genres
                            query_enhancements.append(f"prefer {genres_str} genres")
                            logger.info(f"Enhanced query with favorite genres: {genres_str}")
                    
                    # Add favorite actors (filter out None/empty values)
                    if user_profile.get('favorite_actors'):
                        favorite_actors = [a for a in user_profile.get('favorite_actors', []) if a]
                        if favorite_actors:
                            actors_str = ", ".join(favorite_actors[:2])  # Use top 2 actors
                            query_enhancements.append(f"starring {actors_str}")
                            logger.info(f"Enhanced query with favorite actors: {actors_str}")
                    
                    # Add mood preference
                    if user_profile.get('mood_preference'):
                        mood = user_profile.get('mood_preference')
                        if mood:
                            query_enhancements.append(f"{mood} mood")
                            logger.info(f"Enhanced query with mood: {mood}")
                    
                    # Add watch style preference
                    if user_profile.get('preferences'):
                        prefs = user_profile.get('preferences', '')
                        if prefs and len(prefs) < 100:  # Only add short preferences
                            query_enhancements.append(prefs)
                
                # Combine all enhancements (for non-vague queries)
                if query_enhancements:
                    enhanced_query = f"{query} ({', '.join(query_enhancements)})"
                    logger.info(f"Full enhanced query created with {len(query_enhancements)} enhancements")
            else:
                logger.warning(f"No user profile found for query enhancement")
            
            if use_llm_parsing:
                # Parse query with LLM to get optimized query and filters
                optimized_query, filters = qdrant_service.parse_query_with_llm(enhanced_query)
                logger.info(f"Using optimized query: {optimized_query[:50]}...")
                
                # Store optimized_query for later use
                base_query_for_search = optimized_query
                
                # Generate embedding with optimized query
                query_embedding = self.embeddings.embed_query(optimized_query)
            else:
                # Use enhanced query
                base_query_for_search = enhanced_query
                query_embedding = self.embeddings.embed_query(enhanced_query)
                filters = {}
            
            # Build Qdrant filter
            from qdrant_client.models import Filter, FieldCondition, MatchValue
            conditions = []
            if filters.get('country'):
                conditions.append(
                    FieldCondition(key="country", match=MatchValue(value=filters['country']))
                )
            if filters.get('type'):
                conditions.append(
                    FieldCondition(key="type", match=MatchValue(value=filters['type']))
                )
            if filters.get('year'):
                conditions.append(
                    FieldCondition(key="year", match=MatchValue(value=filters['year']))
                )
            
            query_filter = Filter(must=conditions) if conditions else None
            
            # Extract already-recommended titles from chat history
            excluded_titles = set()
            if chat_history:
                import re
                # Extract titles from previous recommendations (look for **Title**: pattern)
                for q, a in chat_history:
                    # Method 1: Find titles in markdown format: **Title**: **Movie Title**
                    title_matches = re.findall(r'\*\*Title\*\*:\s*\*\*([^*]+)\*\*', a)
                    for title in title_matches:
                        excluded_titles.add(title.strip().lower())
                    
                    # Method 2: Find titles in format: **Title**: Movie Title (without bold)
                    title_matches2 = re.findall(r'\*\*Title\*\*:\s*([^\n*]+?)(?:\n|$)', a)
                    for title in title_matches2:
                        # Clean up title (remove any remaining markdown, extra spaces)
                        clean_title = re.sub(r'\*\*', '', title).strip()
                        if clean_title and len(clean_title) > 2:
                            excluded_titles.add(clean_title.lower())
                    
                    # Method 3: Extract from lines containing "**Title**:"
                    lines = a.split('\n')
                    for line in lines:
                        if '**Title**:' in line:
                            # Extract title after the colon, handling both bold and non-bold
                            title_match = re.search(r'\*\*Title\*\*:\s*\*?\*?([^*\n]+?)(?:\*\*|$)', line)
                            if title_match:
                                clean_title = title_match.group(1).strip()
                                if clean_title and len(clean_title) > 2:
                                    excluded_titles.add(clean_title.lower())
                    
                    # Method 4: Extract titles from numbered lists (e.g., "1. **Title**", "2. **Title**")
                    numbered_titles = re.findall(r'\d+\.\s*\*\*([^*]+)\*\*', a)
                    for title in numbered_titles:
                        excluded_titles.add(title.strip().lower())
                
                if excluded_titles:
                    logger.info(f"Excluding {len(excluded_titles)} already-recommended titles: {list(excluded_titles)[:5]}")
            
            # Check if user is asking for "other" or "more" films
            query_lower = query.lower()
            asking_for_others = any(keyword in query_lower for keyword in [
                'other', 'more', 'different', 'another', 'else', 'additional', 
                'khác', 'thêm', 'nữa'
            ])
            
            # If asking for other films and we have excluded titles, modify query to get different results
            if asking_for_others and excluded_titles:
                # Add diversity to query to get different results
                enhanced_query_for_search = f"{base_query_for_search} different variety diverse"
                query_embedding = self.embeddings.embed_query(enhanced_query_for_search)
                logger.info("Modified query for diversity when asking for other films")
            
            # Increase search limit if asking for more/other films to have more options
            search_limit = 30 if (asking_for_others and excluded_titles) else (20 if asking_for_others else 10)
            
            # Search using raw Qdrant client for more control
            search_results = self.qdrant_client.search(
                collection_name=Config.QDRANT_COLLECTION_NAME,
                query_vector=query_embedding,
                query_filter=query_filter,
                limit=search_limit  # Get more results to filter out already-recommended titles
            )
            
            # Format context from search results, excluding already-recommended titles
            context = []
            skipped_count = 0
            for result in search_results:
                payload = result.payload
                if not payload:
                    continue
                
                title = payload.get("title", "Unknown")
                # Skip if this title was already recommended
                if title.lower() in excluded_titles:
                    skipped_count += 1
                    logger.debug(f"Skipping already-recommended title: {title}")
                    continue
                    
                context.append({
                    "title": title,
                    "description": payload.get("description", "No description available"),
                    "genre": payload.get("genre", ""),
                    "year": payload.get("year", ""),
                    "type": payload.get("type", "Unknown"),
                    "rating": payload.get("rating", ""),
                    "cast": payload.get("cast", ""),  # Include cast for actor matching
                    "country": payload.get("country", ""),  # Include country for language preference
                    "score": result.score
                })
            
            if skipped_count > 0:
                logger.info(f"Skipped {skipped_count} already-recommended titles from search results")
            
            # Post-filter and boost results by user profile
            if user_profile:
                # Safely extract and clean profile data
                favorite_genres = [g.lower() for g in user_profile.get('favorite_genres', []) if g]
                disliked_genres = [g.lower() for g in user_profile.get('disliked_genres', []) if g]
                favorite_actors = [a.lower() for a in user_profile.get('favorite_actors', []) if a]
                language_prefs = (user_profile.get('language_preference') or '').lower()
                
                # Filter out disliked genres
                if disliked_genres:
                    context = [
                        c for c in context
                        if not any(disliked in (c.get('genre') or '').lower() for disliked in disliked_genres)
                    ]
                    logger.info(f"Filtered out disliked genres: {', '.join(disliked_genres)}")
                
                # Sort by comprehensive match score
                def comprehensive_match_score(item):
                    genre_str = (item.get('genre') or '').lower()
                    cast_str = (item.get('cast') or '').lower()
                    country_str = (item.get('country') or '').lower()
                    
                    # Count matching favorite genres
                    genre_matches = sum(1 for fav in favorite_genres if fav in genre_str)
                    
                    # Count matching favorite actors
                    actor_matches = sum(1 for actor in favorite_actors if actor in cast_str)
                    
                    # Check language/country preference match
                    country_match = 0
                    if language_prefs:
                        # Extract country names from language preference
                        lang_countries = language_prefs.split(',')
                        country_match = any(
                            country.strip() in country_str or country_str in country.strip()
                            for country in lang_countries if country.strip()
                        )
                    
                    # Return tuple for sorting (higher values = better match)
                    # Priority: has_genre_match, genre_count, has_actor_match, actor_count, country_match, original_score
                    return (
                        genre_matches > 0,      # Has favorite genre
                        genre_matches,          # Number of genre matches
                        actor_matches > 0,      # Has favorite actor
                        actor_matches,          # Number of actor matches
                        country_match,          # Matches country preference
                        item.get('score', 0)    # Original relevance score
                    )
                
                context.sort(key=comprehensive_match_score, reverse=True)
                logger.info(f"Re-ranked results by profile: genres={len(favorite_genres)}, actors={len(favorite_actors)}, language={bool(language_prefs)}")
            
            # If we don't have enough results after filtering, try to get more
            if len(context) < 5 and asking_for_others and excluded_titles:
                # Try another search with different query variation
                logger.info(f"Only found {len(context)} unique results, trying additional search...")
                additional_query = f"{base_query_for_search} alternative options"
                additional_embedding = self.embeddings.embed_query(additional_query)
                additional_results = self.qdrant_client.search(
                    collection_name=Config.QDRANT_COLLECTION_NAME,
                    query_vector=additional_embedding,
                    query_filter=query_filter,
                    limit=15
                )
                
                for result in additional_results:
                    if len(context) >= 5:
                        break
                    payload = result.payload
                    if not payload:
                        continue
                    title = payload.get("title", "Unknown")
                    if title.lower() in excluded_titles:
                        continue
                    # Check if we already have this title
                    if any(c["title"].lower() == title.lower() for c in context):
                        continue
                    
                    context.append({
                        "title": title,
                        "description": payload.get("description", "No description available"),
                        "genre": payload.get("genre", ""),
                        "year": payload.get("year", ""),
                        "type": payload.get("type", "Unknown"),
                        "rating": payload.get("rating", ""),
                        "cast": payload.get("cast", ""),
                        "country": payload.get("country", ""),
                        "score": result.score
                    })
            
            # Ensure we have at least 5 results for default recommendations
            # If we have fewer than 5, try to get more from a broader search
            if len(context) < 5:
                logger.warning(f"Only found {len(context)} results, attempting broader search...")
                # Try a more general search
                broader_query = "popular movies" if not base_query_for_search else base_query_for_search
                broader_embedding = self.embeddings.embed_query(broader_query)
                broader_results = self.qdrant_client.search(
                    collection_name=Config.QDRANT_COLLECTION_NAME,
                    query_vector=broader_embedding,
                    query_filter=query_filter,
                    limit=10
                )
                
                for result in broader_results:
                    if len(context) >= 5:
                        break
                    payload = result.payload
                    if not payload:
                        continue
                    title = payload.get("title", "Unknown")
                    # Skip if already in context or excluded
                    if title.lower() in excluded_titles:
                        continue
                    if any(c["title"].lower() == title.lower() for c in context):
                        continue
                    
                    context.append({
                        "title": title,
                        "description": payload.get("description", "No description available"),
                        "genre": payload.get("genre", ""),
                        "year": payload.get("year", ""),
                        "type": payload.get("type", "Unknown"),
                        "rating": payload.get("rating", ""),
                        "cast": payload.get("cast", ""),
                        "country": payload.get("country", ""),
                        "score": result.score
                    })
            
            # Limit to top 5 results (default) or keep all if user specified a number
            # For now, always provide at least 5 for the AI to choose from
            context = context[:max(5, len(context))]
            
            # If no valid context found, return error
            if not context:
                logger.warning(f"No valid documents found for query: {query}")
                return {
                    "answer": "I apologize, but I couldn't find any relevant recommendations for your query. Could you try rephrasing or asking about a different genre, release year, region or type of content?",
                    "sources": [],
                    "chat_history": chat_history or [],
                    "response_type": "error"
                }
            
            # 2. Use template system if enabled
            if use_template:
                # Detect response type
                response_type = self.template_system.detect_response_type(query, context)
                logger.info(f"Detected response type: {response_type.value}")
                
                # Log chat history for debugging
                if chat_history:
                    logger.info(f"Using chat history with {len(chat_history)} messages")
                    for i, (q, a) in enumerate(chat_history[-3:], 1):
                        logger.debug(f"History {i} - Q: {q[:50]}... A: {a[:50]}...")
                
                # Create structured prompt with user profile
                prompt_data = self.template_system.create_structured_prompt(
                    query=query,
                    context=context,
                    chat_history=chat_history,
                    response_type=response_type,
                    user_profile=user_profile,
                    user_name=user_name
                )
                
                # Log the prompt for debugging
                logger.debug(f"System prompt length: {len(prompt_data['system'])} chars")
                logger.debug(f"User prompt length: {len(prompt_data['user'])} chars")
                
                # Call LLM with structured prompt
                messages = [
                    SystemMessage(content=prompt_data["system"]),
                    HumanMessage(content=prompt_data["user"])
                ]
                
                response = self.llm.invoke(messages)
                answer = response.content
                
            else:
                # Use default conversational chain
                formatted_history = []
                if chat_history:
                    for q, a in chat_history:
                        formatted_history.append((q, a))
                
                # Build context string
                context_str = self.template_system.format_context_for_prompt(context)
                
                # Use a simple prompt
                user_message = f"{context_str}\n\nUser question: {query}"
                
                response = self.llm.invoke([HumanMessage(content=user_message)])
                answer = response.content
                response_type = ResponseType.GENERAL_CHAT
            
            return {
                "answer": answer,
                "sources": context,
                "chat_history": chat_history or [],
                "response_type": response_type.value if use_template else "default"
            }
            
        except Exception as e:
            logger.error(f"Failed to get recommendation: {e}")
            return {
                "answer": "I apologize, but I'm having trouble generating a recommendation right now.",
                "sources": [],
                "chat_history": [],
                "response_type": "error"
            }
    
    def chat_with_functions(
        self,
        user_input: str,
        chat_history: List[Tuple[str, str]],
        user_profile: Optional[Dict] = None,
        user_name: Optional[str] = None
    ) -> Tuple[str, List[Tuple[str, str]]]:
        """
        Handle conversation with function calling support
        
        Args:
            user_input: User's message
            chat_history: Conversation history
            user_profile: Optional user profile for personalization
            
        Returns:
            Tuple of (response, updated_chat_history)
        """
        try:
            # Build system message with user profile if available
            system_content = "You are an expert entertainment recommendation assistant with access to specialized functions for detailed queries."
            
            # Add user name for personalized greeting
            if user_name:
                system_content += f"\n\n**USER NAME:** {user_name} (greet them by name when appropriate)"
            
            if user_profile:
                preferences = user_profile.get("preferences", "")
                favorite_genres = user_profile.get("favorite_genres", [])
                disliked_genres = user_profile.get("disliked_genres", [])
                watch_style = user_profile.get("watch_style", "")
                mood_preference = user_profile.get("mood_preference", "")
                
                profile_info = "\n\n**USER PROFILE:**\n"
                if preferences:
                    profile_info += f"- Preferences: {preferences}\n"
                if favorite_genres:
                    genres_str = ", ".join(favorite_genres)
                    profile_info += f"- Favorite genres: {genres_str}\n"
                if disliked_genres:
                    disliked_str = ", ".join(disliked_genres)
                    profile_info += f"- Dislikes: {disliked_str} (AVOID these)\n"
                if watch_style:
                    profile_info += f"- Watch style: {watch_style}\n"
                if mood_preference:
                    profile_info += f"- Mood: {mood_preference}\n"
                profile_info += "\nPersonalize recommendations based on this profile. Reference their tastes naturally."
                system_content += profile_info
            
            messages = [
                {"role": "system", "content": system_content}
            ]
            
            # Add chat history
            for q, a in chat_history:
                messages.append({"role": "user", "content": q})
                messages.append({"role": "assistant", "content": a})
            
            # Add current user input
            messages.append({"role": "user", "content": user_input})
            
            # Call Azure OpenAI with function definitions
            from openai import AzureOpenAI
            client = AzureOpenAI(
                api_version=Config.AZURE_OPENAI_API_VERSION,
                azure_endpoint=Config.AZURE_OPENAI_ENDPOINT,
                api_key=Config.AZURE_OPENAI_API_KEY
            )
            
            response = client.chat.completions.create(
                model=Config.AZURE_DEPLOYMENT_NAME,
                messages=messages,
                functions=self.functions,
                function_call="auto"
            )
            
            message = response.choices[0].message
            
            # Check if function was called
            if message.function_call:
                func_name = message.function_call.name
                args = json.loads(message.function_call.arguments)
                
                logger.info(f"Function called: {func_name} with args: {args}")
                
                # Execute the function
                result = self._execute_function(func_name, args)
                
                # Add function result to chat history
                chat_history.append((user_input, result))
                return result, chat_history
            
            # Regular response without function call
            reply = message.content
            chat_history.append((user_input, reply))
            return reply, chat_history
            
        except Exception as e:
            logger.error(f"Error in chat_with_functions: {e}")
            error_msg = "I apologize, but I encountered an error processing your request."
            chat_history.append((user_input, error_msg))
            return error_msg, chat_history
    
    def _execute_function(self, func_name: str, args: Dict) -> str:
        """Execute the called function and return result with template formatting"""
        try:
            if func_name == "get_film_details":
                return self._get_film_details(args["title"])
            
            elif func_name == "filter_by_genre":
                return self._filter_by_genre(
                    args["genres"],
                    args.get("min_year")
                )
            
            elif func_name == "get_similar_titles":
                return self._get_similar_titles(
                    args["reference_title"],
                    args.get("num_results", 5)
                )
            
            elif func_name == "get_trending_recommendations":
                return self._get_trending_recommendations(
                    args["category"]
                )
            
            else:
                return f"Unknown function: {func_name}"
                
        except Exception as e:
            logger.error(f"Error executing function {func_name}: {e}")
            return f"Error executing function: {str(e)}"
    
    def _define_functions(self):
        """Define Azure OpenAI functions"""
        self.functions = [
            {
                "name": "get_film_details",
                "description": "Get detailed information about a specific film or TV show",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "The title of the movie or TV show"
                        }
                    },
                    "required": ["title"]
                }
            },
            {
                "name": "filter_by_genre",
                "description": "Filter recommendations by specific genres",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "genres": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of genres to filter by"
                        }
                    },
                    "required": ["genres"]
                }
            }
        ]

    def _get_film_details(self, title: str) -> str:
        """Get detailed information about a specific film using template"""
        try:
            # Search vectorstore for exact title
            results = self.vectorstore.similarity_search(
                title,
                k=1
            )
            
            if results:
                doc = results[0]
                metadata = doc.metadata
                
                # Use template for structured output
                details = f"""📽️ **{metadata.get('title', 'Unknown')}** ({metadata.get('year', 'N/A')})

            **Type:** {metadata.get('type', 'Unknown')}
            **Genre:** {metadata.get('genre', 'Unknown')}
            **Rating:** {metadata.get('rating', 'N/A')}
            **Duration:** {metadata.get('duration', 'N/A')}

            **Description:**
            {metadata.get('description', 'No description available.')}

            **Why Watch:**
            ✓ Acclaimed {metadata.get('genre', 'entertainment')} with strong performances
            ✓ Engaging storytelling that keeps you invested
            ✓ Perfect for fans of {metadata.get('genre', 'quality content')}

            Would you like recommendations for similar titles?"""
                            
                return details
            
            return f"Sorry, I couldn't find detailed information about '{title}' in our database."
            
        except Exception as e:
            logger.error(f"Error getting film details: {e}")
            return f"Error retrieving film details: {str(e)}"
    
    def _filter_by_genre(self, genres: List[str], min_year: Optional[int] = None) -> str:
        """Filter recommendations by genre using template"""
        try:
            query = " ".join(genres)
            results = self.vectorstore.similarity_search(query, k=10)
            
            # Filter by genre and year
            filtered = []
            for doc in results:
                doc_genres = doc.metadata.get('genre', '').lower()
                if any(genre.lower() in doc_genres for genre in genres):
                    if min_year:
                        try:
                            year = int(doc.metadata.get('year', 0))
                            if year >= min_year:
                                filtered.append(doc)
                        except:
                            continue
                    else:
                        filtered.append(doc)
            
            if filtered:
                response = f"🎬 **{', '.join(genres)} Films"
                if min_year:
                    response += f" from {min_year} onwards"
                response += "**\n\n"
                
                for i, doc in enumerate(filtered[:5], 1):
                    m = doc.metadata
                    response += f"{i}. **{m.get('title', 'Unknown')}** ({m.get('year', 'N/A')})\n"
                    response += f"   {m.get('description', '')[:100]}...\n"
                    response += f"   Rating: {m.get('rating', 'N/A')}\n\n"
                
                response += f"\n💡 These {', '.join(genres)} titles showcase the genre's best elements.\n"
                response += "\nWould you like more specific recommendations within this genre?"
                
                return response
            
            return f"No titles found matching genres: {', '.join(genres)}"
            
        except Exception as e:
            logger.error(f"Error filtering by genre: {e}")
            return f"Error filtering by genre: {str(e)}"
    
    def _get_similar_titles(self, reference_title: str, num_results: int = 5) -> str:
        """Find similar titles using template"""
        try:
            results = self.vectorstore.similarity_search(
                reference_title,
                k=num_results + 1
            )
            
            # Filter out the reference title itself
            similar = [
                doc for doc in results 
                if doc.metadata.get('title', '').lower() != reference_title.lower()
            ][:num_results]
            
            if similar:
                response = f"🎯 **Similar to '{reference_title}'**\n\n"
                
                for i, doc in enumerate(similar, 1):
                    m = doc.metadata
                    response += f"{i}. **{m.get('title', 'Unknown')}** ({m.get('year', 'N/A')})\n"
                    response += f"   Genre: {m.get('genre', 'Unknown')}\n"
                    response += f"   {m.get('description', '')[:120]}...\n\n"
                
                response += "\n💡 These titles share similar themes, style, or tone.\n"
                response += "\nWhich aspects would you like me to focus on for more recommendations?"
                
                return response
            
            return f"No similar titles found for '{reference_title}'"
            
        except Exception as e:
            logger.error(f"Error finding similar titles: {e}")
            return f"Error finding similar titles: {str(e)}"
    
    def _get_trending_recommendations(self, category: str) -> str:
        """Get trending recommendations using template"""
        try:
            query = f"popular {category} highly rated acclaimed"
            results = self.vectorstore.similarity_search(query, k=7)
            
            if results:
                category_name = category.replace('_', ' ').title()
                response = f"🔥 **Trending {category_name}**\n\n"
                
                for i, doc in enumerate(results, 1):
                    m = doc.metadata
                    response += f"{i}. **{m.get('title', 'Unknown')}** ({m.get('year', 'N/A')})\n"
                    response += f"   Genre: {m.get('genre', 'Unknown')}\n"
                    response += f"   Rating: {m.get('rating', 'N/A')}\n"
                    response += f"   {m.get('description', '')[:100]}...\n\n"
                
                response += "\n💡 These titles are generating buzz for their quality and impact.\n"
                response += "\nWhich of these catches your interest?"
                
                return response
            
            return "No trending recommendations available at the moment."
            
        except Exception as e:
            logger.error(f"Error getting trending recommendations: {e}")
            return f"Error getting trending recommendations: {str(e)}"
    
    def clear_memory(self):
        """Clear conversation memory"""
        if self.message_history:
            self.message_history.clear()
        logger.info("Conversation memory cleared")


# Singleton instance
_langchain_service = None


def get_langchain_service() -> LangChainRecommendationService:
    """Get or create LangChain service instance"""
    global _langchain_service
    if _langchain_service is None:
        _langchain_service = LangChainRecommendationService()
    return _langchain_service