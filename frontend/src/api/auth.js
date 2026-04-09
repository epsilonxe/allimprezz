import apiClient from './client'

export const loginUser = (email, password) =>
  apiClient.post('/accounts/auth/login/', { email, password })

export const refreshToken = (refresh) =>
  apiClient.post('/accounts/auth/refresh/', { refresh })

export const logoutUser = (refresh) =>
  apiClient.post('/accounts/auth/logout/', { refresh })

export const getProfile = () => apiClient.get('/accounts/profile/')

export const updateProfile = (data) => apiClient.patch('/accounts/profile/', data)

export const changePassword = (oldPassword, newPassword) =>
  apiClient.post('/accounts/profile/password/', {
    old_password: oldPassword,
    new_password: newPassword,
  })
