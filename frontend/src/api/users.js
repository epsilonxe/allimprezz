import apiClient from './client'

export const getUsers = () => apiClient.get('/accounts/users/')

export const getUser = (id) => apiClient.get(`/accounts/users/${id}/`)

export const createUser = (data) => apiClient.post('/accounts/users/create/', data)

export const updateUser = (id, data) => apiClient.patch(`/accounts/users/${id}/`, data)

export const deleteUser = (id) => apiClient.delete(`/accounts/users/${id}/`)
