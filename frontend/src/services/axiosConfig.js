import axios from 'axios'

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000'

// Create axios instance
const axiosInstance = axios.create({
  baseURL: API_BASE_URL,
  // timeout: 120000, // 120 seconds (increased for TTS + OpenAI)
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor
axiosInstance.interceptors.request.use(
  (config) => {
    console.log(`[API Request] ${config.method.toUpperCase()} ${config.url}`)
    return config
  },
  (error) => {
    console.error('[API Request Error]', error)
    return Promise.reject(error)
  }
)

// Response interceptor
axiosInstance.interceptors.response.use(
  (response) => {
    console.log(
      `[API Response] ${response.config.method.toUpperCase()} ${response.config.url} - Status: ${response.status}`
    )
    return response
  },
  (error) => {
    if (error.response) {
      console.error(`[API Error] ${error.response.status}:`, error.response.data)
    } else if (error.request) {
      console.error('[API Error] No response received:', error.request)
    } else {
      console.error('[API Error] Request setup error:', error.message)
    }
    return Promise.reject(error)
  }
)

export default axiosInstance
