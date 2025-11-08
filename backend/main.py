# backend/main.py
"""
Entertainment Recommendation API - Main Application
FastAPI backend with QdrantDB, Azure OpenAI, and LangChain
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import auth_router, langchain_recommendation_router
from config import Config
from services.qdrant_service import get_qdrant_service
from services.langchain_service import get_langchain_service
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Validate configuration
try:
    Config.validate()
    logger.info("Configuration validated successfully")
except ValueError as e:
    logger.error(f"Configuration error: {e}")
    raise

# Create FastAPI app
app = FastAPI(
    title="Entertainment Recommendation API",
    description="AI-powered entertainment recommendation system with QdrantDB, LangChain, and Azure OpenAI",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS - Include Railway domains
cors_origins = Config.CORS_ORIGINS + [
    "https://*.railway.app",
    "https://*.vercel.app",
    "http://localhost:3000",
    "http://localhost:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(langchain_recommendation_router)

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Entertainment Recommendation API",
        "version": "2.0.0",
        "description": "AI-powered film and TV show recommendations",
        "endpoints": {
            "documentation": {
                "swagger": "/docs",
                "redoc": "/redoc"
            },
            "original_api": {
                "recommendation": "/api/recommendation",
                "health": "/api/health",
                "collection_stats": "/api/collection/stats"
            },
            "langchain_api": {
                "recommendation": "/api/v2/recommendation",
                "film_details": "/api/v2/film/{title}",
                "filter_by_genre": "/api/v2/filter-by-genre",
                "similar_titles": "/api/v2/similar/{title}",
                "trending": "/api/v2/trending/{category}",
                "clear_memory": "/api/v2/clear-memory",
                "health": "/api/v2/health"
            }
        },
        "features": [
            "QdrantDB vector search",
            "Azure OpenAI chat and embeddings",
            "LangChain conversational memory",
            "Azure OpenAI function calling",
            "Netflix dataset integration"
        ]
    }


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("=" * 80)
    logger.info("Starting Entertainment Recommendation API v2.0...")
    logger.info("=" * 80)
    
    try:
        # Initialize services (they will auto-initialize via singletons)
        # Initialize Qdrant service
        logger.info("📊 Initializing Qdrant service...")
        qdrant_service = get_qdrant_service()

        # Initialize LangChain service
        logger.info("🔗 Initializing LangChain service...")
        langchain_service = get_langchain_service()
        logger.info(f"✅ LangChain initialized with {len(langchain_service.functions)} functions")

        # Get collection stats
        stats = qdrant_service.get_collection_stats()
        logger.info(f"Qdrant collection has {stats['total_points']} items")
        logger.info("=" * 80)
        logger.info("🚀 All services initialized successfully!")
        logger.info("=" * 80)
        logger.info(f"📖 API Documentation: http://localhost:8000/docs")
        logger.info(f"⚡ LangChain API: http://localhost:8000/api/v2/recommendation")
        logger.info(f"💬 Chat Interface: Open frontend to start chatting")
        logger.info("=" * 80)
        
    except Exception as e:
        logger.error("=" * 80)
        logger.error(f"❌ Failed to initialize services: {e}")
        logger.error("=" * 80)
        raise


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("=" * 80)
    logger.info("Shutting down Entertainment Recommendation API...")
    logger.info("=" * 80)
    
    # Clear LangChain memory
    try:
        from services.langchain_service import get_langchain_service
        langchain_service = get_langchain_service()
        langchain_service.clear_memory()
        logger.info("✅ LangChain memory cleared")
    except Exception as e:
        logger.warning(f"⚠️  Could not clear LangChain memory: {e}")
    
    logger.info("👋 Goodbye!")
    logger.info("=" * 80)


# Health check endpoint for load balancers
@app.get("/health")
async def health_check():
    """Simple health check endpoint"""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "services": {
            "qdrant": "operational",
            "openai": "operational",
            "langchain": "operational"
        }
    }


# Main entry point
if __name__ == "__main__":
    import uvicorn
    
    # Get port from environment variable (Railway) or use default
    port = int(os.getenv("PORT", 8000))
    
    logger.info(f"Starting server on port {port}...")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info",
        access_log=True
    )