<template>
  <div class="app-layout">
    <header class="page-header">
      <div class="logo">📋 面试考试系统</div>
      <div class="header-right">
        <span class="username">👤 {{ userStore.user?.username }}</span>
        <span class="role-tag">{{ userStore.isAdmin ? '管理员' : '面试官' }}</span>
        <button class="btn btn-ghost" style="padding:6px 14px;font-size:13px;" @click="logout">退出</button>
      </div>
    </header>

    <div class="layout">
      <nav class="sidebar">
        <template v-if="userStore.isAdmin">
          <router-link class="sidebar-item" to="/admin" :class="{ active: $route.path === '/admin' }">
            <span>📊</span> 成绩档案
          </router-link>
          <router-link class="sidebar-item" to="/admin/users" :class="{ active: $route.path === '/admin/users' }">
            <span>👥</span> 账号管理
          </router-link>
          <router-link class="sidebar-item" to="/interviewer" :class="{ active: $route.path.startsWith('/interviewer') }">
            <span>🔧</span> 面试官功能
          </router-link>
        </template>
        <template v-else>
          <router-link class="sidebar-item" to="/interviewer" :class="{ active: $route.path === '/interviewer' }">
            <span>🏠</span> 首页
          </router-link>
          <router-link class="sidebar-item" to="/interviewer/questions" :class="{ active: $route.path === '/interviewer/questions' }">
            <span>📝</span> 题库管理
          </router-link>
          <router-link class="sidebar-item" to="/interviewer/review" :class="{ active: $route.path === '/interviewer/review' }">
            <span>✅</span> 试卷批阅
          </router-link>
        </template>
      </nav>

      <main class="main-content">
        <slot />
      </main>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

function logout() {
  userStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.app-layout { min-height: 100vh; display: flex; flex-direction: column; }
</style>
