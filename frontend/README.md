# Netflix Movie Recommendation API - Backend

FastAPI backend service for AI-powered Netflix movie and TV show recommendations using ChromaDB, Azure OpenAI, LangChain, and Text-to-Speech.

## 🌟 Features

### Core Features
- **ChromaDB Vector Database**: Advanced semantic search specifically for Netflix content
- **Dual API Architecture**: Original API + Enhanced LangChain API with response templates
- **Azure OpenAI Integration**: Chat completions and text embeddings
- **LangChain Framework**: Conversational AI with memory and function calling
- **Smart Query Parsing**: Automatic extraction of filters (country, genre, year, type)
- **Text-to-Speech**: Convert responses to Vietnamese audio using HuggingFace MMS-TTS
- **Session Management**: Persistent conversation memory across requests
- **Response Templates**: 7 structured response types for consistent, engaging answers

### Advanced Capabilities
- **Azure OpenAI Function Calling**: Extended capabilities for film details, genre filtering, similarity search
- **Conversational Memory**: Context-aware responses using conversation history
- **Structured Templates**: Movie/TV show recommendations, trending content, detailed info, genre filters
- **RESTful API**: Clean FastAPI endpoints with automatic OpenAPI documentation
- **MVC Architecture**: Well-organized code with services, routers, and models

## 📁 Project Structure

```
backend/
├── main.py                        # FastAPI application entry point
├── config.py                      # Configuration and environment variables
├── requirements.txt               # Python dependencies
│
├── models/
│   ├── __init__.py
│   └── schemas.py                 # Pydantic request/response models
│
├── routers/
│   ├── __init__.py
│   ├── recommendation.py          # Original API endpoints (/api/*)
│   └── langchain_recommendation.py # LangChain API with templates (/api/v2/*)
│
├── services/
│   ├── __init__.py
│   ├── qdrant_service.py          # Qdrant vector database service
│   ├── openai_service.py          # Azure OpenAI chat & embeddings
│   ├── langchain_service.py       # LangChain conversational AI
│   ├── memory_service.py          # Session-based conversation memory
│   ├── response_templates.py      # Structured response formatting system
│   └── tts_service.py             # Vietnamese Text-to-Speech
│
├── migrate_data/
│   ├── setup_qdrant_cloud.py      # Qdrant data migration script
│   ├── netflix_dataset.py         # Netflix dataset loader
│   ├── run_netflix_data.py        # Data processing utilities
│   └── create_indexes.py          # Database indexing
│
├── chromadb/                      # ChromaDB storage (if used)
├── audio_outputs/                 # Generated TTS audio files
└── .env                           # Environment variables (create from .env.example)
```

## 🚀 Quick Start

### 1. Setup ChromaDB

ChromaDB will be automatically initialized when you first run the application. The database will be stored locally in the `chroma_data` directory. No additional setup is required.

The system will:
1. Create a new collection for Netflix content
2. Load initial Netflix dataset
3. Generate embeddings using Azure OpenAI
4. Store the vectors for semantic search

### 2. Create Virtual Environment

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create `.env` file in the backend directory:

```env
# ChromaDB Configuration (optional - defaults will be used if not specified)
CHROMADB_PERSIST_DIR=./chroma_data
CHROMADB_COLLECTION_NAME=netflix_collection

# Azure OpenAI (Chat Model)
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-chat-api-key
AZURE_DEPLOYMENT_NAME=gpt-4

# Azure OpenAI (Embeddings Model)
AZURE_EMBEDDING_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_EMBEDDING_API_KEY=your-embedding-api-key
AZURE_EMBEDDING_DEPLOYMENT=text-embedding-3-small
```

### 5. Migrate Data to Qdrant

```powershell
python migrate_data/setup_qdrant_cloud.py
```

This loads the Netflix dataset and creates vector embeddings.

### 6. Run the Server

```powershell
python main.py
```

Or using uvicorn:

```powershell
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API Root**: `http://localhost:8000`
- **Swagger Docs**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## 🏗️ Architecture

### Service Layer

**QdrantService** (`services/qdrant_service.py`)
- Vector similarity search
- Smart query parsing (extracts filters from natural language)
- Embedding generation using Azure OpenAI
- Filter building for precise searches

**OpenAIService** (`services/openai_service.py`)
- Azure OpenAI chat completions
- Recommendation generation with context
- Follow-up question generation
- Conversation history integration

**LangChainService** (`services/langchain_service.py`)
- Conversational AI with LangChain framework
- Azure OpenAI function calling (4 functions)
- Response template system integration
- Memory-aware conversations

**MemoryService** (`services/memory_service.py`)
- Session-based conversation storage
- In-memory message history (max 10 messages)
- History formatting for prompts

**ResponseTemplates** (`services/response_templates.py`)
- 7 response types (movie, TV show, similar, genre, detailed, trending, general)
- Auto-detection of response type from query
- Structured prompt generation
- Consistent formatting across responses

**TTSService** (`services/tts_service.py`)
- Vietnamese text-to-speech
- Facebook MMS-TTS model
- Audio file generation and management

## 🎯 API Endpoints

### Original API (`/api/*`)

#### POST `/api/recommendation`
Get AI-powered recommendation with Qdrant context and conversation memory.

**Request:**
```json
{
  "question": "Can you recommend a thriller movie?",
  "use_context": true,
  "top_k": 3,
  "session_id": "session_123"
}
```

**Response:**
```json
{
  "answer": "Based on your interest in thrillers...",
  "audio_url": "/audio/response_123456.wav",
  "related_questions": ["What about sci-fi?", "Any newer releases?"],
  "context_used": [...],
  "session_id": "session_123"
}
```

#### POST `/api/search/top-titles`
Search titles using natural language queries.

**Parameters:** `query` (string), `limit` (int, default: 10)

**Example:**
```powershell
curl -X POST "http://localhost:8000/api/search/top-titles?query=Top%205%20movies&limit=5"
```

#### GET `/api/search/by-filters`
Search using explicit filters.

**Parameters:** `country`, `content_type`, `year`, `genre`, `limit`

#### DELETE `/api/session/{session_id}`
Clear conversation history for a session.

#### GET `/api/health`
Health check endpoint.

#### GET `/api/collection/stats`
Get Qdrant collection statistics.

---

### LangChain API (`/api/v2/*`)

#### POST `/api/v2/recommendation`
Enhanced recommendation with response templates and function calling.

**Request:**
```json
{
  "query": "Recommend a thriller movie similar to Inception",
  "chat_history": [],
  "session_id": "session_123",
  "use_functions": false,
  "use_template": true,
  "response_type": null
}
```

**Response:**
```json
{
  "answer": "🎬 Great choice! Since you love thrillers...",
  "audio_url": "/audio/response_123456.wav",
  "sources": [...],
  "chat_history": [...],
  "function_called": null,
  "response_type": "movie_recommendation"
}
```

#### GET `/api/v2/film/{title}`
Get detailed information about a specific film.

#### POST `/api/v2/filter-by-genre`
Filter films by genre and year.

**Body:** `{"genres": ["Action", "Sci-Fi"], "min_year": 2020}`

#### GET `/api/v2/similar/{title}`
Get titles similar to a reference film.

**Parameters:** `title` (string), `num_results` (int, default: 5)

#### GET `/api/v2/trending/{category}`
Get trending recommendations.

**Categories:** `movies`, `tv_shows`, `all`

#### GET `/api/v2/session-history/{session_id}`
Get conversation history for a session.

#### POST `/api/v2/clear-memory`
Clear conversation memory (session or global).

**Parameters:** `session_id` (optional)

#### GET `/api/v2/response-types`
List available response template types.

#### GET `/api/v2/health`
Health check for LangChain service.

## 💡 Usage Examples

### Python SDK Examples

```python
from services.qdrant_service import get_qdrant_service
from services.langchain_service import get_langchain_service

# Qdrant Service
qdrant = get_qdrant_service()

# Natural language queries
results = qdrant.get_top_titles("Top 5 movies in United States")
results = qdrant.get_top_titles("Best action movies from 2024")
results = qdrant.get_recommendations("I love romantic comedies")

# Filter-based search
results = qdrant.search_by_filters_only(
    country="United States",
    content_type="Movie",
    year=2024,
    genre="Action",
    limit=10
)

# LangChain Service
langchain = get_langchain_service()

# Get recommendation with memory
result = langchain.get_recommendation(
    query="Recommend a thriller movie",
    chat_history=[],
    use_template=True
)

# Use function calling
answer, history = langchain.chat_with_functions(
    query="Show me details about Inception",
    chat_history=[]
)
```

### API Examples

```powershell
# Original API - Simple recommendation
curl -X POST "http://localhost:8000/api/recommendation" `
  -H "Content-Type: application/json" `
  -d '{"question": "Top 5 movies in United States", "use_context": true, "top_k": 5}'

# LangChain API - Template-based recommendation
curl -X POST "http://localhost:8000/api/v2/recommendation" `
  -H "Content-Type: application/json" `
  -d '{"query": "Recommend thriller movies", "use_template": true}'

# Get film details
curl "http://localhost:8000/api/v2/film/Inception"

# Get trending
curl "http://localhost:8000/api/v2/trending/movies"
```

## 🧪 Testing

### Interactive API Documentation
Visit `http://localhost:8000/docs` for Swagger UI with interactive testing.

### Manual Testing

**Test Original API:**
```powershell
curl -X POST "http://localhost:8000/api/recommendation" `
  -H "Content-Type: application/json" `
  -d '{"question": "Top 5 thriller movies", "use_context": true, "top_k": 5}'
```

**Test LangChain API:**
```powershell
curl -X POST "http://localhost:8000/api/v2/recommendation" `
  -H "Content-Type: application/json" `
  -d '{"query": "Recommend action movies", "use_template": true}'
```

**Test Health:**
```powershell
curl "http://localhost:8000/api/health"
curl "http://localhost:8000/api/v2/health"
```

## 🔧 Troubleshooting

### ChromaDB Issues

**Error:** `Failed to initialize ChromaDB`

**Solutions:**
- Check if `chroma_data` directory exists and has write permissions
- Delete the `chroma_data` directory and restart if database is corrupted
- Ensure enough disk space for vector storage
- Check if Azure OpenAI embedding service is accessible
- Verify Python environment has all required dependencies:
  ```bash
  pip install chromadb numpy typing-extensions

### Azure OpenAI Errors

**Error:** `Authentication failed` or `Resource not found`

**Solutions:**
- Verify endpoint URLs (no trailing slash)
- Check API keys are correct
- Ensure deployment names match your Azure resources
- Confirm API version: `2024-07-01-preview`

### Collection Not Found

The collection will be created automatically when running the migration script:
```powershell
python migrate_data/setup_qdrant_cloud.py
```

### TTS Model Download

First run downloads ~200MB from HuggingFace. This is normal and only happens once. Model is cached in `.cache/huggingface/`.

### CORS Errors

Add your frontend URL to `CORS_ORIGINS` in `config.py`:
```python
CORS_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://your-frontend-url",
]
```

### Import Errors

Ensure you're using the virtual environment:
```powershell
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 📦 Key Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| **FastAPI** | 0.119.0 | Web framework and API routing |
| **Uvicorn** | 0.37.0 | ASGI server |
| **Qdrant Client** | ≥1.7.0 | Vector database client |
| **OpenAI** | ≥1.54.0 | Azure OpenAI SDK |
| **LangChain** | ≥0.3.7 | LLM framework and chains |
| **LangChain OpenAI** | ≥0.2.9 | OpenAI integration for LangChain |
| **LangChain Community** | ≥0.3.7 | Community integrations |
| **Transformers** | 4.40.0 | HuggingFace models (TTS) |
| **Torch** | ≥2.6.0 | PyTorch for ML models |
| **Pydantic** | 2.12.3 | Data validation |
| **Python-dotenv** | 1.1.1 | Environment variable management |

See `requirements.txt` for complete dependency list.

## 🎬 Response Template System

The LangChain API includes 7 structured response types for consistent, engaging answers:

1. **movie_recommendation** - Personalized movie suggestions with plot teases
2. **tv_show_recommendation** - Series recommendations with episode/season info
3. **similar_content** - Find titles similar to a reference
4. **genre_filter** - Curated lists by genre and criteria
5. **detailed_info** - Complete information about a specific title
6. **trending** - Currently popular and buzzing content
7. **general_chat** - Natural conversational responses

The system auto-detects the appropriate template based on the query, or you can force a specific type using the `response_type` parameter.

## 🔐 Environment Variables

Required environment variables (create `.env` file):

```env
# Qdrant Database
QDRANT_URL=https://your-cluster.qdrant.io:6333
QDRANT_API_KEY=your_api_key
QDRANT_COLLECTION_NAME=netflix_movies_tv_shows

# Azure OpenAI - Chat Model
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your_chat_key
AZURE_DEPLOYMENT_NAME=gpt-4

# Azure OpenAI - Embeddings Model  
AZURE_EMBEDDING_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_EMBEDDING_API_KEY=your_embedding_key
AZURE_EMBEDDING_DEPLOYMENT=text-embedding-3-small
```

## 📝 License

MIT License - See LICENSE file for details.

## 🤝 Contributing

This is a workshop project for AI Batch 3. Feel free to fork and experiment!

## 📞 Support

- **API Documentation**: http://localhost:8000/docs
- **Issues**: Check server logs for detailed error messages
- **Version**: 2.0.0
