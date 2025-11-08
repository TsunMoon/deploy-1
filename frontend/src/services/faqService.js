import axiosInstance from './axiosConfig'
import { authService } from './authService'

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000'

class FAQService {
  constructor() {
    this.chatHistory = []
    // Generate a unique session ID for this conversation
    this.sessionId = this.generateSessionId()
  }

  // Get user_id from localStorage (stored by authService)
  getUserId() {
    const userInfo = authService.getUserInfo()
    return userInfo?.id || null
  }

  generateSessionId() {
    return `session_${Date.now()}_${Math.random().toString(36).substring(2, 15)}`
  }

  // Reset session (create new conversation)
  resetSession() {
    this.sessionId = this.generateSessionId()
    this.chatHistory = []
  }

  async getAnswer(question) {
    try {
      // Get user_id from localStorage to enable personalized recommendations
      const userId = this.getUserId()

      console.log('Sending request with session_id:', this.sessionId)
      console.log('User ID from localStorage:', userId)

      const requestPayload = {
        query: question,
        chat_history: this.chatHistory,
        session_id: this.sessionId,
        use_functions: false,
        audio_only: false,
        use_template: true,
        response_type: null
      }

      // Include user_id if available (for personalized AI responses)
      if (userId) {
        requestPayload.user_id = userId
      }

      const response = await axiosInstance.post('/api/v2/recommendation', requestPayload)

      // Prepend backend URL to audio_url if it exists
      const audioUrl = response.data.audio_url ? `${API_BASE_URL}${response.data.audio_url}` : null

      // Update chat history for next request
      this.chatHistory = response.data.chat_history || []
      console.log('Updated chat_history length:', this.chatHistory.length)

      // Extract sources information
      const sources = response.data.sources || []
      const contextUsed = sources.map((source) => ({
        title: source.title,
        description: source.description,
        genre: source.genre,
        year: source.year,
        type: source.type,
        rating: source.rating
      }))

      return {
        answer: response.data.answer,
        audioUrl: audioUrl,
        relatedQuestions: this.generateRelatedQuestions(response.data),
        contextUsed: contextUsed,
        responseType: response.data.response_type || 'default',
        functionCalled: response.data.function_called || null,
        sources: sources
      }
    } catch (error) {
      console.error('Chill-Dev Service error:', error)
      throw error
    }
  }

  // Generate related questions based on response type
  generateRelatedQuestions(data) {
    const responseType = data.response_type || 'default'

    // If we have sources, create questions based on them
    if (data.sources && data.sources.length > 0) {
      const firstSource = data.sources[0]
      return [
        `Tell me more about ${firstSource.title}`,
        `Find similar titles to ${firstSource.title}`,
        `What else in ${firstSource.genre}?`
      ]
    }

    // Default questions based on response type
    const questionMap = {
      movie_recommendation: ['Recommend another movie', 'What are trending movies?', 'Show me action movies'],
      tv_show_recommendation: ['Recommend a TV series', 'What are trending shows?', 'Find a binge-worthy series'],
      similar_content: ['Find more similar titles', 'What else would I like?', 'Show me different genres'],
      trending: ['What else is trending?', 'Show me classics', 'Recommend hidden gems'],
      default: ['Recommend a thriller movie', 'What are trending shows?', 'Find movies like Inception']
    }

    return questionMap[responseType] || questionMap['default']
  }

  // Clear conversation history
  clearHistory() {
    this.chatHistory = []
    console.log('Conversation history cleared')
  }

  // Call backend to clear server-side memory
  async clearMemory() {
    try {
      const response = await axiosInstance.post('/api/v2/clear-memory', {
        session_id: this.sessionId // Gửi session_id để backend xóa đúng session
      })
      this.resetSession() // Tạo session mới cho frontend
      return response.data
    } catch (error) {
      console.error('Clear memory error:', error)
      throw error
    }
  }

  // Get film details (direct function call)
  async getFilmDetails(title) {
    try {
      const response = await axiosInstance.get(`/api/v2/film/${encodeURIComponent(title)}`)
      return response.data
    } catch (error) {
      console.error('Get film details error:', error)
      throw error
    }
  }

  // Filter by genre (direct function call)
  async filterByGenre(genres, minYear = null) {
    try {
      const response = await axiosInstance.post('/api/v2/filter-by-genre', {
        genres,
        min_year: minYear
      })
      return response.data
    } catch (error) {
      console.error('Filter by genre error:', error)
      throw error
    }
  }

  // Get similar titles (direct function call)
  async getSimilarTitles(title, numResults = 5) {
    try {
      const response = await axiosInstance.get(`/api/v2/similar/${encodeURIComponent(title)}`, {
        params: { num_results: numResults }
      })
      return response.data
    } catch (error) {
      console.error('Get similar titles error:', error)
      throw error
    }
  }

  // Get trending recommendations (direct function call)
  async getTrending(category = 'all') {
    try {
      const response = await axiosInstance.get(`/api/v2/trending/${category}`)
      return response.data
    } catch (error) {
      console.error('Get trending error:', error)
      throw error
    }
  }

  // Health check for v2 API
  async getHealth() {
    try {
      const response = await axiosInstance.get('/api/v2/health')
      return response.data
    } catch (error) {
      console.error('Health check error:', error)
      throw error
    }
  }

  // Get audio for text
  async getAudioForText(text) {
    try {
      // Get user_id from localStorage for personalized audio responses
      const userId = this.getUserId()

      const requestPayload = {
        query: text,
        chat_history: [],
        use_template: false,
        response_type: null
      }

      // Include user_id if available
      if (userId) {
        requestPayload.user_id = userId
      }

      const response = await axiosInstance.post('/api/v2/recommendation', requestPayload)

      // Prepend backend URL to audio_url if it exists
      const audioUrl = response.data.audio_url ? `${API_BASE_URL}${response.data.audio_url}` : null

      return {
        audioUrl
      }
    } catch (error) {
      console.error('Get audio error:', error)
      throw error
    }
  }

  // Get available response types
  async getResponseTypes() {
    try {
      const response = await axiosInstance.get('/api/v2/response-types')
      return response.data
    } catch (error) {
      console.error('Get response types error:', error)
      throw error
    }
  }

  // Get default recommendations (5 films) when no conversation exists
  async getDefaultRecommendations() {
    try {
      // Get user_id from localStorage for personalized recommendations
      const userId = this.getUserId()

      const requestPayload = {
        query:
          'recommend exactly 5 popular movies with details including title, year, country, genre, rating, summary, and why I will love each one',
        chat_history: [],
        session_id: this.sessionId,
        use_functions: false,
        audio_only: false,
        use_template: true,
        response_type: 'movie_recommendation'
      }

      // Include user_id if available (for personalized AI responses)
      if (userId) {
        requestPayload.user_id = userId
      }

      const response = await axiosInstance.post('/api/v2/recommendation', requestPayload)

      // Prepend backend URL to audio_url if it exists
      const audioUrl = response.data.audio_url ? `${API_BASE_URL}${response.data.audio_url}` : null

      // Extract sources information
      const sources = response.data.sources || []
      const contextUsed = sources.map((source) => ({
        title: source.title,
        description: source.description,
        genre: source.genre,
        year: source.year,
        type: source.type,
        rating: source.rating
      }))

      return {
        answer: response.data.answer,
        audioUrl: audioUrl,
        relatedQuestions: this.generateRelatedQuestions(response.data),
        contextUsed: contextUsed,
        responseType: response.data.response_type || 'movie_recommendation',
        functionCalled: response.data.function_called || null,
        sources: sources
      }
    } catch (error) {
      console.error('Get default recommendations error:', error)
      throw error
    }
  }
}

export const faqService = new FAQService()
