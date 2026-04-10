import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/login',
    name: 'login',
    component: () => import('@/views/LoginView.vue'),
    meta: { requiresAuth: false },
  },
  {
    path: '/dashboard',
    name: 'dashboard',
    component: () => import('@/views/DashboardView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/profile',
    name: 'profile',
    component: () => import('@/views/ProfileView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/tours',
    name: 'tour-list',
    component: () => import('@/views/TourListView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/tours/create',
    name: 'tour-create',
    component: () => import('@/views/TourCreateView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/tours/:id',
    name: 'tour-detail',
    component: () => import('@/views/TourDetailView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/admin/users',
    name: 'user-list',
    component: () => import('@/views/UserListView.vue'),
    meta: { requiresAuth: true, requiresAdmin: true },
  },
  {
    path: '/admin/users/create',
    name: 'user-create',
    component: () => import('@/views/UserCreateView.vue'),
    meta: { requiresAuth: true, requiresAdmin: true },
  },
  {
    path: '/admin/users/:id',
    name: 'user-detail',
    component: () => import('@/views/UserDetailView.vue'),
    meta: { requiresAuth: true, requiresAdmin: true },
  },
  {
    path: '/',
    redirect: '/dashboard',
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

router.beforeEach(async (to) => {
  const isAuthenticated = !!localStorage.getItem('access_token')

  if (to.meta.requiresAuth && !isAuthenticated) {
    return { name: 'login' }
  }
  if (to.name === 'login' && isAuthenticated) {
    return { name: 'dashboard' }
  }

  if (to.meta.requiresAdmin && isAuthenticated) {
    const { useAuthStore } = await import('@/stores/auth')
    const authStore = useAuthStore()
    if (!authStore.user) {
      await authStore.fetchProfile()
    }
    if (!authStore.isAdmin) {
      return { name: 'dashboard' }
    }
  }
})

export default router
