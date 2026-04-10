import apiClient from './client'

// Tours
export const getTours = (params) => apiClient.get('/tours/', { params })
export const getTour = (id) => apiClient.get(`/tours/${id}/`)
export const createTour = (data) => apiClient.post('/tours/create/', data)
export const updateTour = (id, data) => apiClient.patch(`/tours/${id}/`, data)
export const deleteTour = (id) => apiClient.delete(`/tours/${id}/`)

// Cost Scenarios
export const getScenarios = (tourId) => apiClient.get(`/tours/${tourId}/scenarios/`)
export const createScenario = (tourId, data) => apiClient.post(`/tours/${tourId}/scenarios/`, data)
export const getScenario = (tourId, id) => apiClient.get(`/tours/${tourId}/scenarios/${id}/`)
export const updateScenario = (tourId, id, data) => apiClient.patch(`/tours/${tourId}/scenarios/${id}/`, data)
export const deleteScenario = (tourId, id) => apiClient.delete(`/tours/${tourId}/scenarios/${id}/`)

// Cost Items
export const getCostItems = (tourId, scenarioId) => apiClient.get(`/tours/${tourId}/scenarios/${scenarioId}/items/`)
export const createCostItem = (tourId, scenarioId, data) => apiClient.post(`/tours/${tourId}/scenarios/${scenarioId}/items/`, data)
export const updateCostItem = (tourId, scenarioId, id, data) => apiClient.patch(`/tours/${tourId}/scenarios/${scenarioId}/items/${id}/`, data)
export const deleteCostItem = (tourId, scenarioId, id) => apiClient.delete(`/tours/${tourId}/scenarios/${scenarioId}/items/${id}/`)

// Exchange Rates
export const getExchangeRates = (tourId) => apiClient.get(`/tours/${tourId}/exchange-rates/`)
export const createExchangeRate = (tourId, data) => apiClient.post(`/tours/${tourId}/exchange-rates/`, data)
export const updateExchangeRate = (tourId, id, data) => apiClient.patch(`/tours/${tourId}/exchange-rates/${id}/`, data)
export const deleteExchangeRate = (tourId, id) => apiClient.delete(`/tours/${tourId}/exchange-rates/${id}/`)
