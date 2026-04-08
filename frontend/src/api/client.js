import axios from 'axios'

const apiClient = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
})

let isRefreshing = false
let failedQueue = []

const processQueue = (error, token = null) => {
  failedQueue.forEach(({ resolve, reject }) => {
    if (error) {
      reject(error)
    } else {
      resolve(token)
    }
  })
  failedQueue = []
}

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    const isAuthEndpoint =
      originalRequest.url?.includes('/auth/login') ||
      originalRequest.url?.includes('/auth/refresh')

    if (error.response?.status !== 401 || isAuthEndpoint || originalRequest._retry) {
      return Promise.reject(error)
    }

    if (isRefreshing) {
      return new Promise((resolve, reject) => {
        failedQueue.push({ resolve, reject })
      }).then((token) => {
        originalRequest.headers.Authorization = `Bearer ${token}`
        return apiClient(originalRequest)
      })
    }

    originalRequest._retry = true
    isRefreshing = true

    const refreshTokenValue = localStorage.getItem('refresh_token')
    if (!refreshTokenValue) {
      isRefreshing = false
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      window.location.href = '/login'
      return Promise.reject(error)
    }

    try {
      const { data } = await axios.post('/api/accounts/auth/refresh/', {
        refresh: refreshTokenValue,
      })
      localStorage.setItem('access_token', data.access)
      if (data.refresh) {
        localStorage.setItem('refresh_token', data.refresh)
      }
      processQueue(null, data.access)
      originalRequest.headers.Authorization = `Bearer ${data.access}`
      return apiClient(originalRequest)
    } catch (refreshError) {
      processQueue(refreshError, null)
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      window.location.href = '/login'
      return Promise.reject(refreshError)
    } finally {
      isRefreshing = false
    }
  },
)

export default apiClient
