<script setup>
import { ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useToursStore } from '@/stores/tours'

const router = useRouter()
const toursStore = useToursStore()

const form = ref({
  name: '',
  description: '',
  destination: '',
  duration_days: '',
  start_date: '',
  end_date: '',
  status: 'draft',
})
const errors = ref({})
const submitting = ref(false)

// Date sync: auto-compute the third field when two are set
const dateAutoComputing = ref(false)

function addDays(dateStr, days) {
  const d = new Date(dateStr)
  d.setDate(d.getDate() + days)
  return d.toISOString().slice(0, 10)
}
function diffDays(startStr, endStr) {
  const s = new Date(startStr)
  const e = new Date(endStr)
  return Math.round((e - s) / 86400000) + 1
}

watch(() => form.value.start_date, (val) => {
  if (dateAutoComputing.value) return
  dateAutoComputing.value = true
  if (val && form.value.end_date) {
    form.value.duration_days = diffDays(val, form.value.end_date)
  } else if (val && form.value.duration_days) {
    form.value.end_date = addDays(val, parseInt(form.value.duration_days) - 1)
  }
  dateAutoComputing.value = false
})

watch(() => form.value.end_date, (val) => {
  if (dateAutoComputing.value) return
  dateAutoComputing.value = true
  if (val && form.value.start_date) {
    form.value.duration_days = diffDays(form.value.start_date, val)
  } else if (val && form.value.duration_days) {
    form.value.start_date = addDays(val, -(parseInt(form.value.duration_days) - 1))
  }
  dateAutoComputing.value = false
})

watch(() => form.value.duration_days, (val) => {
  if (dateAutoComputing.value) return
  dateAutoComputing.value = true
  const days = parseInt(val)
  if (days > 0 && form.value.start_date) {
    form.value.end_date = addDays(form.value.start_date, days - 1)
  } else if (days > 0 && form.value.end_date) {
    form.value.start_date = addDays(form.value.end_date, -(days - 1))
  }
  dateAutoComputing.value = false
})

async function handleSubmit() {
  errors.value = {}
  submitting.value = true
  try {
    const payload = { ...form.value }
    if (!payload.start_date) delete payload.start_date
    if (!payload.end_date) delete payload.end_date
    payload.duration_days = parseInt(payload.duration_days) || 1
    const tour = await toursStore.addTour(payload)
    router.push({ name: 'tour-detail', params: { id: tour.id } })
  } catch (err) {
    if (err.response?.data) {
      errors.value = err.response.data
    }
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <main class="p-8 max-w-lg mx-auto">
    <h1 class="text-xl font-bold mb-1">Create Tour</h1>
    <p class="text-gray-500 text-sm mb-6">
      <router-link to="/dashboard" class="text-blue-500 hover:text-blue-600 no-underline">Dashboard</router-link>
      <span class="mx-2 text-gray-300">/</span>
      <router-link to="/tours" class="text-blue-500 hover:text-blue-600 no-underline">Tours</router-link>
      <span class="mx-2 text-gray-300">/</span>
      Create
    </p>

    <form class="bg-white p-6 rounded-lg shadow space-y-4" @submit.prevent="handleSubmit">
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Tour Name</label>
        <input v-model="form.name" type="text" required class="w-full px-3 py-2 border border-gray-300 rounded text-sm box-border focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-blue-400" />
        <p v-if="errors.name" class="text-red-500 text-xs mt-1">{{ errors.name[0] }}</p>
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Destination</label>
        <input v-model="form.destination" type="text" required class="w-full px-3 py-2 border border-gray-300 rounded text-sm box-border focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-blue-400" />
        <p v-if="errors.destination" class="text-red-500 text-xs mt-1">{{ errors.destination[0] }}</p>
      </div>

      <div class="grid grid-cols-3 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Duration (days)</label>
          <input v-model="form.duration_days" type="number" min="1" required class="w-full px-3 py-2 border border-gray-300 rounded text-sm box-border focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-blue-400" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Start Date</label>
          <input v-model="form.start_date" type="date" class="w-full px-3 py-2 border border-gray-300 rounded text-sm box-border focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-blue-400" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">End Date</label>
          <input v-model="form.end_date" type="date" class="w-full px-3 py-2 border border-gray-300 rounded text-sm box-border focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-blue-400" />
        </div>
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Status</label>
        <select v-model="form.status" class="w-full px-3 py-2 border border-gray-300 rounded text-sm bg-white focus:outline-none focus:ring-2 focus:ring-blue-400">
          <option value="draft">Draft</option>
          <option value="active">Active</option>
        </select>
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Description</label>
        <textarea v-model="form.description" rows="3" class="w-full px-3 py-2 border border-gray-300 rounded text-sm box-border focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-blue-400"></textarea>
      </div>

      <div class="flex gap-3">
        <button type="submit" :disabled="submitting" class="px-4 py-2 bg-blue-500 text-white border-none rounded cursor-pointer text-sm hover:bg-blue-600 disabled:opacity-50">
          {{ submitting ? 'Creating...' : 'Create Tour' }}
        </button>
        <button type="button" class="px-4 py-2 bg-gray-100 text-gray-700 border border-gray-300 rounded cursor-pointer text-sm hover:bg-gray-200" @click="router.back()">
          Cancel
        </button>
      </div>
    </form>
  </main>
</template>
