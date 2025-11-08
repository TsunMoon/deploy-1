from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue, SearchParams
from openai import AzureOpenAI
from typing import List, Dict, Optional, Tuple
from config import Config
from services.query_parser_service import get_query_parser_service
import logging
import json
import re

logger = logging.getLogger(__name__)


class QdrantService:
    """Service for Qdrant Cloud operations"""
    
    def __init__(self):
        """Initialize Qdrant client and Azure OpenAI client for embeddings"""
        try:
            # Initialize Qdrant client
            self.client = QdrantClient(
                url=Config.QDRANT_URL,
                api_key=Config.QDRANT_API_KEY,
            )
            logger.info(f"Successfully connected to Qdrant Cloud at {Config.QDRANT_URL}")
            
            # Initialize Azure OpenAI client for embeddings
            self.embedding_client = AzureOpenAI(
                api_version=Config.AZURE_OPENAI_API_VERSION,
                azure_endpoint=Config.AZURE_EMBEDDING_ENDPOINT,
                api_key=Config.AZURE_EMBEDDING_API_KEY,
            )
            logger.info("Successfully initialized Azure OpenAI embedding client")
            
            # Initialize LLM client for query parsing and optimization
            self.llm_client = AzureOpenAI(
                api_version=Config.AZURE_OPENAI_API_VERSION,
                azure_endpoint=Config.AZURE_OPENAI_LLM_DETECT_INPUT_ENDPOINT,
                api_key=Config.AZURE_OPENAI_LLM_DETECT_INPUT_API_KEY,
            )
            logger.info("Successfully initialized LLM client for query parsing")
            
            self.llm_deployment = Config.AZURE_OPENAI_LLM_DETECT_INPUT_DEPLOYMENT_NAME
            
            # Initialize QueryParserService for basic query parsing
            self.query_parser = get_query_parser_service()
            logger.info("Successfully initialized QueryParserService")
            
            self.collection_name = Config.QDRANT_COLLECTION_NAME
            
        except Exception as e:
            logger.error(f"Failed to initialize Qdrant service: {e}")
            raise
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding vector for a text using Azure OpenAI
        
        Args:
            text: Text to generate embedding for
            
        Returns:
            List of floats representing the embedding vector
        """
        try:
            response = self.embedding_client.embeddings.create(
                input=text,
                model=Config.AZURE_EMBEDDING_DEPLOYMENT
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            raise
    
    def parse_query_with_llm(self, query: str) -> Tuple[str, Dict[str, any]]:
        """
        Use LLM to intelligently verify, correct, and transform user query for optimal embedding
        
        This function:
        1. Verifies spelling and grammar
        2. Analyzes and matches query against database fields
        3. Generates an optimized summary for embedding search
        4. Extracts structured filters for exact matching
        
        Args:
            query: User query string in any language
            
        Returns:
            Tuple of (optimized_query_string, extracted_filters_dict)
        """
        
        # System prompt for intelligent query processing
        system_prompt = """You are an AI assistant specialized in processing search queries for movies and TV shows.

**Your Tasks:**

1. **Verify & Correct**: Check and fix spelling and grammar errors in the query
2. **Analyze & Match**: Analyze which database fields the query relates to:
   - title: movie/show name
   - description: content description, plot
   - genre: categories (Action, Comedy, Drama, Horror, Romance, Thriller, Sci-Fi, Documentary, Animation, Crime, Mystery, Adventure)
   - year: release year
   - type: Movie or TV Show
   - rating: age rating (PG, PG-13, R, TV-MA, etc.)
   - duration: runtime
   - country: country (United States, Vietnam, South Korea, Thailand, China, Japan, India, etc.)
   - cast: actors
   - director: director

3. **Generate Optimized Summary**: Create a concise, clear summary optimized for semantic search

**Output format (JSON):**
```json
{
  "corrected_query": "corrected query if errors found",
  "optimized_summary": "concise summary optimized for embedding search",
  "filters": {
    "country": "standardized country name or null",
    "type": "Movie or TV Show or null",
    "year": year number or null,
    "genre": "standardized genre name or null"
  },
  "matched_fields": ["list of matched fields"],
  "search_intent": "brief description of search intent"
}
```

**Examples:**

Input: "Tìm fim kinh di hàn quốc 2020"
Output:
```json
{
  "corrected_query": "Tìm phim kinh dị Hàn Quốc 2020",
  "optimized_summary": "Korean horror movies from 2020",
  "filters": {
    "country": "South Korea",
    "type": "Movie",
    "year": 2020,
    "genre": "Horror"
  },
  "matched_fields": ["genre", "country", "year", "type"],
  "search_intent": "Find Korean horror movies released in 2020"
}
```

Input: "phim có Leonardo DiCaprio đóng"
Output:
```json
{
  "corrected_query": "phim có Leonardo DiCaprio đóng",
  "optimized_summary": "movies starring Leonardo DiCaprio",
  "filters": {},
  "matched_fields": ["cast", "title"],
  "search_intent": "Find movies with actor Leonardo DiCaprio"
}
```

Input: "american action movies 2021"
Output:
```json
{
  "corrected_query": "american action movies 2021",
  "optimized_summary": "American action movies from 2021",
  "filters": {
    "country": "United States",
    "type": "Movie",
    "year": 2021,
    "genre": "Action"
  },
  "matched_fields": ["country", "genre", "year", "type"],
  "search_intent": "Find American action movies released in 2021"
}
```

**Important Notes:**
- If no spelling errors, corrected_query = input query
- optimized_summary should be concise, clear, using important keywords
- filters should only contain information that can be used for exact filtering
- Return pure JSON without markdown wrapper
- Support both Vietnamese and English queries
- Normalize country names: "phim mỹ/american/usa" → "United States", "phim hàn/korean" → "South Korea", "phim việt/vietnamese" → "Vietnam"
- Normalize genres: "hành động/action" → "Action", "kinh dị/horror" → "Horror", "hài/comedy" → "Comedy"
"""

        user_prompt = f"Process this query: '{query}'"
        
        try:
            logger.info("🤖 Using LLM to process and optimize query...")
            
            # Call LLM for intelligent query processing
            response = self.llm_client.chat.completions.create(
                model=self.llm_deployment,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.2,  # Low temperature for consistent parsing
                max_tokens=400
            )
            
            # Extract and parse JSON response
            llm_output = response.choices[0].message.content.strip()
            logger.info(f"🤖 LLM raw output: {llm_output[:200]}...")
            
            # Clean up response (remove markdown if present)
            if "```json" in llm_output:
                llm_output = llm_output.split("```json")[1].split("```")[0].strip()
            elif "```" in llm_output:
                llm_output = llm_output.split("```")[1].strip()
            
            # Parse JSON
            parsed = json.loads(llm_output)
            
            # Extract components
            corrected_query = parsed.get('corrected_query', query)
            optimized_summary = parsed.get('optimized_summary', query)
            filters = parsed.get('filters', {})
            matched_fields = parsed.get('matched_fields', [])
            search_intent = parsed.get('search_intent', '')
            
            # Log results
            if corrected_query != query:
                logger.info(f"✏️ Corrected query: {corrected_query}")
            logger.info(f"📝 Optimized summary: {optimized_summary}")
            logger.info(f"🎯 Matched fields: {', '.join(matched_fields)}")
            logger.info(f"💡 Search intent: {search_intent}")
            
            # Clean up null values in filters
            filters = {k: v for k, v in filters.items() if v is not None}
            
            if filters:
                logger.info(f"🔍 Extracted filters: {filters}")
            
            # Return optimized summary for embedding and filters for exact matching
            return optimized_summary, filters
            
        except Exception as e:
            logger.warning(f"⚠️ LLM processing failed: {e}")
            logger.info("📝 Falling back to regex parsing...")
            
            # Fallback: return original query and regex-based filters
            filters = self.parse_query_regex(query)
            return query, filters
    
    def parse_query_regex(self, query: str) -> Dict[str, any]:
        """
        Fallback regex-based query parsing (simplified version)
        
        Args:
            query: User query string
            
        Returns:
            Dictionary with extracted filters
        """
        parsed = {}
        
        # Basic country patterns
        country_patterns = [
            (r'\b(?:phim\s+)?mỹ\b', 'United States'),
            (r'\b(?:phim\s+)?việt\b', 'Vietnam'),
            (r'\b(?:phim\s+)?hàn\b', 'South Korea'),
            (r'\b(?:american|usa|us)\b', 'United States'),
            (r'\b(?:korean|korea)\b', 'South Korea'),
            (r'\b(?:vietnamese|vietnam)\b', 'Vietnam'),
            (r'\b(?:japanese|japan)\b', 'Japan'),
            (r'\b(?:chinese|china)\b', 'China'),
        ]
        
        for pattern, country in country_patterns:
            if re.search(pattern, query.lower()):
                parsed['country'] = country
                break
        
        # Basic type detection
        if re.search(r'\b(?:movies?|phim)\b', query.lower()):
            parsed['type'] = 'Movie'
        elif re.search(r'\b(?:tv\s*shows?|series)\b', query.lower()):
            parsed['type'] = 'TV Show'
        
        # Basic year extraction
        year_match = re.search(r'(?:năm\s+)?(\d{4})', query)
        if year_match:
            parsed['year'] = int(year_match.group(1))
        
        # Basic genre detection
        genre_patterns = [
            (r'\b(?:hành động|action)\b', 'Action'),
            (r'\b(?:hài|comedy)\b', 'Comedy'),
            (r'\b(?:kinh dị|horror)\b', 'Horror'),
            (r'\b(?:tình cảm|romance)\b', 'Romance'),
            (r'\b(?:drama)\b', 'Drama'),
            (r'\b(?:thriller)\b', 'Thriller'),
        ]
        
        for pattern, genre in genre_patterns:
            if re.search(pattern, query.lower()):
                parsed['genre'] = genre
                break
        
        return parsed
    
    def build_filter(self, parsed_query: Dict[str, any]) -> Optional[Filter]:
        """
        Build Qdrant filter from parsed query parameters
        
        Args:
            parsed_query: Dictionary with parsed parameters
            
        Returns:
            Qdrant Filter object or None
        """
        conditions = []
        
        # Filter by country
        if parsed_query.get('country'):
            conditions.append(
                FieldCondition(
                    key="country",
                    match=MatchValue(value=parsed_query['country'])
                )
            )
        
        # Filter by type (Movie or TV Show)
        if parsed_query.get('type'):
            conditions.append(
                FieldCondition(
                    key="type",
                    match=MatchValue(value=parsed_query['type'])
                )
            )
        
        # Filter by year
        if parsed_query.get('year'):
            conditions.append(
                FieldCondition(
                    key="year",
                    match=MatchValue(value=parsed_query['year'])
                )
            )
        
        # Note: Genre filtering is more complex as it's a comma-separated list
        # We'll handle it in post-processing if needed
        
        if conditions:
            return Filter(must=conditions)
        
        return None
    
    def search_titles(
        self,
        query: str,
        limit: int = 10,
        country: Optional[str] = None,
        content_type: Optional[str] = None,
        year: Optional[int] = None,
        use_llm_parsing: bool = True
    ) -> List[Dict]:
        """
        Search for titles in Qdrant based on query and filters
        
        Args:
            query: Search query text
            limit: Maximum number of results to return
            country: Filter by country (e.g., "United States")
            content_type: Filter by type ("Movie" or "TV Show")
            year: Filter by release year
            use_llm_parsing: Use LLM to optimize query (default: True)
            
        Returns:
            List of matching titles with their metadata
        """
        try:
            # If LLM parsing is enabled, process the query
            if use_llm_parsing:
                optimized_query, llm_filters = self.parse_query_with_llm(query)
                
                # Merge LLM filters with explicit filters (explicit filters take precedence)
                country = country or llm_filters.get('country')
                content_type = content_type or llm_filters.get('type')
                year = year or llm_filters.get('year')
                
                # Use optimized query for embedding
                query_for_embedding = optimized_query
            else:
                query_for_embedding = query
            
            # Generate embedding for the query
            query_vector = self.generate_embedding(query_for_embedding)
            
            # Build filter conditions
            conditions = []
            if country:
                conditions.append(
                    FieldCondition(key="country", match=MatchValue(value=country))
                )
            if content_type:
                conditions.append(
                    FieldCondition(key="type", match=MatchValue(value=content_type))
                )
            if year:
                conditions.append(
                    FieldCondition(key="year", match=MatchValue(value=year))
                )
            
            query_filter = Filter(must=conditions) if conditions else None
            
            # Perform search
            search_results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                query_filter=query_filter,
                limit=limit,
                with_payload=True
            )
            
            # Format results
            results = []
            for result in search_results:
                title_data = {
                    'score': result.score,
                    **result.payload
                }
                results.append(title_data)
            
            logger.info(f"Found {len(results)} results for query: {query[:50]}...")
            return results
            
        except Exception as e:
            logger.error(f"Failed to search titles: {e}")
            raise
    
    def get_top_titles(
        self,
        query: str,
        auto_parse: bool = True
    ) -> List[Dict]:
        """
        Get top titles based on natural language query
        
        This is the main function to handle queries like:
        - "Top 5 movies in United States"
        - "Top 10 TV shows in Japan"
        - "Best action movies from 2024"
        
        Args:
            query: Natural language query
            auto_parse: Whether to automatically parse the query (default: True)
            
        Returns:
            List of matching titles with metadata
        """
        try:
            if auto_parse:
                # Parse the query to extract parameters
                parsed = self.query_parser.parse_query(query)
                
                # Search with parsed parameters
                results = self.search_titles(
                    query=parsed['query_text'],
                    limit=parsed['limit'],
                    country=parsed['country'],
                    content_type=parsed['type'],
                    year=parsed['year']
                )
                
                # Post-process for genre if needed
                if parsed.get('genre'):
                    results = [
                        r for r in results 
                        if parsed['genre'].lower() in r.get('genre', '').lower()
                    ]
                
                return results
            else:
                # Direct search without parsing
                return self.search_titles(query=query)
                
        except Exception as e:
            logger.error(f"Failed to get top titles: {e}")
            raise
    
    def get_recommendations(
        self,
        query: str,
        limit: int = 5,
        use_llm_parsing: bool = True
    ) -> List[Dict]:
        """
        Get personalized recommendations based on user query
        
        Args:
            query: User's preference or description
            limit: Number of recommendations to return
            use_llm_parsing: Use LLM to optimize query (default: True)
            
        Returns:
            List of recommended titles
        """
        try:
            # If LLM parsing is enabled, optimize the query
            if use_llm_parsing:
                optimized_query, filters = self.parse_query_with_llm(query)
                query_for_embedding = optimized_query
            else:
                query_for_embedding = query
                filters = {}
            
            # Generate embedding for user's preferences
            query_vector = self.generate_embedding(query_for_embedding)
            
            # Build filter from extracted filters
            query_filter = self.build_filter(filters) if filters else None
            
            # Search for similar titles
            search_results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                query_filter=query_filter,
                limit=limit,
                with_payload=True
            )
            
            # Format results
            recommendations = []
            for result in search_results:
                title_data = {
                    'relevance_score': result.score,
                    **result.payload
                }
                recommendations.append(title_data)
            
            logger.info(f"Generated {len(recommendations)} recommendations")
            return recommendations
            
        except Exception as e:
            logger.error(f"Failed to get recommendations: {e}")
            raise
    
    def get_collection_stats(self) -> Dict:
        """
        Get statistics about the Qdrant collection
        
        Returns:
            Dictionary with collection statistics
        """
        try:
            collection_info = self.client.get_collection(self.collection_name)
            
            stats = {
                'collection_name': self.collection_name,
                'total_points': collection_info.points_count,
                'vector_size': collection_info.config.params.vectors.size,
                'distance': collection_info.config.params.vectors.distance.name,
                'status': collection_info.status.name
            }
            
            logger.info(f"Collection stats: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get collection stats: {e}")
            raise
    
    def search_by_filters_only(
        self,
        country: Optional[str] = None,
        content_type: Optional[str] = None,
        year: Optional[int] = None,
        genre: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict]:
        """
        Search titles using only filters (no semantic search)
        
        Args:
            country: Filter by country
            content_type: Filter by type ("Movie" or "TV Show")
            year: Filter by release year
            genre: Filter by genre (partial match)
            limit: Maximum number of results
            
        Returns:
            List of matching titles
        """
        try:
            # Build filter conditions
            conditions = []
            if country:
                conditions.append(
                    FieldCondition(key="country", match=MatchValue(value=country))
                )
            if content_type:
                conditions.append(
                    FieldCondition(key="type", match=MatchValue(value=content_type))
                )
            if year:
                conditions.append(
                    FieldCondition(key="year", match=MatchValue(value=year))
                )
            
            query_filter = Filter(must=conditions) if conditions else None
            
            # Use scroll to get all matching records
            results, _ = self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=query_filter,
                limit=limit,
                with_payload=True
            )
            
            # Format results
            titles = [result.payload for result in results]
            
            # Post-filter by genre if specified
            if genre:
                titles = [
                    t for t in titles 
                    if genre.lower() in t.get('genre', '').lower()
                ]
            
            logger.info(f"Found {len(titles)} titles matching filters")
            return titles[:limit]
            
        except Exception as e:
            logger.error(f"Failed to search by filters: {e}")
            raise


# Singleton instance
_qdrant_service = None


def get_qdrant_service() -> QdrantService:
    """Get or create Qdrant service instance"""
    global _qdrant_service
    if _qdrant_service is None:
        _qdrant_service = QdrantService()
    return _qdrant_service
