from typing import Dict
from config import Config
import logging
import re

logger = logging.getLogger(__name__)


class QueryParserService:
    """Service for parsing user input to extract filters and parameters"""
    
    def __init__(self):
        """Initialize QueryParserService"""
        # Keywords related to movies/TV shows
        self.movie_keywords = [
            'movie', 'movies', 'film', 'films', 'tv show', 'tv shows', 
            'series', 'show', 'shows', 'netflix', 'watch', 'watching',
            'recommend', 'recommendation', 'suggest', 'suggestion',
            'actor', 'actress', 'director', 'cast', 'genre', 'rating',
            'action', 'comedy', 'drama', 'thriller', 'horror', 'romance',
            'documentary', 'animation', 'sci-fi', 'fantasy', 'crime',
            'mystery', 'adventure', 'family', 'western', 'war',
            'phim', 'phim ảnh', 'xem phim', 'bộ phim', 'diễn viên',
            'đạo diễn', 'hành động', 'kinh dị', 'tình cảm', 'hài',
            'anime', 'cartoon', 'season', 'episode', 'streaming',
            'blockbuster', 'oscar', 'imdb', 'released', 'premiere',
            'year', 'năm'  # Time-related in movie context
        ]
        
        # Keywords for non-movie questions (out of scope)
        # NOTE: Time-related words removed as users may ask about movies by month/year
        self.non_movie_keywords = [
            'weather', 'temperature', 'forecast', 'rain', 'sunny',
            'thời tiết', 'nhiệt độ', 'trời', 'mưa', 'nắng',
            'name', 'your name', 'who are you', 'what are you',
            'tên', 'tên bạn', 'bạn là ai', 'bạn là gì',
            'calculate', 'math', 'solve', 'equation',
            'tính', 'toán', 'giải',
            'news', 'current events', 'politics', 'sports',
            'tin tức', 'thể thao', 'chính trị',
            'recipe', 'cooking', 'food', 'restaurant',
            'công thức', 'nấu ăn', 'món ăn', 'nhà hàng',
            'translate', 'translation', 'dịch', 'meaning',
            'book', 'novel', 'read', 'sách', 'tiểu thuyết', 
            'đọc', 'Tháng', 'Month', 'January', 'February', 
            'March', 'April', 'May', 'June', 'July', 'August', 
            'September', 'October', 'November', 'December', 
            'Jan', 'Feb', 'Mar', 'Apr', 'Jun', 'Jul', 'Aug', 
            'Sep', 'Oct', 'Nov', 'Dec'
        ]
        logger.info("Successfully initialized QueryParserService")
    
    def is_movie_related(self, query: str) -> bool:
        """
        Check if the query is related to movies/TV shows
        
        Args:
            query: User query string
            
        Returns:
            True if query is movie-related, False otherwise
        """
        query_lower = query.lower()
        
        # Check for movie-related keywords FIRST (higher priority)
        # This prevents movie/show titles from being rejected
        for keyword in self.movie_keywords:
            if keyword in query_lower:
                logger.info(f"Query contains movie keyword: '{keyword}'")
                return True
        
        # Then check for non-movie keywords
        for keyword in self.non_movie_keywords:
            if keyword in query_lower:
                logger.info(f"Query contains non-movie keyword: '{keyword}'")
                return False
        
        # Check for movie inquiry patterns (e.g., "Tell me more about [title]", "What is [title]")
        # These patterns suggest the user is asking about a specific title
        movie_inquiry_patterns = [
            r'\b(tell\s+me\s+more\s+about|tell\s+me\s+about|what\s+is|what\'?s|who\s+is|who\'?s|describe|explain)\b',
            r'\b(about|info|information|details|detail)\b.*\b(movie|film|show|series|tv)\b',
            r'\b(movie|film|show|series|tv)\b.*\b(about|info|information|details)\b',
            r'\b(find|search|look\s+for)\b.*\b(movie|film|show|series)\b',
        ]
        
        for pattern in movie_inquiry_patterns:
            if re.search(pattern, query_lower):
                logger.info(f"Query matches movie inquiry pattern: '{pattern}'")
                return True
        
        # If no specific keywords found, check for context patterns
        # Questions like "What is...", "Who is..." might be about movies
        movie_context_patterns = [
            r'\b(best|top|good|great|popular|famous)\b.*\b(watch|see|view)\b',
            r'\b(what|which|any)\b.*\b(good|watch|see|recommend)\b',
            r'\bshow\s+me\b',
            r'\blooking\s+for\b',
            r'\bfind\b.*\b(watch|see)\b',
        ]
        
        for pattern in movie_context_patterns:
            if re.search(pattern, query_lower):
                logger.info(f"Query matches movie context pattern: '{pattern}'")
                return True
        
        # If query is short and doesn't contain non-movie keywords, 
        # it might be a movie title or simple inquiry - allow it by default
        # This handles cases like "2 Hearts", "Inception", etc.
        if len(query.split()) <= 5 and not any(kw in query_lower for kw in self.non_movie_keywords):
            logger.info(f"Query appears to be a potential movie title or simple inquiry: '{query}'")
            return True
        
        logger.info("Query does not appear to be movie-related")
        return False
    
    def parse_query(self, query: str) -> Dict[str, any]:
        """
        Parse user query to extract filters and parameters
        
        Args:
            query: User query string (e.g., "Top 5 movies in United States")
            
        Returns:
            Dictionary with parsed parameters: {
                'limit': int,
                'country': str or None,
                'type': str or None (Movie/TV Show),
                'query_text': str
            }
        """
        parsed = {
            'limit': 10,  # Default limit
            'country': None,
            'type': None,
            'year': None,
            'genre': None,
            'query_text': query
        }
        
        # Extract number (e.g., "Top 5", "Top 10")
        number_match = re.search(r'top\s+(\d+)', query.lower())
        if number_match:
            parsed['limit'] = int(number_match.group(1))
        
        # Extract country
        # Common country patterns
        country_patterns = [
            r'in\s+(united\s+states?|usa?|america)',
            r'in\s+(united\s+kingdom|uk|britain)',
            r'in\s+(japan)',
            r'in\s+(canada)',
            r'in\s+(australia)',
            r'in\s+(india)',
            r'in\s+(france)',
            r'in\s+(germany)',
            r'in\s+(south\s+korea|korea)',
            r'in\s+(spain)',
            r'in\s+(mexico)',
            r'in\s+(brazil)',
            r'in\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)',  # Generic country name
        ]
        
        for pattern in country_patterns:
            country_match = re.search(pattern, query, re.IGNORECASE)
            if country_match:
                country = country_match.group(1)
                # Normalize common variations
                country_map = {
                    'united states': 'United States',
                    'usa': 'United States',
                    'us': 'United States',
                    'america': 'United States',
                    'united kingdom': 'United Kingdom',
                    'uk': 'United Kingdom',
                    'britain': 'United Kingdom',
                    'south korea': 'South Korea',
                    'korea': 'South Korea',
                }
                parsed['country'] = country_map.get(country.lower(), country.title())
                break
        
        # Extract type (Movie or TV Show)
        if re.search(r'\bmovies?\b', query.lower()):
            parsed['type'] = 'Movie'
        elif re.search(r'\btv\s*shows?\b|\bseries\b|\bshows?\b', query.lower()):
            parsed['type'] = 'TV Show'
        
        # Extract year
        year_match = re.search(r'(?:from|in|year|năm)\s+(\d{4})', query.lower())
        if year_match:
            parsed['year'] = int(year_match.group(1))

        # Extract genre
        genres = [
            'action', 'comedy', 'drama', 'thriller', 'horror', 'romance', 
            'sci-fi', 'science fiction', 'fantasy', 'documentary', 'animation',
            'crime', 'mystery', 'adventure', 'family', 'western', 'war'
        ]
        for genre in genres:
            if re.search(r'\b' + genre + r'\b', query.lower()):
                parsed['genre'] = genre.title()
                break
        
        logger.info(f"Parsed query: {parsed}")
        return parsed


# Singleton instance
_query_parser_service = None


def get_query_parser_service() -> QueryParserService:
    """Get or create QueryParserService instance"""
    global _query_parser_service
    if _query_parser_service is None:
        _query_parser_service = QueryParserService()
    return _query_parser_service
