import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import { loginUser, logoutUser, getProfile } from '@/api/auth'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const accessToken = ref(localStorage.getItem('access_token'))
  const refreshToken = ref(localStorage.getItem('refresh_token'))

  const isAuthenticated = computed(() => !!accessToken.value)
  const isAdmin = computed(() => user.value?.role === 'admin')
  const isStaff = computed(() => ['admin', 'staff'].includes(user.value?.role))
  const fullName = computed(() =>
    user.value ? `${user.value.first_name} ${user.value.last_name}`.trim() : '',
  )

  async function login(email, password) {
    const { data } = await loginUser(email, password)
    accessToken.value = data.access
    refreshToken.value = data.refresh
    user.value = data.user
    localStorage.setItem('access_token', data.access)
    localStorage.setItem('refresh_token', data.refresh)
    return data
  }

  async function logout() {
    try {
      if (refreshToken.value) {
        await logoutUser(refreshToken.value)
      }
    } catch {
      // Ignore logout API errors — clear local state regardless
    }
    user.value = null
    accessToken.value = null
    refreshToken.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  }

  async function fetchProfile() {
    try {
      const { data } = await getProfile()
      user.value = data
    } catch {
      await logout()
    }
  }

  function setTokens(access, refresh) {
    accessToken.value = access
    refreshToken.value = refresh
    localStorage.setItem('access_token', access)
    if (refresh) {
      localStorage.setItem('refresh_token', refresh)
    }
  }

  return {
    user,
    accessToken,
    refreshToken,
    isAuthenticated,
    isAdmin,
    isStaff,
    fullName,
    login,
    logout,
    fetchProfile,
    setTokens,
  }
})
