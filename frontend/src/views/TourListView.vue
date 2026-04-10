<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useToursStore } from '@/stores/tours'

const router = useRouter()
const toursStore = useToursStore()

const search = ref('')
const statusFilter = ref('')
const sortKey = ref('created_at')
const sortAsc = ref(false)

const columns = [
  { key: 'name', label: 'Tour Name' },
  { key: 'destination', label: 'Destination' },
  { key: 'duration_days', label: 'Days' },
  { key: 'start_date', label: 'Start Date' },
  { key: 'status', label: 'Status' },
  { key: 'scenario_count', label: 'Scenarios' },
  { key: 'created_at', label: 'Created' },
]

const statusOptions = [
  { value: '', label: 'All Statuses' },
  { value: 'draft', label: 'Draft' },
  { value: 'active', label: 'Active' },
  { value: 'completed', label: 'Completed' },
  { value: 'cancelled', label: 'Cancelled' },
]

const statusColors = {
  draft: 'bg-gray-100 text-gray-600',
  active: 'bg-green-100 text-green-700',
  completed: 'bg-blue-100 text-blue-700',
  cancelled: 'bg-red-100 text-red-600',
}

const filteredTours = computed(() => {
  const q = search.value.toLowerCase().trim()
  let result = toursStore.tours
  if (statusFilter.value) {
    result = result.filter((t) => t.status === statusFilter.value)
  }
  if (q) {
    result = result.filter((t) =>
      t.name.toLowerCase().includes(q) ||
      t.destination.toLowerCase().includes(q)
    )
  }
  const key = sortKey.value
  const dir = sortAsc.value ? 1 : -1
  return [...result].sort((a, b) => {
    const va = (a[key] ?? '').toString().toLowerCase()
    const vb = (b[key] ?? '').toString().toLowerCase()
    if (va < vb) return -1 * dir
    if (va > vb) return 1 * dir
    return 0
  })
})

function toggleSort(key) {
  if (sortKey.value === key) {
    sortAsc.value = !sortAsc.value
  } else {
    sortKey.value = key
    sortAsc.value = true
  }
}

function sortIndicator(key) {
  if (sortKey.value !== key) return ''
  return sortAsc.value ? ' ▲' : ' ▼'
}

function formatDate(dateStr) {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleDateString()
}

onMounted(() => {
  toursStore.fetchTours()
})
</script>

<template>
  <main class="p-8 max-w-5xl mx-auto">
    <div class="flex items-center justify-between mb-6">
      <div>
        <h1 class="text-xl font-bold mb-1">Tour Management</h1>
        <p class="text-gray-500 text-sm m-0">
          <router-link to="/dashboard" class="text-blue-500 hover:text-blue-600 no-underline">Dashboard</router-link>
          <span class="mx-2 text-gray-300">/</span>
          All tours
        </p>
      </div>
      <button
        class="px-4 py-2 bg-blue-500 text-white border-none rounded cursor-pointer text-sm hover:bg-blue-600"
        @click="router.push({ name: 'tour-create' })"
      >
        Create Tour
      </button>
    </div>

    <p v-if="toursStore.loading">Loading tours...</p>

    <template v-else>
      <div class="flex gap-3 mb-4">
        <input
          v-model="search"
          type="text"
          placeholder="Search by name or destination..."
          class="flex-1 px-3 py-2 border border-gray-300 rounded text-sm box-border focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-blue-400"
        />
        <select
          v-model="statusFilter"
          class="px-3 py-2 border border-gray-300 rounded text-sm bg-white focus:outline-none focus:ring-2 focus:ring-blue-400"
        >
          <option v-for="opt in statusOptions" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
        </select>
      </div>

      <table class="w-full border-collapse bg-white rounded-lg overflow-hidden shadow">
        <thead>
          <tr>
            <th
              v-for="col in columns"
              :key="col.key"
              class="px-4 py-3 text-left text-sm font-semibold bg-gray-50 border-b border-gray-200 cursor-pointer select-none whitespace-nowrap hover:bg-gray-100"
              @click="toggleSort(col.key)"
            >
              {{ col.label }}{{ sortIndicator(col.key) }}
            </th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="tour in filteredTours"
            :key="tour.id"
            class="cursor-pointer hover:bg-gray-50 border-b border-gray-100"
            @click="router.push({ name: 'tour-detail', params: { id: tour.id } })"
          >
            <td class="px-4 py-3 text-sm font-medium">{{ tour.name }}</td>
            <td class="px-4 py-3 text-sm">{{ tour.destination }}</td>
            <td class="px-4 py-3 text-sm text-center">{{ tour.duration_days }}</td>
            <td class="px-4 py-3 text-sm">{{ formatDate(tour.start_date) }}</td>
            <td class="px-4 py-3 text-sm">
              <span :class="['inline-block px-2 py-0.5 rounded-full text-xs capitalize', statusColors[tour.status]]">
                {{ tour.status }}
              </span>
            </td>
            <td class="px-4 py-3 text-sm text-center">{{ tour.scenario_count }}</td>
            <td class="px-4 py-3 text-sm">{{ formatDate(tour.created_at) }}</td>
          </tr>
          <tr v-if="filteredTours.length === 0">
            <td colspan="7" class="text-center text-gray-400 py-8">No tours found.</td>
          </tr>
        </tbody>
      </table>
    </template>
  </main>
</template>
