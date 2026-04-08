<script setup>
import { onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

onMounted(async () => {
  if (authStore.isAuthenticated) {
    await authStore.fetchProfile()
  }
})
</script>

<template>
  <RouterView />
</template>
