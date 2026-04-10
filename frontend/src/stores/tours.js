import { ref } from 'vue'
import { defineStore } from 'pinia'
import {
  getTours, getTour, createTour, updateTour, deleteTour,
  createScenario, updateScenario, deleteScenario,
  createCostItem, updateCostItem, deleteCostItem,
  createExchangeRate, updateExchangeRate, deleteExchangeRate,
} from '@/api/tours'

export const useToursStore = defineStore('tours', () => {
  const tours = ref([])
  const currentTour = ref(null)
  const loading = ref(false)

  async function fetchTours(params) {
    loading.value = true
    try {
      const { data } = await getTours(params)
      tours.value = data
    } finally {
      loading.value = false
    }
  }

  async function fetchTour(id) {
    loading.value = true
    try {
      const { data } = await getTour(id)
      currentTour.value = data
    } finally {
      loading.value = false
    }
  }

  async function addTour(data) {
    const response = await createTour(data)
    return response.data
  }

  async function editTour(id, data) {
    const response = await updateTour(id, data)
    currentTour.value = { ...currentTour.value, ...response.data }
    return response.data
  }

  async function removeTour(id) {
    await deleteTour(id)
    tours.value = tours.value.filter((t) => t.id !== id)
    currentTour.value = null
  }

  // Scenarios
  async function addScenario(tourId, data) {
    const response = await createScenario(tourId, data)
    await fetchTour(tourId)
    return response.data
  }

  async function editScenario(tourId, scenarioId, data) {
    const response = await updateScenario(tourId, scenarioId, data)
    await fetchTour(tourId)
    return response.data
  }

  async function removeScenario(tourId, scenarioId) {
    await deleteScenario(tourId, scenarioId)
    await fetchTour(tourId)
  }

  async function markDesiredScenario(tourId, scenarioId) {
    await updateScenario(tourId, scenarioId, { is_desired: true })
    await fetchTour(tourId)
  }

  // Cost Items
  async function addCostItem(tourId, scenarioId, data) {
    const response = await createCostItem(tourId, scenarioId, data)
    await fetchTour(tourId)
    return response.data
  }

  async function editCostItem(tourId, scenarioId, itemId, data) {
    const response = await updateCostItem(tourId, scenarioId, itemId, data)
    await fetchTour(tourId)
    return response.data
  }

  async function removeCostItem(tourId, scenarioId, itemId) {
    await deleteCostItem(tourId, scenarioId, itemId)
    await fetchTour(tourId)
  }

  // Exchange Rates
  async function addExchangeRate(tourId, data) {
    const response = await createExchangeRate(tourId, data)
    await fetchTour(tourId)
    return response.data
  }

  async function editExchangeRate(tourId, rateId, data) {
    const response = await updateExchangeRate(tourId, rateId, data)
    await fetchTour(tourId)
    return response.data
  }

  async function removeExchangeRate(tourId, rateId) {
    await deleteExchangeRate(tourId, rateId)
    await fetchTour(tourId)
  }

  return {
    tours, currentTour, loading,
    fetchTours, fetchTour, addTour, editTour, removeTour,
    addScenario, editScenario, removeScenario, markDesiredScenario,
    addCostItem, editCostItem, removeCostItem,
    addExchangeRate, editExchangeRate, removeExchangeRate,
  }
})
