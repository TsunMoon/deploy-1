🎯 Chức năng chính:
1. Hệ thống gợi ý phim/TV show thông minh
Tích hợp với QdrantDB (vector database) để tìm kiếm semantic
Sử dụng Azure OpenAI cho embeddings và chat
Xây dựng các câu trả lời có cấu trúc và ngữ cảnh
2. Quản lý hội thoại (Conversational Memory)
Lưu trữ lịch sử chat để hiểu ngữ cảnh
Trả lời có nhận thức về các câu hỏi trước đó
Cung cấp trải nghiệm chat liên tục
3. Azure OpenAI Function Calling
Định nghĩa 2 functions:
get_film_details: Lấy chi tiết về phim/show cụ thể
filter_by_genre: Lọc theo thể loại và năm phát hành
4. Hệ thống Response Templates
7 loại template có cấu trúc:
movie_recommendation - Gợi ý phim
tv_show_recommendation - Gợi ý series
similar_content - Tìm nội dung tương tự
genre_filter - Lọc theo thể loại
detailed_info - Thông tin chi tiết
trending - Nội dung đang hot
general_chat - Chat tự nhiên