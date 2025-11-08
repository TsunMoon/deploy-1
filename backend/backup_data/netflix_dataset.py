from datasets import load_dataset
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


class NetflixDatasetLoader:
    """Load Netflix shows dataset from HuggingFace"""
    
    def __init__(self):
        self.dataset = None
    
    def load_netflix_dataset(self) -> List[Dict]:
        """
        Load Netflix shows from HuggingFace dataset
        
        Args:
            max_items: Maximum number of items to load (default 100)
            
        Returns:
            List of movie/show dictionaries
        """
        try:
            logger.info("Loading Netflix dataset from HuggingFace...")
            self.dataset = load_dataset('hugginglearners/netflix-shows', split='train')
            
            # Convert to list of dicts with required fields
            movies = []
            for i, item in enumerate(self.dataset):
                # Filter by release year between 2020 and 2021
                release_year = item.get('release_year')
                if release_year is None or not (2020 <= release_year <= 2021):
                    continue
                
                # Map dataset fields to our schema
                movie = {
                    "title": item.get('title', 'Unknown'),
                    "description": item.get('description', ''),
                    "genre": item.get('listed_in', 'Unknown'),  # genres
                    "year": item.get('release_year', 'Unknown'),
                    "type": item.get('type', 'Unknown'),  # Movie or TV Show
                    "rating": item.get('rating', 'Unknown'),
                    "duration": item.get('duration', 'Unknown'),
                    "country": item.get('country', 'Unknown'),
                    "cast": item.get('cast', 'Unknown'),
                    "director": item.get('director', 'Unknown')
                }
                
                # Only add if has description
                if movie["description"] and movie["title"]:
                    movies.append(movie)
            
            logger.info(f"Loaded {len(movies)} Netflix titles from HuggingFace")
            return movies
            
        except Exception as e:
            logger.error(f"Failed to load Netflix dataset: {e}")
            return []


def get_netflix_data() -> List[Dict]:
    """Helper function to load Netflix data"""
    loader = NetflixDatasetLoader()
    return loader.load_netflix_dataset()

