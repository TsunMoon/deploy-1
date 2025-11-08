🎯 Công nghệ AI chính:

1. RAG Pipeline (Retrieval-Augmented Generation)
   - Query Preprocessing: GPT-4o-mini xử lý và tối ưu query (sửa lỗi chính tả, extract filters)
   - Embedding Generation: text-embedding-3-small tạo vector 1536 dimensions cho semantic search
   - Vector Search: Qdrant hybrid search (semantic similarity + exact filters)
   - Response Generation: GPT-4 tạo response dựa trên context từ vector database
   - Flow: User Query → Query Optimization → Embedding → Vector Search → Context → LLM Generation → Response

2. LangChain Framework Integration
   - AzureOpenAIEmbeddings: Wrapper cho text-embedding-3-small model
   - Qdrant VectorStore: LangChain integration với Qdrant vector database
   - AzureChatOpenAI: Wrapper cho GPT-4 chat model với temperature=1.0
   - ChatMessageHistory: Quản lý conversation memory (hiện dùng MemoryService thay thế)
   - SystemMessage/HumanMessage: LangChain message types cho structured prompts

3. Multi-Model Architecture
   - GPT-4o-mini: Query parsing và optimization (temperature=0.2, max_tokens=400)
     → Input: Raw user query (tiếng Việt/Anh)
     → Output: JSON với optimized_summary, filters (country/type/year/genre), search_intent
   - text-embedding-3-small: Embedding generation (1536 dimensions)
     → Input: Optimized query text
     → Output: Vector representation cho semantic search
   - GPT-4: Response generation và function calling (temperature=1.0, max_retries=2)
     → Input: Structured prompt (system + user messages với context)
     → Output: Natural language response hoặc function calls

4. Azure OpenAI Function Calling
   - 4 functions được định nghĩa:
     get_film_details: Lấy thông tin chi tiết về phim/show cụ thể
     filter_by_genre: Lọc recommendations theo genre và năm
     get_similar_titles: Tìm phim tương tự với reference title
     get_trending_recommendations: Lấy trending content theo category
   - GPT-4 tự động detect khi nào cần gọi function
   - Function execution với template formatting

5. Response Template System
   - 7 loại template có cấu trúc:
     movie_recommendation - Gợi ý phim với plot teases và follow-up questions
     tv_show_recommendation - Gợi ý series với season/episode info
     similar_content - Tìm nội dung tương tự với similarity explanations
     genre_filter - Lọc theo thể loại với curated lists
     detailed_info - Thông tin chi tiết về title cụ thể
     trending - Nội dung đang hot với trend insights
     general_chat - Chat tự nhiên với warm tone
   - Auto-detect response type từ query và context
   - Tạo structured prompts với system/user messages

6. Query Optimization với LLM
   - GPT-4o-mini xử lý query trước khi embedding:
     Verify & Correct: Sửa lỗi spelling và grammar
     Analyze & Match: Phân tích và match với database fields (title, description, genre, year, type, rating, country, cast, director)
     Generate Optimized Summary: Tạo summary tối ưu cho embedding search
     Extract Structured Filters: Trích xuất filters (country, type, year, genre) cho exact matching
   - Normalize: "phim mỹ" → "United States", "hành động" → "Action"
   - Fallback: Regex parsing nếu LLM parsing fails

7. Hybrid Search Strategy
   - Semantic Search: Vector similarity search với cosine distance
   - Exact Filters: Qdrant FieldCondition cho country, type, year
   - Top-K Retrieval: Top 5 documents với relevance scores
   - Context Formatting: Format search results thành structured context cho LLM

8. Conversational Memory Integration
   - Session-based memory với max 10 messages
   - Chat history được format và inject vào LLM prompts
   - Context-aware responses dựa trên conversation history
   - Memory service tích hợp với LangChain service

