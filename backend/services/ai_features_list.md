# Main AI Features List in the System

1. **LangChain**:

   - Framework orchestration for RAG pipeline
   - Components: AzureOpenAIEmbeddings, Qdrant VectorStore, AzureChatOpenAI
   - Conversational Memory: Session-based (max 10 messages), remembers user chat context
   - Structured prompts with SystemMessage/HumanMessage

2. **HuggingFace**:

   - Dataset: `hugginglearners/netflix-shows` (8,807 movies/TV shows)
   - Load and process Netflix dataset for vector database

3. **RAG (Retrieval-Augmented Generation)**:

   - Pipeline: Query → Optimization (GPT-4o-mini) → Embedding (text-embedding-3-small) → Vector Search (Qdrant) → Context → LLM Generation (GPT-4) → Response
   - Query Optimization: GPT-4o-mini fixes errors, extracts filters, normalizes ("phim mỹ" → "United States")
   - Hybrid Search: Combines semantic search (vector similarity) + exact filters (country, type, year)

4. **Azure OpenAI Multi-Model**:

   - GPT-4o-mini: Query parsing and optimization
   - text-embedding-3-small: Embedding generation (1536 dimensions)
   - GPT-4: Response generation and function calling

5. **Qdrant Vector Database**:

   - Semantic search with cosine similarity
   - Collection: netflix_movies_tv_shows (8,807 documents)
   - Top-K retrieval: Top 5 documents with relevance scores

6. **Azure OpenAI Function Calling**:

   - 4 functions: get_film_details, filter_by_genre, get_similar_titles, get_trending_recommendations
   - GPT-4 automatically detects and calls functions when needed

7. **Response Template System**:
   - 7 template types: movie_recommendation, tv_show_recommendation, similar_content, genre_filter, detailed_info, trending, general_chat
   - Auto-detect response type from query and context
