<script setup>
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

async function handleLogout() {
  await authStore.logout()
  router.push({ name: 'login' })
}
</script>

<template>
  <div class="dashboard">
    <header class="dashboard-header">
      <h1>All Imprezz</h1>
      <div class="header-actions">
        <span class="user-info">
          {{ authStore.fullName }}
          <span class="role-badge">{{ authStore.user?.role }}</span>
        </span>
        <button class="logout-btn" @click="handleLogout">Sign out</button>
      </div>
    </header>

    <main class="dashboard-content">
      <h2>Welcome, {{ authStore.fullName }}</h2>
      <p>You are signed in as <strong>{{ authStore.user?.email }}</strong>.</p>
    </main>
  </div>
</template>

<style scoped>
.dashboard {
  min-height: 100vh;
  background-color: #f5f5f5;
}

.dashboard-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 2rem;
  background: white;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.dashboard-header h1 {
  margin: 0;
  font-size: 1.25rem;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.user-info {
  font-size: 0.875rem;
  color: #333;
}

.role-badge {
  display: inline-block;
  padding: 0.125rem 0.5rem;
  margin-left: 0.5rem;
  background-color: #e8f0fe;
  color: #1a73e8;
  border-radius: 12px;
  font-size: 0.75rem;
  text-transform: capitalize;
}

.logout-btn {
  padding: 0.375rem 0.75rem;
  background: none;
  border: 1px solid #ccc;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.875rem;
}

.logout-btn:hover {
  background-color: #f0f0f0;
}

.dashboard-content {
  padding: 2rem;
  max-width: 800px;
  margin: 0 auto;
}

.dashboard-content h2 {
  margin-top: 0;
}
</style>
