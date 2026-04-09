<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUsersStore } from '@/stores/users'

const router = useRouter()
const usersStore = useUsersStore()

const search = ref('')
const sortKey = ref('date_joined')
const sortAsc = ref(false)

const columns = [
  { key: 'email', label: 'Email' },
  { key: 'first_name', label: 'First Name' },
  { key: 'last_name', label: 'Last Name' },
  { key: 'role', label: 'Role' },
  { key: 'is_active', label: 'Status' },
  { key: 'date_joined', label: 'Joined' },
]

function getUserValue(user, key) {
  if (key === 'is_active') return user.is_active ? 'active' : 'inactive'
  if (key === 'date_joined') return user.date_joined
  return (user[key] ?? '').toString().toLowerCase()
}

const filteredUsers = computed(() => {
  const q = search.value.toLowerCase().trim()
  let result = usersStore.users
  if (q) {
    result = result.filter((u) => {
      const fullName = `${u.first_name} ${u.last_name}`.toLowerCase()
      return (
        u.email.toLowerCase().includes(q) ||
        fullName.includes(q) ||
        u.role.toLowerCase().includes(q)
      )
    })
  }
  const key = sortKey.value
  const dir = sortAsc.value ? 1 : -1
  return [...result].sort((a, b) => {
    const va = getUserValue(a, key)
    const vb = getUserValue(b, key)
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
  return new Date(dateStr).toLocaleDateString()
}

onMounted(() => {
  usersStore.fetchUsers()
})
</script>

<template>
  <main class="p-8 max-w-4xl mx-auto">
    <div class="flex items-center justify-between mb-6">
      <div>
        <h1 class="text-xl font-bold mb-1">Manage Users</h1>
        <p class="text-gray-500 text-sm m-0">
          <router-link to="/dashboard" class="text-blue-500 hover:text-blue-600 no-underline">Dashboard</router-link>
          <span class="mx-2 text-gray-300">/</span>
          All users
        </p>
      </div>
      <button
        class="px-4 py-2 bg-blue-500 text-white border-none rounded cursor-pointer text-sm hover:bg-blue-600"
        @click="router.push({ name: 'user-create' })"
      >
        Create User
      </button>
    </div>

    <p v-if="usersStore.loading">Loading users...</p>

    <template v-else>
      <div class="mb-4">
        <input
          v-model="search"
          type="text"
          placeholder="Search by name, email, or role..."
          class="w-full px-3 py-2 border border-gray-300 rounded text-sm box-border focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-blue-400"
        />
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
            v-for="user in filteredUsers"
            :key="user.id"
            class="cursor-pointer hover:bg-gray-50 border-b border-gray-100"
            @click="router.push({ name: 'user-detail', params: { id: user.id } })"
          >
            <td class="px-4 py-3 text-sm">{{ user.email }}</td>
            <td class="px-4 py-3 text-sm">{{ user.first_name }}</td>
            <td class="px-4 py-3 text-sm">{{ user.last_name }}</td>
            <td class="px-4 py-3 text-sm">
              <span class="inline-block px-2 py-0.5 bg-blue-50 text-blue-600 rounded-full text-xs capitalize">
                {{ user.role }}
              </span>
            </td>
            <td class="px-4 py-3 text-sm">
              <span
                :class="[
                  'inline-block px-2 py-0.5 rounded-full text-xs',
                  user.is_active ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-600',
                ]"
              >
                {{ user.is_active ? 'Active' : 'Inactive' }}
              </span>
            </td>
            <td class="px-4 py-3 text-sm">{{ formatDate(user.date_joined) }}</td>
          </tr>
          <tr v-if="filteredUsers.length === 0">
            <td colspan="6" class="text-center text-gray-400 py-8">No users found.</td>
          </tr>
        </tbody>
      </table>
    </template>
  </main>
</template>
