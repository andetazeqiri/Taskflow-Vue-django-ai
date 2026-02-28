import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import HomeView from '../views/HomeView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/LoginView.vue'),
      meta: { requiresAuth: false, isPublic: true }
    },
    {
      path: '/',
      name: 'home',
      component: HomeView,
      meta: { requiresAuth: true }
    },
    {
      path: '/tasks',
      name: 'tasks',
      component: () => import('../views/TasksView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/tasks/:id',
      name: 'taskDetail',
      component: () => import('../views/TaskDetailView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/about',
      name: 'about',
      component: () => import('../views/AboutView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/:pathMatch(.*)*',
      redirect: () => {
        const authStore = useAuthStore()
        return authStore.isAuthenticated ? '/tasks' : '/login'
      }
    }
  ],
})

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  const requiresAuth = to.meta.requiresAuth !== false
  const isPublic = to.meta.isPublic === true

  
  const isAuthenticated = authStore.isAuthenticated

  
  if (requiresAuth && !isAuthenticated) {
    console.warn(`[Router Guard] Unauthenticated user attempting to access protected route: ${to.path}`)
    return next({
      path: '/login',
      query: { redirect: to.fullPath }
    })
  }

 
  if (isPublic && isAuthenticated && to.path === '/login') {
    console.log('[Router Guard] Authenticated user redirected from login to tasks')
    return next('/tasks')
  }

  
  next()
})


router.afterEach((to, from) => {
  
  const authStore = useAuthStore()
  if (to.path !== from.path) {
    // authStore.clearError()
  }
})

export default router
