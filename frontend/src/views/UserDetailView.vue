<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUsersStore } from '@/stores/users'

const route = useRoute()
const router = useRouter()
const usersStore = useUsersStore()

const form = ref({ first_name: '', last_name: '', role: 'agent', is_active: true })
const error = ref('')
const success = ref('')
const saving = ref(false)
const showDeleteConfirm = ref(false)
const deleting = ref(false)

onMounted(async () => {
  await usersStore.fetchUser(route.params.id)
  if (usersStore.currentUser) {
    form.value = {
      first_name: usersStore.currentUser.first_name,
      last_name: usersStore.currentUser.last_name,
      role: usersStore.currentUser.role,
      is_active: usersStore.currentUser.is_active,
    }
  }
})

async function handleSave() {
  error.value = ''
  success.value = ''
  saving.value = true
  try {
    await usersStore.editUser(route.params.id, form.value)
    success.value = 'User updated successfully.'
  } catch (err) {
    const data = err.response?.data
    if (data) {
      const messages = Object.values(data).flat()
      error.value = messages.join(' ')
    } else {
      error.value = 'Failed to update user.'
    }
  } finally {
    saving.value = false
  }
}

async function handleDelete() {
  deleting.value = true
  error.value = ''
  try {
    await usersStore.removeUser(route.params.id)
    router.push({ name: 'user-list' })
  } catch (err) {
    const data = err.response?.data
    error.value = data?.detail || 'Failed to delete user.'
    showDeleteConfirm.value = false
  } finally {
    deleting.value = false
  }
}
</script>

<template>
  <main class="p-8 max-w-lg mx-auto">
    <div class="mb-6">
      <h1 class="text-xl font-bold mb-1">Manage Users</h1>
      <p class="text-gray-500 text-sm m-0">
        <router-link to="/dashboard" class="text-blue-500 hover:text-blue-600 no-underline">Dashboard</router-link>
        <span class="mx-2 text-gray-300">/</span>
        <router-link to="/admin/users" class="text-blue-500 hover:text-blue-600 no-underline">All users</router-link>
        <span class="mx-2 text-gray-300">/</span>
        User Detail
      </p>
    </div>

    <p v-if="usersStore.loading">Loading...</p>

    <div v-else-if="usersStore.currentUser" class="bg-white p-8 rounded-lg shadow">
      <p class="text-base text-gray-500 m-0 mb-6 pb-4 border-b border-gray-200">
        {{ usersStore.currentUser.email }}
      </p>

      <form @submit.prevent="handleSave">
        <div class="flex gap-4">
          <div class="flex-1 mb-4">
            <label for="first_name" class="block mb-1 font-medium text-sm">First Name</label>
            <input
              id="first_name"
              v-model="form.first_name"
              type="text"
              class="w-full px-3 py-2 border border-gray-300 rounded text-base box-border focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-blue-400"
            />
          </div>
          <div class="flex-1 mb-4">
            <label for="last_name" class="block mb-1 font-medium text-sm">Last Name</label>
            <input
              id="last_name"
              v-model="form.last_name"
              type="text"
              class="w-full px-3 py-2 border border-gray-300 rounded text-base box-border focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-blue-400"
            />
          </div>
        </div>

        <div class="mb-4">
          <label for="role" class="block mb-1 font-medium text-sm">Role</label>
          <select
            id="role"
            v-model="form.role"
            class="w-full px-3 py-2 border border-gray-300 rounded text-base box-border focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-blue-400"
          >
            <option value="admin">Admin</option>
            <option value="staff">Staff</option>
            <option value="agent">Agent</option>
          </select>
        </div>

        <div class="mb-4">
          <label class="flex items-center gap-2 font-medium text-sm cursor-pointer">
            <input type="checkbox" v-model="form.is_active" class="w-auto" />
            Active
          </label>
        </div>

        <p v-if="error" class="text-red-600 text-sm my-2">{{ error }}</p>
        <p v-if="success" class="text-green-600 text-sm my-2">{{ success }}</p>

        <button
          type="submit"
          :disabled="saving"
          class="w-full py-2.5 bg-blue-500 text-white rounded text-base cursor-pointer mt-2 hover:bg-blue-600 disabled:opacity-60 disabled:cursor-not-allowed"
        >
          {{ saving ? 'Saving...' : 'Save Changes' }}
        </button>
      </form>

      <div class="mt-8 pt-6 border-t border-red-100">
        <h3 class="m-0 mb-3 text-sm text-red-600">Danger Zone</h3>
        <div v-if="!showDeleteConfirm">
          <button
            class="px-4 py-2 bg-red-600 text-white border-none rounded cursor-pointer text-sm hover:bg-red-800"
            @click="showDeleteConfirm = true"
          >
            Delete User
          </button>
        </div>
        <div v-else>
          <p class="text-red-600 text-sm m-0 mb-3">Are you sure? This action cannot be undone.</p>
          <div class="flex gap-2">
            <button
              :disabled="deleting"
              class="px-4 py-2 bg-red-600 text-white border-none rounded cursor-pointer text-sm hover:bg-red-800 disabled:opacity-60 disabled:cursor-not-allowed"
              @click="handleDelete"
            >
              {{ deleting ? 'Deleting...' : 'Yes, Delete' }}
            </button>
            <button
              class="px-4 py-2 bg-transparent border border-gray-300 rounded cursor-pointer text-sm hover:bg-gray-100"
              @click="showDeleteConfirm = false"
            >
              Cancel
            </button>
          </div>
        </div>
      </div>
    </div>
  </main>
</template>
