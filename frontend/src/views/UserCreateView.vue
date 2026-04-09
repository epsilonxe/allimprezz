<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUsersStore } from '@/stores/users'

const router = useRouter()
const usersStore = useUsersStore()

const form = ref({
  email: '',
  first_name: '',
  last_name: '',
  role: 'agent',
  password: '',
})
const error = ref('')
const loading = ref(false)

async function handleSubmit() {
  error.value = ''
  loading.value = true
  try {
    await usersStore.addUser(form.value)
    router.push({ name: 'user-list' })
  } catch (err) {
    const data = err.response?.data
    if (data) {
      const messages = Object.values(data).flat()
      error.value = messages.join(' ')
    } else {
      error.value = 'Failed to create user.'
    }
  } finally {
    loading.value = false
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
        Create User
      </p>
    </div>

    <div class="bg-white p-8 rounded-lg shadow">
      <form @submit.prevent="handleSubmit">
        <div class="mb-4">
          <label for="email" class="block mb-1 font-medium text-sm">Email</label>
          <input
            id="email"
            v-model="form.email"
            type="email"
            required
            autocomplete="off"
            class="w-full px-3 py-2 border border-gray-300 rounded text-base box-border focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-blue-400"
          />
        </div>

        <div class="flex gap-4">
          <div class="flex-1 mb-4">
            <label for="first_name" class="block mb-1 font-medium text-sm">First Name</label>
            <input
              id="first_name"
              v-model="form.first_name"
              type="text"
              required
              class="w-full px-3 py-2 border border-gray-300 rounded text-base box-border focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-blue-400"
            />
          </div>
          <div class="flex-1 mb-4">
            <label for="last_name" class="block mb-1 font-medium text-sm">Last Name</label>
            <input
              id="last_name"
              v-model="form.last_name"
              type="text"
              required
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
          <label for="password" class="block mb-1 font-medium text-sm">Password</label>
          <input
            id="password"
            v-model="form.password"
            type="password"
            required
            autocomplete="new-password"
            class="w-full px-3 py-2 border border-gray-300 rounded text-base box-border focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-blue-400"
          />
          <small class="block mt-1 text-gray-400 text-xs">
            Min 8 characters, with uppercase, lowercase, digit, and special character.
          </small>
        </div>

        <p v-if="error" class="text-red-600 text-sm my-2">{{ error }}</p>

        <button
          type="submit"
          :disabled="loading"
          class="w-full py-2.5 bg-blue-500 text-white rounded text-base cursor-pointer mt-2 hover:bg-blue-600 disabled:opacity-60 disabled:cursor-not-allowed"
        >
          {{ loading ? 'Creating...' : 'Create User' }}
        </button>
      </form>
    </div>
  </main>
</template>
