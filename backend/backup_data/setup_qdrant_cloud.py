#!/usr/bin/env python3
"""
Qdrant Cloud Setup and Data Population Script
This script creates a collection in Qdrant Cloud and populates it with entertainment data
"""

import os
import sys
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, PayloadSchemaType
from openai import AzureOpenAI
import hashlib
import logging
from typing import List, Dict
from backend.backup_data.netflix_dataset import NetflixDatasetLoader

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
QDRANT_VECTOR_SIZE = int(os.getenv("QDRANT_VECTOR_SIZE", "1536"))

AZURE_EMBEDDING_API_KEY = os.getenv("AZURE_EMBEDDING_API_KEY")
AZURE_EMBEDDING_ENDPOINT = os.getenv("AZURE_EMBEDDING_ENDPOINT")
AZURE_EMBEDDING_DEPLOYMENT = os.getenv("AZURE_EMBEDDING_DEPLOYMENT", "text-embedding-3-small")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-07-01-preview")

def validate_config():
    """Validate required configuration"""
    required_vars = {
        "QDRANT_URL": QDRANT_URL,
        "QDRANT_API_KEY": QDRANT_API_KEY,
        "AZURE_EMBEDDING_API_KEY": AZURE_EMBEDDING_API_KEY,
        "AZURE_EMBEDDING_ENDPOINT": AZURE_EMBEDDING_ENDPOINT,
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
        logger.info("Successfully connected to Qdrant Cloud")
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
        logger.info("Successfully initialized Azure OpenAI client")
        return client
    except Exception as e:
        logger.error(f"Failed to initialize Azure OpenAI: {e}")
        raise


def create_collection(qdrant_client: QdrantClient):
    """Create Qdrant collection if it doesn't exist"""
    try:
        # Check if collection exists
        collections = qdrant_client.get_collections().collections
        collection_names = [col.name for col in collections]
        
        if QDRANT_COLLECTION_NAME in collection_names:
            logger.info(f"Collection '{QDRANT_COLLECTION_NAME}' already exists")
            
            # Ask user if they want to recreate it
            response = input(f"Do you want to delete and recreate the collection? (y/n): ").strip().lower()
            if response == 'y':
                qdrant_client.delete_collection(QDRANT_COLLECTION_NAME)
                logger.info(f"Deleted existing collection '{QDRANT_COLLECTION_NAME}'")
            else:
                logger.info("Using existing collection")
                return
        
        # Create new collection
        qdrant_client.create_collection(
            collection_name=QDRANT_COLLECTION_NAME,
            vectors_config=VectorParams(
                size=QDRANT_VECTOR_SIZE,
                distance=Distance.COSINE
            )
        )
        logger.info(f"Successfully created collection '{QDRANT_COLLECTION_NAME}'")
        
        # Create payload indexes for filtering
        logger.info("Creating payload indexes...")
        create_payload_indexes(qdrant_client)
        
    except Exception as e:
        logger.error(f"Failed to create collection: {e}")
        raise


def create_payload_indexes(qdrant_client: QdrantClient):
    """
    Create indexes on payload fields for filtering
    
    Args:
        qdrant_client: Qdrant client instance
    """
    try:
        # Define fields to index
        indexes = {
            "type": PayloadSchemaType.KEYWORD,      # Movie or TV Show
            "country": PayloadSchemaType.KEYWORD,   # Country
            "rating": PayloadSchemaType.KEYWORD,    # Rating (e.g., PG-13, R)
            "year": PayloadSchemaType.INTEGER,      # Release year
        }
        
        # Create index for each field
        for field_name, schema_type in indexes.items():
            try:
                logger.info(f"  Creating index for field '{field_name}'...")
                qdrant_client.create_payload_index(
                    collection_name=QDRANT_COLLECTION_NAME,
                    field_name=field_name,
                    field_schema=schema_type
                )
                logger.info(f"  ✓ Index created for '{field_name}'")
            except Exception as e:
                if "already exists" in str(e).lower():
                    logger.info(f"  Index for '{field_name}' already exists")
                else:
                    raise
        
        logger.info("✓ All payload indexes created successfully")
        
    except Exception as e:
        logger.error(f"Failed to create payload indexes: {e}")
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


def create_text_for_embedding(movie: Dict) -> str:
    """
    Create a comprehensive text representation for embedding
    
    CHUNKING STRATEGY:
    - Each movie/show is ONE chunk (no content splitting)
    - Optimized text structure for semantic search
    - Focus on description + key metadata
    """
    # Ensure year is properly formatted
    year = movie.get('year', 'Unknown')
    year_str = str(year) if year != 'Unknown' else 'Unknown'
    
    # Primary content (weighted for semantic search)
    description = movie.get('description', '').strip()
    title = movie.get('title', 'Unknown')
    genre = movie.get('genre', 'Unknown')
    
    # Build text optimized for semantic search
    # Format: Most important info first for better embedding quality
    parts = [
        f"{title}",  # Title first for strong signal
        f"Description: {description}",  # Main content
        f"Genre: {genre}",  # Important for recommendations
        f"Type: {movie.get('type', 'Unknown')}",
        f"Year: {year_str}",
        f"Rating: {movie.get('rating', 'Unknown')}",
        f"Duration: {movie.get('duration', 'Unknown')}",
    ]
    
    # Add optional fields if they exist and are meaningful
    if movie.get('cast') and movie.get('cast') != 'Unknown':
        parts.append(f"Cast: {movie['cast']}")
    if movie.get('director') and movie.get('director') != 'Unknown':
        parts.append(f"Director: {movie['director']}")
    if movie.get('country') and movie.get('country') != 'Unknown':
        parts.append(f"Country: {movie['country']}")
    
    return " | ".join(parts)


def generate_point_id(movie: Dict) -> int:
    """Generate a unique numeric ID for a movie based on its content"""
    content = f"{movie.get('title', '')}{movie.get('year', '')}{movie.get('type', '')}"
    hash_value = hashlib.md5(content.encode()).hexdigest()
    # Convert first 15 hex chars to integer for better uniqueness
    return int(hash_value[:15], 16)


def migrate_data_to_qdrant(
    qdrant_client: QdrantClient,
    azure_client: AzureOpenAI,
    movies: List[Dict],
    chunk_size: int = 100
):
    """
    Migrate Netflix data to Qdrant with chunking
    
    Args:
        qdrant_client: Qdrant client instance
        azure_client: Azure OpenAI client instance
        movies: List of movie dictionaries
        chunk_size: Number of records to process per chunk (default: 100)
    """
    try:
        total_movies = len(movies)
        logger.info(f"Starting migration of {total_movies} movies to Qdrant")
        logger.info(f"Processing in chunks of {chunk_size} records")
        
        # Process movies in chunks
        for i in range(0, total_movies, chunk_size):
            chunk = movies[i:i + chunk_size]
            chunk_num = (i // chunk_size) + 1
            total_chunks = (total_movies + chunk_size - 1) // chunk_size
            
            logger.info(f"Processing chunk {chunk_num}/{total_chunks} ({len(chunk)} records)")
            
            points = []
            for idx, movie in enumerate(chunk):
                try:
                    # Validate required fields
                    if not movie.get('title') or not movie.get('description'):
                        logger.warning(f"Skipping movie with missing title or description")
                        continue
                    
                    # Create text for embedding
                    text = create_text_for_embedding(movie)
                    
                    # Generate embedding
                    embedding = generate_embedding(azure_client, text)
                    
                    # Generate unique ID
                    point_id = generate_point_id(movie)
                    
                    # Ensure year is an integer for indexing compatibility
                    payload = movie.copy()
                    year_value = payload.get('year')
                    if isinstance(year_value, int) and 1900 <= year_value <= 2100:
                        payload['year'] = year_value
                    else:
                        # Remove year field if it's not a valid integer
                        payload.pop('year', None)
                    
                    # Create point
                    point = PointStruct(
                        id=point_id,
                        vector=embedding,
                        payload=payload
                    )
                    points.append(point)
                    
                    # Log progress every 10 items
                    if (idx + 1) % 10 == 0:
                        logger.info(f"  Generated embeddings for {idx + 1}/{len(chunk)} items in current chunk")
                    
                except Exception as e:
                    logger.error(f"Failed to process movie '{movie.get('title', 'Unknown')}': {e}")
                    continue
            
            # Upload chunk to Qdrant with retry logic
            if points:
                max_retries = 3
                retry_count = 0
                while retry_count < max_retries:
                    try:
                        qdrant_client.upsert(
                            collection_name=QDRANT_COLLECTION_NAME,
                            points=points
                        )
                        logger.info(f"✓ Successfully uploaded chunk {chunk_num}/{total_chunks} ({len(points)} points)")
                        break
                    except Exception as e:
                        retry_count += 1
                        if retry_count >= max_retries:
                            logger.error(f"Failed to upload chunk {chunk_num} after {max_retries} attempts: {e}")
                            logger.warning(f"Skipping chunk {chunk_num} and continuing with next chunk...")
                            break
                        else:
                            logger.warning(f"Retry {retry_count}/{max_retries} for chunk {chunk_num}: {e}")
                            import time
                            time.sleep(2 ** retry_count)  # Exponential backoff
        
        logger.info(f"✓ Migration completed! Total movies processed: {total_movies}")
        
        # Get collection info
        collection_info = qdrant_client.get_collection(QDRANT_COLLECTION_NAME)
        logger.info(f"Collection '{QDRANT_COLLECTION_NAME}' now contains {collection_info.points_count} points")
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        raise


def main():
    """Main execution function"""
    try:
        logger.info("=" * 60)
        logger.info("Qdrant Cloud Setup and Data Migration")
        logger.info("=" * 60)
        
        # Validate configuration
        if not validate_config():
            sys.exit(1)
        
        # Initialize clients
        logger.info("\n[1/5] Initializing clients...")
        qdrant_client = initialize_qdrant_client()
        azure_client = initialize_azure_openai()
        
        # Create collection
        logger.info("\n[2/5] Creating Qdrant collection...")
        create_collection(qdrant_client)
        
        # Load Netflix dataset
        logger.info("\n[3/5] Loading Netflix dataset...")
        loader = NetflixDatasetLoader()
        movies = loader.load_netflix_dataset()
        
        if not movies:
            logger.error("No movies loaded. Exiting.")
            sys.exit(1)
        
        logger.info(f"Loaded {len(movies)} movies")
        
        # Confirm migration
        logger.info("\n[4/5] Ready to migrate data to Qdrant")
        response = input(f"Proceed with migrating {len(movies)} movies? (y/n): ").strip().lower()
        
        if response != 'y':
            logger.info("Migration cancelled by user")
            sys.exit(0)
        
        # Migrate data
        logger.info("\n[5/5] Migrating data to Qdrant...")
        
        # CHUNKING CONFIGURATION:
        # - chunk_size: Number of records to process per batch
        # - Adjust based on dataset size and API rate limits
        # - Recommended: 100-200 for datasets < 5000 records
        optimal_chunk_size = min(150, max(50, len(movies) // 10))
        logger.info(f"Using optimal chunk size: {optimal_chunk_size}")
        
        migrate_data_to_qdrant(
            qdrant_client=qdrant_client,
            azure_client=azure_client,
            movies=movies,
            chunk_size=optimal_chunk_size
        )
        
        logger.info("\n" + "=" * 60)
        logger.info("✓ Setup and migration completed successfully!")
        logger.info("=" * 60)
        
    except KeyboardInterrupt:
        logger.info("\nOperation cancelled by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"\nFatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

