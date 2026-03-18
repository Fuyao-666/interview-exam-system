import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'

const routes = [
  {
    path: '/',
    redirect: '/login'
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue')
  },
  {
    path: '/exam',
    name: 'ExamEntry',
    component: () => import('@/views/ExamEntry.vue')
  },
  // 注意：result 路由必须在 :paperId 之前，否则会被错误匹配
  {
    path: '/exam/result/:paperId',
    name: 'ExamResult',
    component: () => import('@/views/ExamResult.vue')
  },
  {
    path: '/exam/:paperId',
    name: 'ExamTaking',
    component: () => import('@/views/ExamTaking.vue')
  },
  {
    path: '/admin',
    name: 'AdminDashboard',
    component: () => import('@/views/admin/Dashboard.vue'),
    meta: { requiresAuth: true, adminOnly: true }
  },
  {
    path: '/interviewer',
    name: 'InterviewerDashboard',
    component: () => import('@/views/interviewer/Dashboard.vue'),
    meta: { requiresAuth: true, interviewerOnly: true }
  },
  {
    path: '/interviewer/questions',
    name: 'QuestionManagement',
    component: () => import('@/views/interviewer/Questions.vue'),
    meta: { requiresAuth: true, interviewerOnly: true }
  },
  {
    path: '/interviewer/review',
    name: 'ReviewPapers',
    component: () => import('@/views/interviewer/Review.vue'),
    meta: { requiresAuth: true, interviewerOnly: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const userStore = useUserStore()

  if (to.meta.requiresAuth && !userStore.isLoggedIn) {
    next('/login')
    return
  }

  if (to.meta.adminOnly && !userStore.isAdmin) {
    next('/login')
    return
  }

  if (to.meta.interviewerOnly && !userStore.isInterviewer) {
    next('/login')
    return
  }

  next()
})

export default router
