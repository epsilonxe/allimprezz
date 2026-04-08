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
    path: '/',
    redirect: '/dashboard',
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

router.beforeEach((to) => {
  const isAuthenticated = !!localStorage.getItem('access_token')

  if (to.meta.requiresAuth && !isAuthenticated) {
    return { name: 'login' }
  }
  if (to.name === 'login' && isAuthenticated) {
    return { name: 'dashboard' }
  }
})

export default router
