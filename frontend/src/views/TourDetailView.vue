<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useToursStore } from '@/stores/tours'

const route = useRoute()
const router = useRouter()
const toursStore = useToursStore()

const tourId = Number(route.params.id)
const activeTab = ref('info')
const message = ref('')
const messageType = ref('success')
const showDeleteConfirm = ref(false)

// Tour edit form
const editForm = ref({})
const editMode = ref(false)
const saving = ref(false)
const dateAutoComputing = ref(false)

// Scenario form
const showScenarioForm = ref(false)
const editingScenario = ref(null)
const scenarioForm = ref({ label: '', num_pax: '', num_tour_leaders: 0, markup_percent: 5, notes: '' })

// Active scenario tab
const activeScenarioId = ref(null)

// Cost items search & sort
const itemSearch = ref('')
const itemSortKey = ref('item_number')
const itemSortDir = ref('asc')

function toggleItemSort(key) {
  if (itemSortKey.value === key) {
    itemSortDir.value = itemSortDir.value === 'asc' ? 'desc' : 'asc'
  } else {
    itemSortKey.value = key
    itemSortDir.value = 'asc'
  }
}

// Note float window
const noteItem = ref(null)
const noteText = ref('')

// Exchange rate form
const showRateForm = ref(false)
const rateForm = ref({ currency_code: '', rate: '' })
const ratesPanelOpen = ref(false)

const categoryOptions = [
  { value: 'insurance', label: 'Insurance' },
  { value: 'visa', label: 'Visa' },
  { value: 'miscellaneous', label: 'Miscellaneous' },
  { value: 'management_fee', label: 'Management Fee' },
  { value: 'op_ticket', label: 'OP Ticket' },
  { value: 'op_expense', label: 'OP Expense' },
  { value: 'accommodation', label: 'Accommodation' },
  { value: 'activity', label: 'Activity' },
  { value: 'transportation', label: 'Transportation' },
  { value: 'other', label: 'Other' },
]

const statusColors = {
  draft: 'bg-gray-100 text-gray-600',
  active: 'bg-green-100 text-green-700',
  completed: 'bg-blue-100 text-blue-700',
  cancelled: 'bg-red-100 text-red-600',
}

const tour = computed(() => toursStore.currentTour)
const feasibility = computed(() => tour.value?.feasibility)

const currencyOptions = computed(() => {
  const opts = ['THB']
  if (tour.value?.exchange_rates) {
    for (const er of tour.value.exchange_rates) {
      if (!opts.includes(er.currency_code)) opts.push(er.currency_code)
    }
  }
  return opts
})

const activeScenario = computed(() => {
  if (!tour.value?.cost_scenarios?.length) return null
  return tour.value.cost_scenarios.find(s => s.id === activeScenarioId.value) || tour.value.cost_scenarios[0]
})

const desiredScenario = computed(() => {
  return tour.value?.cost_scenarios?.find(s => s.is_desired) || null
})

const feasibilityScenarios = computed(() => {
  if (!feasibility.value?.scenarios) return []
  const src = tour.value?.cost_scenarios || []
  return feasibility.value.scenarios.map((fs, i) => ({
    ...fs,
    id: src[i]?.id,
    is_desired: !!src[i]?.is_desired,
  }))
})

const displayedItems = computed(() => {
  const items = activeScenario.value?.items || []
  const q = itemSearch.value.trim().toLowerCase()
  const filtered = q
    ? items.filter(it =>
        (it.name || '').toLowerCase().includes(q) ||
        (it.pay_to || '').toLowerCase().includes(q) ||
        (it.category || '').toLowerCase().includes(q) ||
        (it.notes || '').toLowerCase().includes(q),
      )
    : items.slice()

  const key = itemSortKey.value
  const dir = itemSortDir.value === 'asc' ? 1 : -1
  const numericKeys = ['item_number', 'unit_cost', 'total_cost']
  filtered.sort((a, b) => {
    let av = a[key]
    let bv = b[key]
    if (numericKeys.includes(key)) {
      av = parseFloat(av) || 0
      bv = parseFloat(bv) || 0
      return (av - bv) * dir
    }
    av = (av ?? '').toString().toLowerCase()
    bv = (bv ?? '').toString().toLowerCase()
    if (av < bv) return -1 * dir
    if (av > bv) return 1 * dir
    return 0
  })
  return filtered
})

function showMsg(text, type = 'success') {
  message.value = text
  messageType.value = type
  setTimeout(() => { message.value = '' }, 3000)
}

function formatNumber(val) {
  const num = parseFloat(val)
  if (isNaN(num)) return val
  return num.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

function formatDate(dateStr) {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleDateString()
}

// --- Date sync watchers ---
watch(() => editForm.value.start_date, (val) => {
  if (dateAutoComputing.value) return
  if (val && editForm.value.duration_days) {
    dateAutoComputing.value = true
    const start = new Date(val)
    start.setDate(start.getDate() + parseInt(editForm.value.duration_days) - 1)
    editForm.value.end_date = start.toISOString().slice(0, 10)
    dateAutoComputing.value = false
  }
})

watch(() => editForm.value.end_date, (val) => {
  if (dateAutoComputing.value) return
  if (val && editForm.value.start_date) {
    dateAutoComputing.value = true
    const start = new Date(editForm.value.start_date)
    const end = new Date(val)
    editForm.value.duration_days = Math.round((end - start) / 86400000) + 1
    dateAutoComputing.value = false
  }
})

watch(() => editForm.value.duration_days, (val) => {
  if (dateAutoComputing.value) return
  if (val && editForm.value.start_date) {
    dateAutoComputing.value = true
    const start = new Date(editForm.value.start_date)
    start.setDate(start.getDate() + parseInt(val) - 1)
    editForm.value.end_date = start.toISOString().slice(0, 10)
    dateAutoComputing.value = false
  }
})

// --- Tour info ---
function startEdit() {
  editForm.value = {
    name: tour.value.name,
    description: tour.value.description,
    destination: tour.value.destination,
    duration_days: tour.value.duration_days,
    start_date: tour.value.start_date || '',
    end_date: tour.value.end_date || '',
    status: tour.value.status,
  }
  editMode.value = true
}

async function saveEdit() {
  saving.value = true
  try {
    const payload = { ...editForm.value }
    if (!payload.start_date) payload.start_date = null
    if (!payload.end_date) payload.end_date = null
    await toursStore.editTour(tourId, payload)
    await toursStore.fetchTour(tourId)
    editMode.value = false
    showMsg('Tour updated.')
  } catch (err) {
    showMsg(err.response?.data?.detail || 'Failed to update tour.', 'error')
  } finally {
    saving.value = false
  }
}

async function handleDelete() {
  try {
    await toursStore.removeTour(tourId)
    router.push({ name: 'tour-list' })
  } catch {
    showMsg('Failed to delete tour.', 'error')
  }
  showDeleteConfirm.value = false
}

// --- Scenarios ---
function openScenarioForm(scenario = null) {
  if (scenario) {
    editingScenario.value = scenario.id
    scenarioForm.value = {
      label: scenario.label,
      num_pax: scenario.num_pax,
      num_tour_leaders: scenario.num_tour_leaders,
      markup_percent: scenario.markup_percent,
      selling_price_per_pax: scenario.selling_price_per_pax,
      notes: scenario.notes,
    }
  } else {
    editingScenario.value = null
    const isFirst = !tour.value?.cost_scenarios?.length
    scenarioForm.value = { label: isFirst ? 'Default' : '', num_pax: '', num_tour_leaders: 0, markup_percent: 5, notes: '' }
  }
  showScenarioForm.value = true
}

async function saveScenario() {
  try {
    const payload = { ...scenarioForm.value }
    payload.num_pax = parseInt(payload.num_pax)
    payload.markup_percent = parseFloat(payload.markup_percent) || 5
    if (editingScenario.value) {
      payload.selling_price_per_pax = parseFloat(payload.selling_price_per_pax) || 0
      await toursStore.editScenario(tourId, editingScenario.value, payload)
    } else {
      await toursStore.addScenario(tourId, payload)
    }
    showScenarioForm.value = false
    showMsg(editingScenario.value ? 'Scenario updated.' : 'Scenario added.')
  } catch (err) {
    showMsg(err.response?.data?.detail || 'Failed to save scenario.', 'error')
  }
}

async function removeScenario(scenarioId) {
  if (!confirm('Delete this scenario and all its cost items?')) return
  try {
    await toursStore.removeScenario(tourId, scenarioId)
    if (activeScenarioId.value === scenarioId) {
      activeScenarioId.value = tour.value?.cost_scenarios?.[0]?.id || null
    }
    showMsg('Scenario deleted.')
  } catch {
    showMsg('Failed to delete scenario.', 'error')
  }
}

async function markDesired(scenarioId) {
  try {
    await toursStore.markDesiredScenario(tourId, scenarioId)
    showMsg('Marked as desired scenario.')
  } catch (err) {
    const detail = err?.response?.data ? JSON.stringify(err.response.data) : err?.message || 'unknown error'
    showMsg(`Failed to mark desired scenario: ${detail}`, 'error')
  }
}

// --- Inline item editing ---
async function updateItemField(scenarioId, itemId, field, value) {
  try {
    const payload = {}
    if (field === 'unit_cost') {
      payload[field] = parseFloat(value) || 0
    } else if (field === 'item_number') {
      payload[field] = parseInt(value) || 0
    } else {
      payload[field] = value
    }
    await toursStore.editCostItem(tourId, scenarioId, itemId, payload)
  } catch (err) {
    showMsg('Failed to update item.', 'error')
  }
}

async function addNewItem(scenarioId) {
  try {
    const maxNum = activeScenario.value?.items?.length
      ? Math.max(...activeScenario.value.items.map(i => i.item_number)) + 1
      : 1
    await toursStore.addCostItem(tourId, scenarioId, {
      item_number: maxNum,
      name: 'New item',
      category: 'other',
      unit_cost: 0,
      currency: 'THB',
    })
  } catch (err) {
    showMsg('Failed to add item.', 'error')
  }
}

async function removeItem(scenarioId, item) {
  const msg = item.is_synced
    ? 'This item is synced. Deleting it will also delete it from all other scenarios. Continue?'
    : 'Delete this cost item?'
  if (!confirm(msg)) return
  try {
    await toursStore.removeCostItem(tourId, scenarioId, item.id)
  } catch {
    showMsg('Failed to delete item.', 'error')
  }
}

// --- Notes float window ---
function openNoteWindow(item) {
  noteItem.value = item
  noteText.value = item.notes || ''
}

async function saveNote() {
  if (!noteItem.value) return
  try {
    await toursStore.editCostItem(tourId, activeScenario.value.id, noteItem.value.id, { notes: noteText.value })
    noteItem.value = null
  } catch {
    showMsg('Failed to save note.', 'error')
  }
}

// --- Selling price inline edit ---
async function updateSellingPrice(scenarioId, value) {
  try {
    const price = parseFloat(value) || 0
    await toursStore.editScenario(tourId, scenarioId, { selling_price_per_pax: price })
    showMsg(price > 0 ? 'Selling price override set.' : 'Selling price reset to markup.')
  } catch {
    showMsg('Failed to update selling price.', 'error')
  }
}

// --- Exchange rates ---
const editingRateId = ref(null)

function openRateForm() {
  editingRateId.value = null
  rateForm.value = { currency_code: '', rate: '' }
  showRateForm.value = true
}

function editRate(er) {
  editingRateId.value = er.id
  rateForm.value = { currency_code: er.currency_code, rate: er.rate }
  showRateForm.value = true
}

async function saveRate() {
  try {
    const payload = { ...rateForm.value }
    payload.rate = parseFloat(payload.rate) || 0
    if (editingRateId.value) {
      await toursStore.editExchangeRate(tourId, editingRateId.value, payload)
      showMsg('Exchange rate updated.')
    } else {
      await toursStore.addExchangeRate(tourId, payload)
      showMsg('Exchange rate added.')
    }
    showRateForm.value = false
    editingRateId.value = null
  } catch (err) {
    showMsg(err.response?.data?.detail || 'Failed to save rate.', 'error')
  }
}

async function removeRate(rateId) {
  if (!confirm('Delete this exchange rate?')) return
  try {
    await toursStore.removeExchangeRate(tourId, rateId)
    showMsg('Rate deleted.')
  } catch {
    showMsg('Failed to delete rate.', 'error')
  }
}

// --- Init ---
watch(tour, (val) => {
  if (val?.cost_scenarios?.length && !activeScenarioId.value) {
    activeScenarioId.value = val.cost_scenarios[0].id
  }
})

onMounted(() => {
  toursStore.fetchTour(tourId)
})
</script>

<template>
  <main class="p-8 max-w-5xl mx-auto">
    <p v-if="toursStore.loading && !tour">Loading...</p>

    <template v-if="tour">
      <!-- Header -->
      <div class="flex items-center justify-between mb-6">
        <div>
          <h1 class="text-xl font-bold mb-1">{{ tour.name }}</h1>
          <p class="text-gray-500 text-sm m-0">
            <router-link to="/dashboard" class="text-blue-500 hover:text-blue-600 no-underline">Dashboard</router-link>
            <span class="mx-2 text-gray-300">/</span>
            <router-link to="/tours" class="text-blue-500 hover:text-blue-600 no-underline">Tours</router-link>
            <span class="mx-2 text-gray-300">/</span>
            {{ tour.name }}
          </p>
        </div>
        <span :class="['inline-block px-3 py-1 rounded-full text-sm capitalize', statusColors[tour.status]]">
          {{ tour.status }}
        </span>
      </div>

      <!-- Message -->
      <div v-if="message" :class="['mb-4 px-4 py-2 rounded text-sm', messageType === 'error' ? 'bg-red-50 text-red-700' : 'bg-green-50 text-green-700']">
        {{ message }}
      </div>

      <!-- Tabs -->
      <div class="flex gap-1 mb-6 border-b border-gray-200">
        <button
          v-for="tab in [{ key: 'info', label: 'Tour Info' }, { key: 'cost', label: 'Cost Feasibility' }, { key: 'summary', label: 'Summary' }]"
          :key="tab.key"
          :class="['px-4 py-2 text-sm border-none cursor-pointer bg-transparent -mb-px', activeTab === tab.key ? 'border-b-2 border-blue-500 text-blue-600 font-medium' : 'text-gray-500 hover:text-gray-700']"
          @click="activeTab = tab.key"
        >
          {{ tab.label }}
        </button>
      </div>

      <!-- ==================== Tab: Tour Info ==================== -->
      <div v-if="activeTab === 'info'">
        <div v-if="!editMode" class="bg-white p-6 rounded-lg shadow">
          <div class="grid grid-cols-2 gap-4 mb-4">
            <div><span class="text-gray-500 text-sm">Destination</span><p class="font-medium m-0 mt-1">{{ tour.destination }}</p></div>
            <div><span class="text-gray-500 text-sm">Duration</span><p class="font-medium m-0 mt-1">{{ tour.duration_days }} days</p></div>
            <div><span class="text-gray-500 text-sm">Start Date</span><p class="font-medium m-0 mt-1">{{ formatDate(tour.start_date) }}</p></div>
            <div><span class="text-gray-500 text-sm">End Date</span><p class="font-medium m-0 mt-1">{{ formatDate(tour.end_date) }}</p></div>
            <div><span class="text-gray-500 text-sm">Created By</span><p class="font-medium m-0 mt-1">{{ tour.created_by_name || '-' }}</p></div>
            <div><span class="text-gray-500 text-sm">Created At</span><p class="font-medium m-0 mt-1">{{ formatDate(tour.created_at) }}</p></div>
          </div>
          <div v-if="tour.description" class="mb-4">
            <span class="text-gray-500 text-sm">Description</span>
            <p class="m-0 mt-1">{{ tour.description }}</p>
          </div>

          <div class="mb-4 border-t border-gray-100 pt-4">
            <div class="flex items-center gap-2 mb-2">
              <span class="text-amber-500">★</span>
              <h3 class="text-sm font-semibold m-0">Desired Scenario</h3>
            </div>
            <p v-if="!desiredScenario" class="text-gray-400 text-sm m-0">No desired scenario selected yet.</p>
            <div v-else class="bg-amber-50/40 border border-amber-100 rounded p-4">
              <div class="flex items-center justify-between mb-3">
                <span class="font-semibold">{{ desiredScenario.label || `${desiredScenario.num_pax} Pax` }}</span>
                <span :class="['inline-block px-2 py-0.5 rounded-full text-xs', desiredScenario.summary?.is_feasible ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-600']">
                  {{ desiredScenario.summary?.is_feasible ? 'Feasible' : 'Not feasible' }}
                </span>
              </div>
              <div class="grid grid-cols-2 md:grid-cols-5 gap-3 text-sm">
                <div>
                  <span class="text-gray-500 text-xs block">Pax</span>
                  <span class="font-medium">{{ desiredScenario.num_pax }}</span>
                </div>
                <div>
                  <span class="text-gray-500 text-xs block">Cost / Pax</span>
                  <span class="font-medium">{{ formatNumber(desiredScenario.summary?.cost_per_pax) }}</span>
                </div>
                <div>
                  <span class="text-gray-500 text-xs block">Selling / Pax</span>
                  <span class="font-medium">{{ formatNumber(desiredScenario.summary?.effective_selling_price_per_pax) }}</span>
                </div>
                <div>
                  <span class="text-gray-500 text-xs block">Profit</span>
                  <span :class="['font-medium', parseFloat(desiredScenario.summary?.total_profit) >= 0 ? 'text-green-600' : 'text-red-600']">
                    {{ formatNumber(desiredScenario.summary?.total_profit) }}
                  </span>
                </div>
                <div>
                  <span class="text-gray-500 text-xs block">Margin</span>
                  <span :class="['font-medium', parseFloat(desiredScenario.summary?.margin_percent) >= 0 ? 'text-green-600' : 'text-red-600']">
                    {{ desiredScenario.summary?.margin_percent }}%
                  </span>
                </div>
              </div>
            </div>
          </div>

          <div class="flex gap-3">
            <button class="px-4 py-2 bg-blue-500 text-white border-none rounded cursor-pointer text-sm hover:bg-blue-600" @click="startEdit">Edit</button>
            <button class="px-4 py-2 bg-red-500 text-white border-none rounded cursor-pointer text-sm hover:bg-red-600" @click="showDeleteConfirm = true">Delete</button>
          </div>
        </div>

        <!-- Edit Form -->
        <form v-else class="bg-white p-6 rounded-lg shadow space-y-4" @submit.prevent="saveEdit">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Tour Name</label>
              <input v-model="editForm.name" type="text" required class="w-full px-3 py-2 border border-gray-300 rounded text-sm box-border focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-blue-400" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Destination</label>
              <input v-model="editForm.destination" type="text" required class="w-full px-3 py-2 border border-gray-300 rounded text-sm box-border focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-blue-400" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Duration (days)</label>
              <input v-model="editForm.duration_days" type="number" min="1" required class="w-full px-3 py-2 border border-gray-300 rounded text-sm box-border focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-blue-400" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Status</label>
              <select v-model="editForm.status" class="w-full px-3 py-2 border border-gray-300 rounded text-sm bg-white focus:outline-none focus:ring-2 focus:ring-blue-400">
                <option value="draft">Draft</option>
                <option value="active">Active</option>
                <option value="completed">Completed</option>
                <option value="cancelled">Cancelled</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Start Date</label>
              <input v-model="editForm.start_date" type="date" class="w-full px-3 py-2 border border-gray-300 rounded text-sm box-border focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-blue-400" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">End Date</label>
              <input v-model="editForm.end_date" type="date" class="w-full px-3 py-2 border border-gray-300 rounded text-sm box-border focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-blue-400" />
            </div>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Description</label>
            <textarea v-model="editForm.description" rows="3" class="w-full px-3 py-2 border border-gray-300 rounded text-sm box-border focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-blue-400"></textarea>
          </div>
          <div class="flex gap-3">
            <button type="submit" :disabled="saving" class="px-4 py-2 bg-blue-500 text-white border-none rounded cursor-pointer text-sm hover:bg-blue-600 disabled:opacity-50">Save</button>
            <button type="button" class="px-4 py-2 bg-gray-100 text-gray-700 border border-gray-300 rounded cursor-pointer text-sm hover:bg-gray-200" @click="editMode = false">Cancel</button>
          </div>
        </form>

        <!-- Delete Confirmation Modal -->
        <div v-if="showDeleteConfirm" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div class="bg-white p-6 rounded-lg shadow-lg max-w-sm w-full mx-4">
            <h3 class="text-lg font-semibold mb-2">Delete Tour</h3>
            <p class="text-gray-600 text-sm mb-4">Are you sure you want to delete "{{ tour.name }}"? This will also delete all cost scenarios and items.</p>
            <div class="flex gap-3 justify-end">
              <button class="px-4 py-2 bg-gray-100 text-gray-700 border border-gray-300 rounded cursor-pointer text-sm hover:bg-gray-200" @click="showDeleteConfirm = false">Cancel</button>
              <button class="px-4 py-2 bg-red-500 text-white border-none rounded cursor-pointer text-sm hover:bg-red-600" @click="handleDelete">Delete</button>
            </div>
          </div>
        </div>
      </div>

      <!-- ==================== Tab: Cost Feasibility ==================== -->
      <div v-if="activeTab === 'cost'">
        <!-- Scenario Tabs + Content -->
        <div class="bg-white rounded-lg shadow border border-gray-200">
          <div class="flex items-center border-b border-gray-200">
            <button
              v-for="scenario in tour.cost_scenarios"
              :key="scenario.id"
              :class="['px-5 py-2.5 text-sm border-none cursor-pointer transition-all relative', activeScenarioId === scenario.id ? 'text-blue-700 font-semibold bg-white' : 'text-gray-500 bg-gray-50 hover:bg-gray-100 hover:text-gray-700']"
              :style="activeScenarioId === scenario.id ? 'box-shadow: inset 0 -2px 0 #3b82f6; margin-bottom: -1px; padding-bottom: calc(0.625rem + 1px);' : ''"
              @click="activeScenarioId = scenario.id"
            >
              {{ scenario.label || `${scenario.num_pax} Pax` }}<span v-if="scenario.is_desired" class="ml-1 text-amber-500">★</span>
            </button>
            <button
              class="px-4 py-2.5 text-sm border-none cursor-pointer bg-gray-50 text-gray-400 hover:text-blue-500 hover:bg-gray-100"
              @click="openScenarioForm()"
            >
              + Add
            </button>
          </div>

        <div v-if="activeScenario">
          <!-- Scenario Header -->
          <div class="flex items-center justify-between p-4 border-b border-gray-100">
            <div>
              <p class="text-gray-500 text-xs m-0">
                {{ activeScenario.num_pax }} pax / {{ activeScenario.num_tour_leaders }} TL / Markup {{ activeScenario.markup_percent }}%
                <span v-if="activeScenario.notes" class="ml-2 text-gray-400">{{ activeScenario.notes }}</span>
              </p>
            </div>
            <div class="flex gap-2">
              <button class="px-3 py-1 bg-gray-100 text-gray-600 border-none rounded cursor-pointer text-xs hover:bg-gray-200" @click="openScenarioForm(activeScenario)">Edit</button>
              <button class="px-3 py-1 bg-red-50 text-red-600 border-none rounded cursor-pointer text-xs hover:bg-red-100" @click="removeScenario(activeScenario.id)">Delete</button>
            </div>
          </div>

          <!-- Summary bar -->
          <div v-if="activeScenario.summary?.error" class="p-3 bg-amber-50 text-amber-700 text-sm border-b border-amber-100">
            {{ activeScenario.summary.error }}
          </div>
          <div v-else-if="activeScenario.summary" class="grid grid-cols-5 gap-2 p-4 bg-gray-50 text-center text-xs border-b border-gray-100">
            <div>
              <span class="text-gray-400 block">Cost/Pax</span>
              <span class="font-semibold">{{ formatNumber(activeScenario.summary.cost_per_pax) }}</span>
            </div>
            <div>
              <span class="text-gray-400 block">Selling/Pax</span>
              <input
                :value="activeScenario.selling_price_per_pax > 0 ? activeScenario.selling_price_per_pax : activeScenario.summary.computed_selling_price_per_pax"
                type="number" step="0.01" min="0"
                class="w-24 mx-auto text-center font-semibold text-sm bg-transparent border border-transparent rounded px-1 py-0.5 focus:border-blue-400 focus:bg-white focus:outline-none"
                title="Edit selling price per pax (set 0 to use markup)"
                @change="updateSellingPrice(activeScenario.id, $event.target.value)"
              />
              <span v-if="activeScenario.selling_price_per_pax > 0" class="text-orange-500 text-[10px] block">(override)</span>
            </div>
            <div>
              <span class="text-gray-400 block">Total Cost</span>
              <span class="font-semibold">{{ formatNumber(activeScenario.summary.total_cost) }}</span>
            </div>
            <div>
              <span class="text-gray-400 block">Total Revenue</span>
              <span class="font-semibold">{{ formatNumber(activeScenario.summary.total_revenue) }}</span>
            </div>
            <div>
              <span class="text-gray-400 block">Profit</span>
              <span :class="['font-semibold', parseFloat(activeScenario.summary.total_profit) >= 0 ? 'text-green-600' : 'text-red-600']">
                {{ formatNumber(activeScenario.summary.total_profit) }}
                <span class="text-gray-400 font-normal">({{ activeScenario.summary.margin_percent }}%)</span>
              </span>
            </div>
          </div>

          <!-- Cost Items Table (inline editing) -->
          <div class="p-4">
            <div class="flex items-center justify-between mb-2 gap-2">
              <span class="text-sm font-medium text-gray-600 whitespace-nowrap">Cost Items</span>
              <input
                v-model="itemSearch"
                type="text"
                placeholder="Search items..."
                class="flex-1 max-w-xs px-2 py-1 border border-gray-200 rounded text-xs focus:outline-none focus:ring-1 focus:ring-blue-400"
              />
              <button class="px-3 py-1 bg-blue-50 text-blue-600 border-none rounded cursor-pointer text-xs hover:bg-blue-100 whitespace-nowrap" @click="addNewItem(activeScenario.id)">+ Add Item</button>
            </div>
            <table v-if="activeScenario.items?.length" class="w-full border-collapse text-sm">
              <thead>
                <tr class="text-left text-xs text-gray-400 border-b border-gray-100 select-none">
                  <th class="py-2 pr-1 text-center w-8" title="Sync to other scenarios">
                    <svg xmlns="http://www.w3.org/2000/svg" class="inline w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" /></svg>
                  </th>
                  <th class="py-2 pr-1 w-10 cursor-pointer hover:text-gray-600" @click="toggleItemSort('item_number')">
                    # <span v-if="itemSortKey === 'item_number'">{{ itemSortDir === 'asc' ? '\u25b2' : '\u25bc' }}</span>
                  </th>
                  <th class="py-2 pr-1 cursor-pointer hover:text-gray-600" @click="toggleItemSort('name')">
                    Item <span v-if="itemSortKey === 'name'">{{ itemSortDir === 'asc' ? '\u25b2' : '\u25bc' }}</span>
                  </th>
                  <th class="py-2 pr-1 w-28 cursor-pointer hover:text-gray-600" @click="toggleItemSort('category')">
                    Category <span v-if="itemSortKey === 'category'">{{ itemSortDir === 'asc' ? '\u25b2' : '\u25bc' }}</span>
                  </th>
                  <th class="py-2 pr-1 cursor-pointer hover:text-gray-600" @click="toggleItemSort('pay_to')">
                    Pay To <span v-if="itemSortKey === 'pay_to'">{{ itemSortDir === 'asc' ? '\u25b2' : '\u25bc' }}</span>
                  </th>
                  <th class="py-2 pr-1 w-16 cursor-pointer hover:text-gray-600" @click="toggleItemSort('currency')">
                    Curr <span v-if="itemSortKey === 'currency'">{{ itemSortDir === 'asc' ? '\u25b2' : '\u25bc' }}</span>
                  </th>
                  <th class="py-2 pr-1 text-right w-24 cursor-pointer hover:text-gray-600" @click="toggleItemSort('unit_cost')">
                    Unit Cost <span v-if="itemSortKey === 'unit_cost'">{{ itemSortDir === 'asc' ? '\u25b2' : '\u25bc' }}</span>
                  </th>
                  <th class="py-2 pr-1 text-right w-24 cursor-pointer hover:text-gray-600" @click="toggleItemSort('total_cost')">
                    Total <span v-if="itemSortKey === 'total_cost'">{{ itemSortDir === 'asc' ? '\u25b2' : '\u25bc' }}</span>
                  </th>
                  <th class="py-2 w-14"></th>
                </tr>
              </thead>
              <tbody>
                <tr v-if="!displayedItems.length">
                  <td colspan="9" class="py-3 text-center text-gray-400 text-xs">No items match your search.</td>
                </tr>
                <tr v-for="item in displayedItems" :key="item.id" class="border-b border-gray-50 hover:bg-gray-50 group">
                  <td class="py-1 pr-1 text-center">
                    <input
                      type="checkbox"
                      :checked="item.is_synced"
                      class="cursor-pointer accent-blue-500"
                      title="Sync this item to other scenarios"
                      @change="updateItemField(activeScenario.id, item.id, 'is_synced', $event.target.checked)"
                    />
                  </td>
                  <td class="py-1 pr-1">
                    <input
                      :value="item.item_number"
                      type="number" min="0"
                      class="w-full px-1 py-1 border border-transparent rounded text-sm text-center bg-transparent focus:border-gray-300 focus:bg-white focus:outline-none"
                      @change="updateItemField(activeScenario.id, item.id, 'item_number', $event.target.value)"
                    />
                  </td>
                  <td class="py-1 pr-1">
                    <input
                      :value="item.name"
                      type="text"
                      class="w-full px-1 py-1 border border-transparent rounded text-sm bg-transparent focus:border-gray-300 focus:bg-white focus:outline-none"
                      @change="updateItemField(activeScenario.id, item.id, 'name', $event.target.value)"
                    />
                  </td>
                  <td class="py-1 pr-1">
                    <select
                      :value="item.category"
                      class="w-full px-1 py-1 border border-transparent rounded text-xs bg-transparent focus:border-gray-300 focus:bg-white focus:outline-none"
                      @change="updateItemField(activeScenario.id, item.id, 'category', $event.target.value)"
                    >
                      <option v-for="cat in categoryOptions" :key="cat.value" :value="cat.value">{{ cat.label }}</option>
                    </select>
                  </td>
                  <td class="py-1 pr-1">
                    <input
                      :value="item.pay_to"
                      type="text"
                      class="w-full px-1 py-1 border border-transparent rounded text-sm bg-transparent focus:border-gray-300 focus:bg-white focus:outline-none"
                      @change="updateItemField(activeScenario.id, item.id, 'pay_to', $event.target.value)"
                    />
                  </td>
                  <td class="py-1 pr-1">
                    <select
                      :value="item.currency"
                      class="w-full px-1 py-1 border border-transparent rounded text-xs bg-transparent focus:border-gray-300 focus:bg-white focus:outline-none"
                      @change="updateItemField(activeScenario.id, item.id, 'currency', $event.target.value)"
                    >
                      <option v-for="c in currencyOptions" :key="c" :value="c">{{ c }}</option>
                    </select>
                  </td>
                  <td class="py-1 pr-1">
                    <input
                      :value="item.unit_cost"
                      type="number" step="0.01" min="0"
                      class="w-full px-1 py-1 border border-transparent rounded text-sm text-right bg-transparent focus:border-gray-300 focus:bg-white focus:outline-none"
                      @change="updateItemField(activeScenario.id, item.id, 'unit_cost', $event.target.value)"
                    />
                  </td>
                  <td class="py-1 pr-1 text-right font-medium text-sm">
                    <template v-if="item.currency === 'THB' || !item.total_cost_thb">
                      {{ formatNumber(item.total_cost) }}
                    </template>
                    <template v-else>
                      <span class="text-gray-400 text-xs block">{{ item.currency }} {{ formatNumber(item.total_cost) }}</span>
                      <span>{{ formatNumber(item.total_cost_thb) }}</span>
                    </template>
                  </td>
                  <td class="py-1 text-right whitespace-nowrap">
                    <button
                      :class="['bg-transparent border-none cursor-pointer mr-1 p-0.5', item.notes ? 'text-blue-500' : 'text-gray-300 group-hover:text-blue-400']"
                      title="Add/edit note"
                      @click="openNoteWindow(item)"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" /></svg>
                    </button>
                    <button
                      class="bg-transparent border-none cursor-pointer p-0.5 text-gray-300 group-hover:text-red-500"
                      title="Delete item"
                      @click="removeItem(activeScenario.id, item)"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
            <p v-else class="text-gray-400 text-sm m-0">No cost items yet. Click "+ Add Item" to start.</p>
          </div>
        </div>

        <div v-else class="p-8 text-center text-gray-400">
          No cost scenarios yet. Click "+ Add" to create one.
        </div>
        </div>

        <!-- Scenario Form Modal -->
        <div v-if="showScenarioForm" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div class="bg-white p-6 rounded-lg shadow-lg max-w-md w-full mx-4">
            <h3 class="text-lg font-semibold mb-4">{{ editingScenario ? 'Edit' : 'Add' }} Scenario</h3>
            <div class="space-y-3">
              <div>
                <label class="block text-sm text-gray-700 mb-1">Label</label>
                <input v-model="scenarioForm.label" type="text" placeholder="e.g. 6 Pax + 2 TL" class="w-full px-3 py-2 border border-gray-300 rounded text-sm box-border focus:outline-none focus:ring-1 focus:ring-blue-400" />
              </div>
              <div class="grid grid-cols-3 gap-3">
                <div>
                  <label class="block text-sm text-gray-700 mb-1">Passengers</label>
                  <input v-model="scenarioForm.num_pax" type="number" min="1" required class="w-full px-3 py-2 border border-gray-300 rounded text-sm box-border focus:outline-none focus:ring-1 focus:ring-blue-400" />
                </div>
                <div>
                  <label class="block text-sm text-gray-700 mb-1">Tour Leaders</label>
                  <input v-model="scenarioForm.num_tour_leaders" type="number" min="0" class="w-full px-3 py-2 border border-gray-300 rounded text-sm box-border focus:outline-none focus:ring-1 focus:ring-blue-400" />
                </div>
                <div>
                  <label class="block text-sm text-gray-700 mb-1">Markup %</label>
                  <input v-model="scenarioForm.markup_percent" type="number" step="0.01" min="0" class="w-full px-3 py-2 border border-gray-300 rounded text-sm box-border focus:outline-none focus:ring-1 focus:ring-blue-400" />
                </div>
              </div>
              <!-- Selling price override (edit mode only) -->
              <div v-if="editingScenario">
                <label class="block text-sm text-gray-700 mb-1">Selling Price / Pax Override <span class="text-gray-400 font-normal">(0 = use markup)</span></label>
                <input v-model="scenarioForm.selling_price_per_pax" type="number" step="0.01" min="0" class="w-full px-3 py-2 border border-gray-300 rounded text-sm box-border focus:outline-none focus:ring-1 focus:ring-blue-400" />
              </div>
              <div>
                <label class="block text-sm text-gray-700 mb-1">Notes</label>
                <textarea v-model="scenarioForm.notes" rows="2" class="w-full px-3 py-2 border border-gray-300 rounded text-sm box-border focus:outline-none focus:ring-1 focus:ring-blue-400"></textarea>
              </div>
              <!-- Copy from default (create mode only) -->
            </div>
            <div class="flex gap-3 mt-4 justify-end">
              <button class="px-4 py-2 bg-gray-100 text-gray-700 border border-gray-300 rounded cursor-pointer text-sm hover:bg-gray-200" @click="showScenarioForm = false">Cancel</button>
              <button class="px-4 py-2 bg-blue-500 text-white border-none rounded cursor-pointer text-sm hover:bg-blue-600" @click="saveScenario">Save</button>
            </div>
          </div>
        </div>

        <!-- Floating Note Window -->
        <div v-if="noteItem" class="fixed bottom-20 right-6 z-50 bg-white rounded-lg shadow-xl border border-gray-200 w-80">
          <div class="flex items-center justify-between px-4 py-3 border-b border-gray-100">
            <h4 class="text-sm font-semibold text-gray-700 m-0">Note: {{ noteItem.name }}</h4>
            <button class="text-gray-400 hover:text-gray-600 bg-transparent border-none cursor-pointer text-lg leading-none" @click="noteItem = null">&times;</button>
          </div>
          <div class="p-4">
            <textarea
              v-model="noteText"
              rows="4"
              placeholder="Add a note for this item..."
              class="w-full px-3 py-2 border border-gray-300 rounded text-sm box-border focus:outline-none focus:ring-1 focus:ring-blue-400 resize-y"
            ></textarea>
            <div class="flex gap-2 mt-2 justify-end">
              <button class="px-3 py-1 bg-gray-200 text-gray-600 border-none rounded cursor-pointer text-sm hover:bg-gray-300" @click="noteItem = null">Cancel</button>
              <button class="px-3 py-1 bg-blue-500 text-white border-none rounded cursor-pointer text-sm hover:bg-blue-600" @click="saveNote">Save</button>
            </div>
          </div>
        </div>
      </div>

      <!-- ==================== Tab: Summary ==================== -->
      <div v-if="activeTab === 'summary'">
        <div v-if="!feasibility" class="bg-white p-8 rounded-lg shadow text-center text-gray-400">
          Add cost scenarios to see the feasibility summary.
        </div>

        <div v-else-if="feasibility.error" class="bg-white p-8 rounded-lg shadow">
          <div class="p-4 bg-amber-50 text-amber-700 rounded text-sm">
            {{ feasibility.error }}
          </div>
        </div>

        <template v-else>
          <div class="bg-white p-6 rounded-lg shadow mb-6">
            <div class="flex items-center justify-between mb-4">
              <h2 class="text-lg font-semibold m-0">Feasibility Comparison</h2>
              <span :class="['inline-block px-3 py-1 rounded-full text-sm', feasibility.all_feasible ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-600']">
                {{ feasibility.all_feasible ? 'All Feasible' : 'Some Not Feasible' }}
              </span>
            </div>

            <div class="overflow-x-auto">
              <table class="w-full border-collapse text-sm">
                <thead>
                  <tr class="text-left text-xs text-gray-400 border-b border-gray-200">
                    <th class="py-3 pr-4">Metric</th>
                    <th v-for="s in feasibilityScenarios" :key="s.id" class="py-3 pr-4 text-right align-bottom">
                      <div class="flex flex-col items-end gap-1">
                        <span>{{ s.label || `${s.num_pax} Pax` }}</span>
                        <span v-if="s.is_desired" class="inline-block px-2 py-0.5 rounded-full bg-amber-100 text-amber-700 text-[10px] font-semibold">★ Desired</span>
                        <button v-else class="inline-block px-2 py-0.5 rounded-full bg-gray-50 text-gray-500 border border-gray-200 text-[10px] cursor-pointer hover:bg-amber-50 hover:text-amber-700 hover:border-amber-200" @click="markDesired(s.id)">☆ Mark as desired</button>
                      </div>
                    </th>
                  </tr>
                </thead>
                <tbody>
                  <tr class="border-b border-gray-50">
                    <td class="py-2 pr-4 text-gray-600">Tour Leaders</td>
                    <td v-for="s in feasibilityScenarios" :key="s.id" class="py-2 pr-4 text-right">{{ s.num_tour_leaders }}</td>
                  </tr>
                  <tr class="border-b border-gray-50">
                    <td class="py-2 pr-4 text-gray-600">Markup %</td>
                    <td v-for="s in feasibilityScenarios" :key="s.id" class="py-2 pr-4 text-right">{{ s.markup_percent }}%</td>
                  </tr>
                  <tr class="border-b border-gray-50">
                    <td class="py-2 pr-4 text-gray-600">Cost / Pax</td>
                    <td v-for="s in feasibilityScenarios" :key="s.id" class="py-2 pr-4 text-right">{{ formatNumber(s.cost_per_pax) }}</td>
                  </tr>
                  <tr class="border-b border-gray-50">
                    <td class="py-2 pr-4 text-gray-600">Selling Price / Pax</td>
                    <td v-for="s in feasibilityScenarios" :key="s.id" class="py-2 pr-4 text-right">
                      {{ formatNumber(s.effective_selling_price_per_pax) }}
                      <span v-if="s.selling_price_override" class="text-orange-500 text-xs block">(override)</span>
                    </td>
                  </tr>
                  <tr class="border-b border-gray-50">
                    <td class="py-2 pr-4 text-gray-600">Total Cost</td>
                    <td v-for="s in feasibilityScenarios" :key="s.id" class="py-2 pr-4 text-right font-medium">{{ formatNumber(s.total_cost) }}</td>
                  </tr>
                  <tr class="border-b border-gray-50">
                    <td class="py-2 pr-4 text-gray-600">Total Revenue</td>
                    <td v-for="s in feasibilityScenarios" :key="s.id" class="py-2 pr-4 text-right font-medium">{{ formatNumber(s.total_revenue) }}</td>
                  </tr>
                  <tr class="border-b border-gray-100 bg-gray-50">
                    <td class="py-2 pr-4 font-semibold">Profit</td>
                    <td v-for="s in feasibilityScenarios" :key="s.id" :class="['py-2 pr-4 text-right font-semibold', parseFloat(s.total_profit) >= 0 ? 'text-green-600' : 'text-red-600']">
                      {{ formatNumber(s.total_profit) }}
                    </td>
                  </tr>
                  <tr class="border-b border-gray-100">
                    <td class="py-2 pr-4 text-gray-600">Profit / Pax</td>
                    <td v-for="s in feasibilityScenarios" :key="s.id" :class="['py-2 pr-4 text-right', parseFloat(s.profit_per_pax) >= 0 ? 'text-green-600' : 'text-red-600']">
                      {{ formatNumber(s.profit_per_pax) }}
                    </td>
                  </tr>
                  <tr>
                    <td class="py-2 pr-4 text-gray-600">Margin</td>
                    <td v-for="s in feasibilityScenarios" :key="s.id" :class="['py-2 pr-4 text-right', parseFloat(s.margin_percent) >= 0 ? 'text-green-600' : 'text-red-600']">
                      {{ s.margin_percent }}%
                    </td>
                  </tr>
                  <tr class="border-t border-gray-200">
                    <td class="py-2 pr-4 text-gray-600">Feasible</td>
                    <td v-for="s in feasibilityScenarios" :key="s.id" class="py-2 pr-4 text-right">
                      <span :class="['inline-block px-2 py-0.5 rounded-full text-xs', s.is_feasible ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-600']">
                        {{ s.is_feasible ? 'Yes' : 'No' }}
                      </span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- Cost Breakdown by Category -->
          <div class="bg-white p-6 rounded-lg shadow">
            <h3 class="text-base font-semibold mb-4">Cost Breakdown by Category</h3>
            <div class="overflow-x-auto">
              <table class="w-full border-collapse text-sm">
                <thead>
                  <tr class="text-left text-xs text-gray-400 border-b border-gray-200">
                    <th class="py-3 pr-4">Category</th>
                    <th v-for="s in feasibilityScenarios" :key="s.id" class="py-3 pr-4 text-right">{{ s.label || `${s.num_pax} Pax` }}</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="cat in categoryOptions" :key="cat.value" class="border-b border-gray-50">
                    <td class="py-2 pr-4 text-gray-600 capitalize">{{ cat.label }}</td>
                    <td v-for="s in feasibilityScenarios" :key="s.id" class="py-2 pr-4 text-right">
                      <template v-if="s.cost_breakdown[cat.value]">
                        {{ formatNumber(s.cost_breakdown[cat.value]) }}
                        <span class="text-gray-400 text-xs block">({{ (parseFloat(s.cost_breakdown[cat.value]) / parseFloat(s.total_cost) * 100).toFixed(2) }}%)</span>
                      </template>
                      <template v-else>-</template>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </template>
      </div>
      <!-- Floating Exchange Rate Panel -->
      <div v-if="activeTab === 'cost' || activeTab === 'summary'" class="fixed bottom-6 right-6 z-40">
        <!-- Minimized: floating button -->
        <button
          v-if="!ratesPanelOpen"
          class="flex items-center gap-2 px-4 py-2.5 bg-white text-gray-700 border border-gray-200 rounded-full shadow-lg cursor-pointer text-sm hover:shadow-xl transition-shadow"
          @click="ratesPanelOpen = true"
        >
          <span class="text-base">&#x2693;</span>
          Exchange Rates
          <span v-if="tour.exchange_rates?.length" class="bg-blue-100 text-blue-700 text-xs px-1.5 py-0.5 rounded-full">{{ tour.exchange_rates.length }}</span>
        </button>

        <!-- Expanded: floating panel -->
        <div v-else class="bg-white rounded-lg shadow-xl border border-gray-200 w-80">
          <div class="flex items-center justify-between px-4 py-3 border-b border-gray-100">
            <h3 class="text-sm font-semibold text-gray-700 m-0">Exchange Rates</h3>
            <div class="flex items-center gap-2">
              <button class="px-2 py-1 bg-gray-100 text-gray-700 border border-gray-300 rounded cursor-pointer text-xs hover:bg-gray-200" @click="openRateForm">+ Add</button>
              <button class="text-gray-400 hover:text-gray-600 bg-transparent border-none cursor-pointer text-lg leading-none" @click="ratesPanelOpen = false; showRateForm = false">&minus;</button>
            </div>
          </div>
          <div class="px-4 py-3 max-h-60 overflow-y-auto">
            <div v-if="tour.exchange_rates?.length" class="space-y-2">
              <div v-for="er in tour.exchange_rates" :key="er.id" class="flex items-center justify-between py-1.5 px-2 bg-gray-50 rounded text-sm">
                <span>1 {{ er.currency_code }} = {{ formatNumber(er.rate) }} THB</span>
                <span class="flex gap-1.5">
                  <button class="text-blue-400 hover:text-blue-600 bg-transparent border-none cursor-pointer text-xs" @click="editRate(er)">edit</button>
                  <button class="text-red-400 hover:text-red-600 bg-transparent border-none cursor-pointer text-xs" @click="removeRate(er.id)">x</button>
                </span>
              </div>
            </div>
            <p v-else class="text-gray-400 text-sm m-0">No exchange rates set.</p>
          </div>
          <div v-if="showRateForm" class="px-4 py-3 border-t border-gray-100">
            <div class="flex gap-2 items-end">
              <div class="flex-1">
                <label class="block text-xs text-gray-500 mb-1">Currency</label>
                <input v-model="rateForm.currency_code" type="text" placeholder="USD" :disabled="!!editingRateId" :class="['w-full px-2 py-1 border border-gray-300 rounded text-sm focus:outline-none focus:ring-1 focus:ring-blue-400', editingRateId ? 'bg-gray-100 text-gray-500' : '']" />
              </div>
              <div class="flex-1">
                <label class="block text-xs text-gray-500 mb-1">Rate (THB)</label>
                <input v-model="rateForm.rate" type="number" step="0.01" placeholder="35.00" class="w-full px-2 py-1 border border-gray-300 rounded text-sm focus:outline-none focus:ring-1 focus:ring-blue-400" />
              </div>
            </div>
            <div class="flex gap-2 mt-2">
              <button class="flex-1 px-3 py-1 bg-blue-500 text-white border-none rounded cursor-pointer text-sm hover:bg-blue-600" @click="saveRate">{{ editingRateId ? 'Update' : 'Save' }}</button>
              <button class="px-3 py-1 bg-gray-200 text-gray-600 border-none rounded cursor-pointer text-sm hover:bg-gray-300" @click="showRateForm = false">Cancel</button>
            </div>
          </div>
        </div>
      </div>

    </template>
  </main>
</template>
