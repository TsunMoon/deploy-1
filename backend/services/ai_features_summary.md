# Tổng hợp Công nghệ AI - Netflix Recommendation System

## 🎯 RAG Pipeline (Retrieval-Augmented Generation)

**Flow chính:**

- **Query Preprocessing** → GPT-4o-mini: Sửa lỗi, extract filters, tối ưu query
- **Embedding** → text-embedding-3-small: Tạo vector 1536D cho semantic search
- **Vector Search** → Qdrant: Hybrid search (semantic + exact filters)
- **Generation** → GPT-4: Tạo response từ context

**Kết quả:** User Query → Optimized Query → Embedding → Search → Context → LLM → Response

---

## 🤖 Multi-Model Architecture

### GPT-4o-mini (Query Parsing)

- **Vai trò:** Preprocessing và optimization
- **Input:** Raw query (Việt/Anh)
- **Output:** JSON (optimized_summary, filters, search_intent)
- **Config:** temperature=0.2, max_tokens=400

### text-embedding-3-small (Embeddings)

- **Vai trò:** Semantic search
- **Input:** Optimized text
- **Output:** Vector 1536 dimensions

### GPT-4 (Generation)

- **Vai trò:** Response generation + Function calling
- **Input:** Structured prompt (context + query + history)
- **Output:** Natural language response
- **Config:** temperature=1.0, max_retries=2

---

## 🔗 LangChain Integration

**Components:**

- `AzureOpenAIEmbeddings` - Wrapper cho embedding model
- `Qdrant VectorStore` - Vector database integration
- `AzureChatOpenAI` - Wrapper cho GPT-4 chat
- `SystemMessage/HumanMessage` - Structured prompts

**Chức năng:** Orchestrate RAG pipeline với memory management

---

## ⚙️ Azure OpenAI Function Calling

**4 Functions:**

1. `get_film_details` - Chi tiết phim/show
2. `filter_by_genre` - Lọc theo genre + năm
3. `get_similar_titles` - Tìm phim tương tự
4. `get_trending_recommendations` - Trending content

**Cơ chế:** GPT-4 tự động detect và gọi function khi cần

---

## 📝 Response Template System

**7 Loại Templates:**

- `movie_recommendation` - Gợi ý phim
- `tv_show_recommendation` - Gợi ý series
- `similar_content` - Nội dung tương tự
- `genre_filter` - Lọc theo thể loại
- `detailed_info` - Thông tin chi tiết
- `trending` - Nội dung hot
- `general_chat` - Chat tự nhiên

**Tính năng:** Auto-detect type từ query + context, tạo structured prompts

---

## 🔍 Query Optimization

**GPT-4o-mini xử lý:**

- ✅ Verify & Correct: Sửa spelling/grammar
- ✅ Analyze & Match: Match với database fields
- ✅ Generate Optimized Summary: Tối ưu cho embedding
- ✅ Extract Filters: country, type, year, genre

**Normalize:** "phim mỹ" → "United States", "hành động" → "Action"

**Fallback:** Regex parsing nếu LLM fails

---

## 🔎 Hybrid Search Strategy

**Kết hợp 2 phương pháp:**

- **Semantic Search:** Vector similarity (cosine distance)
- **Exact Filters:** Qdrant FieldCondition (country, type, year)

**Retrieval:** Top 5 documents với relevance scores

**Output:** Structured context cho LLM generation

---

## 💬 Conversational Memory

**Tính năng:**

- Session-based (max 10 messages)
- Chat history inject vào prompts
- Context-aware responses
- Tích hợp với LangChain service

**Kết quả:** Trải nghiệm chat liên tục, hiểu ngữ cảnh

---

## 📊 Tổng kết

**3 Models chính:**

- GPT-4o-mini → Query optimization
- text-embedding-3-small → Embeddings
- GPT-4 → Generation + Function calling

**Core Technologies:**

- RAG Pipeline
- LangChain Framework
- Qdrant Vector Database
- Response Templates
- Function Calling

**Kết quả:** Hệ thống recommendation thông minh với semantic search, context-aware responses, và multi-model architecture
