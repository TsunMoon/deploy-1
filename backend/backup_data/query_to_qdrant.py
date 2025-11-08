#!/usr/bin/env python3
"""
Query Qdrant Database Script
This script demonstrates how to query the Qdrant database with a simple user query string
"""

import os
import sys
import json
import logging
import re
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue
from openai import AzureOpenAI
from typing import List, Dict, Optional

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Configuration
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
QDRANT_COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME", "netflix_movies_tv_shows")

AZURE_EMBEDDING_API_KEY = os.getenv("AZURE_EMBEDDING_API_KEY")
AZURE_EMBEDDING_ENDPOINT = os.getenv("AZURE_EMBEDDING_ENDPOINT")
AZURE_EMBEDDING_DEPLOYMENT = os.getenv("AZURE_EMBEDDING_DEPLOYMENT", "text-embedding-3-small")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-07-01-preview")

# LLM Configuration for Query Parsing - Use specialized LLM detect input config
AZURE_LLM_ENDPOINT = os.getenv("AZURE_OPENAI_LLM_DETECT_INPUT_ENDPOINT", os.getenv("AZURE_OPENAI_ENDPOINT"))
AZURE_LLM_API_KEY = os.getenv("AZURE_OPENAI_LLM_DETECT_INPUT_API_KEY", os.getenv("AZURE_OPENAI_API_KEY"))
AZURE_LLM_DEPLOYMENT = os.getenv("AZURE_OPENAI_LLM_DETECT_INPUT_DEPLOYMENT_NAME", "gpt-4o-mini")
# ============================================================================
# USER INPUT - MODIFY THIS TO TEST DIFFERENT QUERIES
# ============================================================================

USER_QUERY = "Phim Mỹ hành động năm 2021"  # Test Vietnamese query

# ============================================================================


def validate_config():
    """Validate required configuration"""
    required_vars = {
        "QDRANT_URL": QDRANT_URL,
        "QDRANT_API_KEY": QDRANT_API_KEY,
        "AZURE_EMBEDDING_API_KEY": AZURE_EMBEDDING_API_KEY,
        "AZURE_EMBEDDING_ENDPOINT": AZURE_EMBEDDING_ENDPOINT,
        "AZURE_LLM_API_KEY": AZURE_LLM_API_KEY,
        "AZURE_LLM_ENDPOINT": AZURE_LLM_ENDPOINT,
        "AZURE_LLM_DEPLOYMENT": AZURE_LLM_DEPLOYMENT,
    }
    
    missing = [name for name, value in required_vars.items() if not value]
    
    if missing:
        logger.error(f"Missing required environment variables: {', '.join(missing)}")
        logger.error("Please set these in your .env file")
        return False
    
    return True


def initialize_qdrant_client() -> QdrantClient:
    """Initialize and return Qdrant client"""
    try:
        client = QdrantClient(
            url=QDRANT_URL,
            api_key=QDRANT_API_KEY,
        )
        logger.info("✓ Successfully connected to Qdrant Cloud")
        return client
    except Exception as e:
        logger.error(f"Failed to connect to Qdrant: {e}")
        raise


def initialize_azure_openai() -> AzureOpenAI:
    """Initialize and return Azure OpenAI client"""
    try:
        client = AzureOpenAI(
            api_key=AZURE_EMBEDDING_API_KEY,
            api_version=AZURE_OPENAI_API_VERSION,
            azure_endpoint=AZURE_EMBEDDING_ENDPOINT
        )
        logger.info("✓ Successfully initialized Azure OpenAI client")
        return client
    except Exception as e:
        logger.error(f"Failed to initialize Azure OpenAI: {e}")
        raise


def generate_embedding(azure_client: AzureOpenAI, text: str) -> List[float]:
    """Generate embedding for a text using Azure OpenAI"""
    try:
        response = azure_client.embeddings.create(
            input=text,
            model=AZURE_EMBEDDING_DEPLOYMENT
        )
        return response.data[0].embedding
    except Exception as e:
        logger.error(f"Failed to generate embedding: {e}")
        raise

def initialize_llm_client() -> AzureOpenAI:
    """Initialize and return LLM Azure OpenAI client for query parsing"""
    try:
        client = AzureOpenAI(
            api_key=AZURE_LLM_API_KEY,
            api_version=AZURE_OPENAI_API_VERSION,
            azure_endpoint=AZURE_LLM_ENDPOINT
        )
        logger.info("✓ Successfully initialized LLM Azure OpenAI client")
        return client
    except Exception as e:
        logger.error(f"Failed to initialize LLM Azure OpenAI: {e}")
        raise


def parse_query_with_llm(llm_client: AzureOpenAI, query: str) -> tuple[str, Dict[str, any]]:
    """
    Use LLM to intelligently verify, correct, and transform user query for optimal embedding
    
    This function:
    1. Verifies spelling and grammar
    2. Analyzes and matches query against database fields
    3. Generates an optimized summary for embedding search
    4. Extracts structured filters for exact matching
    
    Args:
        llm_client: Azure OpenAI client for LLM
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
        response = llm_client.chat.completions.create(
            model=AZURE_LLM_DEPLOYMENT,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.2,  # Low temperature for consistent parsing
            max_tokens=400
        )
        
        # Extract and parse JSON response
        llm_output = response.choices[0].message.content.strip()
        logger.info(f"🤖 LLM raw output:\n{llm_output}")
        
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
        filters = parse_query_regex(query)
        return query, filters


def parse_query_regex(query: str) -> Dict[str, any]:
    """
    Fallback regex-based query parsing (simplified version of original)
    
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
    if re.search(r'\b(?:hành động|action)\b', query.lower()):
        parsed['genre'] = 'Action'
    elif re.search(r'\b(?:hài|comedy)\b', query.lower()):
        parsed['genre'] = 'Comedy'
    
    return parsed


def build_filter(parsed_query: Dict[str, any]) -> Optional[Filter]:
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
        logger.info(f"🌍 Adding country filter: {parsed_query['country']}")
    
    # Filter by type (Movie or TV Show)
    if parsed_query.get('type'):
        conditions.append(
            FieldCondition(
                key="type",
                match=MatchValue(value=parsed_query['type'])
            )
        )
        logger.info(f"🎬 Adding type filter: {parsed_query['type']}")
    
    # Filter by year
    if parsed_query.get('year'):
        conditions.append(
            FieldCondition(
                key="year",
                match=MatchValue(value=parsed_query['year'])
            )
        )
        logger.info(f"📅 Adding year filter: {parsed_query['year']}")
    
    # Genre filtering would need to be done post-search since it's stored as text
    # We'll handle it in the search function
    
    if conditions:
        return Filter(must=conditions)
    return None


def search_qdrant(
    qdrant_client: QdrantClient,
    query_vector: List[float],
    query_filter: Optional[Filter] = None,
    limit: int = 5
) -> List[Dict]:
    """
    Search Qdrant database with query vector and optional filters
    
    Args:
        qdrant_client: Qdrant client instance
        query_vector: Query embedding vector
        query_filter: Optional filter for exact matching
        limit: Maximum number of results
        
    Returns:
        List of search results with scores
    """
    try:
        # Perform search with filter
        search_results = qdrant_client.search(
            collection_name=QDRANT_COLLECTION_NAME,
            query_vector=query_vector,
            query_filter=query_filter,
            limit=limit
        )
        
        # Format results
        results = []
        for hit in search_results:
            result = {
                "score": hit.score,
                "id": hit.id,
                **hit.payload
            }
            results.append(result)
        
        return results
        
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise


def display_results(results: List[Dict]):
    """
    Display search results in a formatted way
    
    Args:
        results: List of search results
    """
    if not results:
        logger.info("\n❌ No results found matching your criteria")
        return
    
    logger.info(f"\n{'='*80}")
    logger.info(f"Found {len(results)} results:")
    logger.info(f"{'='*80}\n")
    
    for idx, result in enumerate(results, 1):
        score = result.get('score', 0)
        title = result.get('title', 'Unknown')
        content_type = result.get('type', 'Unknown')
        year = result.get('year', 'Unknown')
        rating = result.get('rating', 'Unknown')
        duration = result.get('duration', 'Unknown')
        genre = result.get('genre', 'Unknown')
        description = result.get('description', 'No description available')
        
        logger.info(f"[{idx}] {title}")
        logger.info(f"    Score: {score:.4f}")
        logger.info(f"    Type: {content_type}")
        logger.info(f"    Year: {year}")
        logger.info(f"    Rating: {rating}")
        logger.info(f"    Duration: {duration}")
        logger.info(f"    Genre: {genre}")
        logger.info(f"    Description: {description}")
        
        # Optional: Display additional fields
        if result.get('cast'):
            cast = result['cast']
            if len(cast) > 100:
                cast = cast[:100] + "..."
            logger.info(f"    Cast: {cast}")
        
        if result.get('director'):
            director = result['director']
            logger.info(f"    Director: {director}")
        
        if result.get('country'):
            country = result['country']
            logger.info(f"    Country: {country}")
        
        logger.info("")  # Empty line between results


def display_query_parameters():
    """Display the current query parameters"""
    logger.info("\n" + "="*80)
    logger.info("QUERY PARAMETERS")
    logger.info("="*80)
    logger.info(f"Query: {USER_QUERY}")
    logger.info("="*80 + "\n")


def get_collection_stats(qdrant_client: QdrantClient):
    """Display collection statistics"""
    try:
        collection_info = qdrant_client.get_collection(QDRANT_COLLECTION_NAME)
        logger.info(f"\nCollection Stats:")
        logger.info(f"  - Total points: {collection_info.points_count}")
        logger.info(f"  - Vector size: {collection_info.config.params.vectors.size}")
        logger.info(f"  - Distance metric: {collection_info.config.params.vectors.distance}")
    except Exception as e:
        logger.warning(f"Could not retrieve collection stats: {e}")


def main():
    """Main execution function"""
    try:
        logger.info("="*80)
        logger.info("QDRANT DATABASE QUERY TOOL")
        logger.info("="*80)
        
        # Validate configuration
        if not validate_config():
            sys.exit(1)
        
        # Initialize clients
        logger.info("\nInitializing clients...")
        qdrant_client = initialize_qdrant_client()
        azure_client = initialize_azure_openai()
        llm_client = initialize_llm_client()
        
        # Get collection stats
        get_collection_stats(qdrant_client)
        
        # Display query parameters
        display_query_parameters()
        
        # Parse query for filters using LLM
        logger.info("Processing query with LLM...")
        optimized_query, parsed_filters = parse_query_with_llm(llm_client, USER_QUERY)
        
        # Build filter from parsed filters
        query_filter = build_filter(parsed_filters)
        
        # Generate query embedding using optimized query
        logger.info("Generating query embedding from optimized query...")
        query_vector = generate_embedding(azure_client, optimized_query)
        logger.info(f"✓ Generated embedding vector (dimension: {len(query_vector)})")
        
        # Search database
        logger.info("\nSearching Qdrant database...")
        results = search_qdrant(
            qdrant_client=qdrant_client,
            query_vector=query_vector,
            query_filter=query_filter,
            limit=5
        )
        
        # Display results
        display_results(results)
        
        logger.info("="*80)
        logger.info("✓ Query completed successfully!")
        logger.info("="*80)
        
    except KeyboardInterrupt:
        logger.info("\n\nOperation cancelled by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"\nFatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
