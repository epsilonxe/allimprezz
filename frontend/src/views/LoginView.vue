<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const email = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

async function handleLogin() {
  error.value = ''
  loading.value = true
  try {
    await authStore.login(email.value, password.value)
    router.push({ name: 'dashboard' })
  } catch (err) {
    error.value = err.response?.data?.detail || 'Invalid email or password.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="flex items-center justify-center min-h-screen bg-gray-100">
    <div class="bg-white p-8 rounded-lg shadow w-full max-w-sm">
      <h1 class="text-2xl font-bold text-center mb-1">All Imprezz</h1>
      <p class="text-center text-gray-500 mb-6">Sign in to your account</p>

      <form @submit.prevent="handleLogin">
        <div class="mb-4">
          <label for="email" class="block mb-1 font-medium text-sm">Email</label>
          <input
            id="email"
            v-model="email"
            type="email"
            placeholder="you@example.com"
            required
            autocomplete="email"
            class="w-full px-3 py-2 border border-gray-300 rounded text-base box-border focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-blue-400"
          />
        </div>

        <div class="mb-4">
          <label for="password" class="block mb-1 font-medium text-sm">Password</label>
          <input
            id="password"
            v-model="password"
            type="password"
            placeholder="Password"
            required
            autocomplete="current-password"
            class="w-full px-3 py-2 border border-gray-300 rounded text-base box-border focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-blue-400"
          />
        </div>

        <p v-if="error" class="text-red-600 text-sm my-2">{{ error }}</p>

        <button
          type="submit"
          :disabled="loading"
          class="w-full py-2.5 bg-blue-500 text-white rounded text-base cursor-pointer mt-2 hover:bg-blue-600 disabled:opacity-60 disabled:cursor-not-allowed"
        >
          {{ loading ? 'Signing in...' : 'Sign in' }}
        </button>
      </form>
    </div>
  </div>
</template>
