<template>
  <div class="login-page">
    <div class="login-left">
      <div class="brand">
        <div class="brand-icon">📋</div>
        <h1>面试考试系统</h1>
        <p>专业、高效的在线面试评测平台</p>
      </div>
      <div class="features">
        <div class="feature-item">
          <span class="feature-icon">⚡</span>
          <span>随机抽题，每次不同</span>
        </div>
        <div class="feature-item">
          <span class="feature-icon">🛡️</span>
          <span>防作弊监控，公平公正</span>
        </div>
        <div class="feature-item">
          <span class="feature-icon">📊</span>
          <span>自动评分，实时结果</span>
        </div>
      </div>
    </div>

    <div class="login-right">
      <div class="login-card">
        <h2>管理后台登录</h2>
        <p class="login-subtitle">面试官 / 系统管理员</p>

        <div v-if="error" class="alert alert-error">{{ error }}</div>

        <form @submit.prevent="handleLogin">
          <div class="form-group">
            <label>用户名</label>
            <input
              v-model="username"
              class="form-control"
              type="text"
              placeholder="请输入用户名"
              required
              autocomplete="username"
            />
          </div>

          <div class="form-group">
            <label>密码</label>
            <input
              v-model="password"
              class="form-control"
              type="password"
              placeholder="请输入密码"
              required
              autocomplete="current-password"
            />
          </div>

          <button type="submit" class="btn btn-primary btn-full btn-lg" :disabled="loading">
            {{ loading ? '登录中...' : '登 录' }}
          </button>
        </form>

        <div class="divider"><span>或者</span></div>

        <router-link to="/exam" class="btn btn-outline btn-full">
          候选人答题入口 →
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import api from '@/api'

const router = useRouter()
const userStore = useUserStore()

const username = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

async function handleLogin() {
  loading.value = true
  error.value = ''
  try {
    const data = await api.post('/auth/login', {
      username: username.value,
      password: password.value
    })
    userStore.setUser(data.user, data.access_token)
    if (data.user.role === 'admin') {
      router.push('/admin')
    } else {
      router.push('/interviewer')
    }
  } catch (err) {
    error.value = err.response?.data?.error || '用户名或密码错误'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
}

.login-left {
  flex: 1;
  background: linear-gradient(135deg, #4f6ef7 0%, #7c3aed 100%);
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 60px;
  color: #fff;
}

.brand-icon {
  font-size: 52px;
  margin-bottom: 20px;
}

.brand h1 {
  font-size: 32px;
  font-weight: 700;
  margin-bottom: 12px;
}

.brand p {
  font-size: 16px;
  opacity: 0.85;
  margin-bottom: 48px;
}

.features {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 15px;
  opacity: 0.9;
}

.feature-icon {
  font-size: 20px;
}

.login-right {
  width: 480px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
  background: #fff;
}

.login-card {
  width: 100%;
  max-width: 380px;
}

.login-card h2 {
  font-size: 26px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 6px;
}

.login-subtitle {
  font-size: 14px;
  color: var(--text-muted);
  margin-bottom: 32px;
}

.divider {
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 20px 0;
  color: var(--text-muted);
  font-size: 13px;
}
.divider::before,
.divider::after {
  content: '';
  flex: 1;
  height: 1px;
  background: var(--border);
}

@media (max-width: 768px) {
  .login-left {
    display: none;
  }
  .login-right {
    width: 100%;
  }
}
</style>
