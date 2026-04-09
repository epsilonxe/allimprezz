<script setup>
import { onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

async function handleLogout() {
  await authStore.logout()
  router.push({ name: 'login' })
}

onMounted(async () => {
  if (authStore.isAuthenticated) {
    await authStore.fetchProfile()
  }
})
</script>

<template>
  <div v-if="route.meta.requiresAuth !== false && authStore.isAuthenticated" class="min-h-screen bg-gray-100">
    <nav class="flex items-center justify-between px-8 py-3 bg-white shadow-sm">
      <router-link to="/dashboard" class="text-xl font-bold text-gray-900 no-underline">
        All Imprezz
      </router-link>
      <div class="flex items-center gap-4">
        <span class="text-sm text-gray-700">
          {{ authStore.fullName }}
          <span class="inline-block px-2 py-0.5 ml-1 bg-blue-50 text-blue-600 rounded-full text-xs capitalize">
            {{ authStore.user?.role }}
          </span>
        </span>
        <button
          class="px-3 py-1.5 bg-transparent border border-gray-300 rounded cursor-pointer text-sm hover:bg-gray-100"
          @click="handleLogout"
        >
          Sign out
        </button>
      </div>
    </nav>

    <RouterView />
  </div>

  <RouterView v-else />
</template>
