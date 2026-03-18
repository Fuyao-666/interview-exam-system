<template>
  <div class="admin-page">
    <!-- 顶部导航 -->
    <header class="admin-header">
      <div class="header-brand">
        <span class="brand-icon">📋</span>
        <span class="brand-name">面试考试系统</span>
        <span class="role-badge">管理员</span>
      </div>
      <div class="header-user">
        <span class="username">{{ userStore.user?.username }}</span>
        <button class="btn-logout" @click="logout">退出登录</button>
      </div>
    </header>

    <!-- 主体 -->
    <div class="admin-body">
      <!-- 侧边栏 -->
      <aside class="sidebar">
        <nav class="sidebar-nav">
          <a
            class="nav-item"
            :class="{ active: activeTab === 'users' }"
            @click="activeTab = 'users'"
          >
            <span class="nav-icon">👥</span>
            账号管理
          </a>
          <a
            class="nav-item"
            :class="{ active: activeTab === 'results' }"
            @click="activeTab = 'results'"
          >
            <span class="nav-icon">📊</span>
            成绩档案
          </a>
        </nav>
      </aside>

      <!-- 主内容区 -->
      <main class="main-content">
        <!-- 账号管理 -->
        <div v-if="activeTab === 'users'" class="content-section">
          <div class="section-header">
            <div>
              <h2>账号管理</h2>
              <p>管理面试官账号</p>
            </div>
            <button class="btn-primary" @click="showCreateUser = true">
              + 新建账号
            </button>
          </div>

          <div class="data-card">
            <table class="data-table">
              <thead>
                <tr>
                  <th>用户名</th>
                  <th>角色</th>
                  <th>状态</th>
                  <th>创建时间</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="user in users" :key="user.id">
                  <td>
                    <div class="user-cell">
                      <div class="user-avatar">{{ user.username[0].toUpperCase() }}</div>
                      {{ user.username }}
                    </div>
                  </td>
                  <td>
                    <span class="role-tag" :class="user.role">
                      {{ user.role === 'admin' ? '管理员' : '面试官' }}
                    </span>
                  </td>
                  <td>
                    <span class="status-tag" :class="user.is_active ? 'active' : 'inactive'">
                      {{ user.is_active ? '正常' : '已停用' }}
                    </span>
                  </td>
                  <td class="text-muted">{{ formatDate(user.created_at) }}</td>
                  <td>
                    <div v-if="user.role !== 'admin'" class="action-group">
                      <button
                        class="btn-action"
                        :class="user.is_active ? 'danger' : 'success'"
                        @click="toggleUser(user.id)"
                      >
                        {{ user.is_active ? '停用' : '启用' }}
                      </button>
                      <button
                        class="btn-action delete"
                        @click="deleteUser(user.id, user.username)"
                      >
                        删除
                      </button>
                    </div>
                    <span v-else class="text-muted">-</span>
                  </td>
                </tr>
                <tr v-if="!users.length">
                  <td colspan="5" class="empty-row">暂无数据</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- 成绩档案 -->
        <div v-if="activeTab === 'results'" class="content-section">
          <div class="section-header">
            <div>
              <h2>成绩档案</h2>
              <p>查看所有考生考试记录</p>
            </div>
            <div class="filter-bar">
              <input
                v-model="filters.name"
                type="text"
                class="filter-input"
                placeholder="搜索姓名..."
                @input="loadResults"
              />
            </div>
          </div>

          <div class="data-card">
            <table class="data-table">
              <thead>
                <tr>
                  <th>姓名</th>
                  <th>公司</th>
                  <th>手机号</th>
                  <th>客观题</th>
                  <th>主观题</th>
                  <th>总分</th>
                  <th>切屏</th>
                  <th>状态</th>
                  <th>考试时间</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="result in results" :key="result.id">
                  <td><strong>{{ result.candidate_name }}</strong></td>
                  <td class="text-muted">{{ result.company || '-' }}</td>
                  <td class="text-muted">{{ result.phone || '-' }}</td>
                  <td>{{ result.objective_score }}</td>
                  <td>{{ result.subjective_score ?? '-' }}</td>
                  <td>
                    <span class="total-score">{{ result.total_score ?? '-' }}</span>
                  </td>
                  <td>
                    <span v-if="result.screen_focus_loss_count > 0" class="violation-tag">
                      {{ result.screen_focus_loss_count }}
                    </span>
                    <span v-else class="text-muted">-</span>
                  </td>
                  <td>
                    <span class="status-tag" :class="result.status">
                      {{ result.status === 'submitted' ? '待批阅' : result.status === 'graded' ? '已批阅' : result.status === 'in_progress' ? '考试中' : result.status }}
                    </span>
                  </td>
                  <td class="text-muted">{{ formatDateTime(result.start_time) }}</td>
                  <td>
                    <button class="btn-action delete" @click="deletePaper(result.id, result.candidate_name)">
                      删除
                    </button>
                  </td>
                </tr>
                <tr v-if="!results.length">
                  <td colspan="10" class="empty-row">暂无数据</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </main>
    </div>

    <!-- 创建用户弹窗 -->
    <div v-if="showCreateUser" class="modal-overlay" @click.self="showCreateUser = false">
      <div class="modal-box">
        <h3>创建面试官账号</h3>
        <form @submit.prevent="createUser">
          <div class="form-group">
            <label>用户名</label>
            <input v-model="newUser.username" class="form-input" type="text" placeholder="请输入用户名" required />
          </div>
          <div class="form-group">
            <label>初始密码</label>
            <input v-model="newUser.password" class="form-input" type="password" placeholder="请输入密码" required />
          </div>
          <div class="modal-actions">
            <button type="button" class="btn-cancel" @click="showCreateUser = false">取消</button>
            <button type="submit" class="btn-primary">创建账号</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import api from '@/api'

const router = useRouter()
const userStore = useUserStore()

const activeTab = ref('users')
const users = ref([])
const results = ref([])
const showCreateUser = ref(false)
const newUser = ref({ username: '', password: '' })
const filters = ref({ name: '' })

onMounted(() => {
  loadUsers()
  loadResults()
})

async function loadUsers() {
  try {
    users.value = await api.get('/admin/users')
  } catch (err) {
    console.error('加载用户失败:', err)
  }
}

async function loadResults() {
  try {
    const params = new URLSearchParams()
    if (filters.value.name) params.append('name', filters.value.name)
    results.value = await api.get(`/admin/results?${params.toString()}`)
  } catch (err) {
    console.error('加载成绩失败:', err)
  }
}

async function toggleUser(userId) {
  try {
    await api.post(`/admin/users/${userId}/toggle`)
    loadUsers()
  } catch (err) {
    alert('操作失败：' + (err.response?.data?.error || '未知错误'))
  }
}

async function deleteUser(userId, username) {
  if (!confirm(`确定要删除面试官「${username}」吗？此操作不可恢复。`)) return
  try {
    await api.delete(`/admin/users/${userId}`)
    loadUsers()
  } catch (err) {
    alert('删除失败：' + (err.response?.data?.error || '未知错误'))
  }
}

async function deletePaper(paperId, candidateName) {
  if (!confirm(`确定要删除「${candidateName}」的试卷记录吗？此操作不可恢复。`)) return
  try {
    await api.delete(`/admin/papers/${paperId}`)
    loadResults()
  } catch (err) {
    alert('删除失败：' + (err.response?.data?.error || '未知错误'))
  }
}

async function createUser() {
  try {
    await api.post('/admin/users', newUser.value)
    showCreateUser.value = false
    newUser.value = { username: '', password: '' }
    loadUsers()
  } catch (err) {
    alert('创建失败：' + (err.response?.data?.error || '未知错误'))
  }
}

function logout() {
  userStore.logout()
  router.push('/login')
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString('zh-CN')
}

function formatDateTime(dateStr) {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleString('zh-CN')
}
</script>

<style scoped>
.admin-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f0f2f5;
}

/* 顶部导航 */
.admin-header {
  height: 60px;
  background: #fff;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}

.header-brand {
  display: flex;
  align-items: center;
  gap: 10px;
}

.brand-icon { font-size: 22px; }

.brand-name {
  font-size: 16px;
  font-weight: 700;
  color: #1e293b;
}

.role-badge {
  padding: 2px 10px;
  background: #4f6ef7;
  color: #fff;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

.header-user {
  display: flex;
  align-items: center;
  gap: 14px;
}

.username {
  font-size: 14px;
  color: #64748b;
}

.btn-logout {
  padding: 6px 16px;
  background: transparent;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-size: 13px;
  color: #64748b;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-logout:hover {
  border-color: #ef4444;
  color: #ef4444;
}

/* 主体布局 */
.admin-body {
  flex: 1;
  display: flex;
}

/* 侧边栏 */
.sidebar {
  width: 220px;
  flex-shrink: 0;
  background: #fff;
  border-right: 1px solid #e2e8f0;
  padding: 20px 12px;
}

.sidebar-nav {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  border-radius: 8px;
  font-size: 14px;
  color: #64748b;
  cursor: pointer;
  transition: all 0.2s;
  text-decoration: none;
  user-select: none;
}

.nav-item:hover {
  background: #f1f5f9;
  color: #1e293b;
}

.nav-item.active {
  background: #eef1fe;
  color: #4f6ef7;
  font-weight: 600;
}

.nav-icon { font-size: 16px; }

/* 主内容 */
.main-content {
  flex: 1;
  padding: 28px;
  min-width: 0;
}

.content-section { }

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 12px;
}

.section-header h2 {
  font-size: 20px;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 2px;
}

.section-header p {
  font-size: 13px;
  color: #94a3b8;
}

.btn-primary {
  padding: 9px 20px;
  background: #4f6ef7;
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s;
  white-space: nowrap;
}

.btn-primary:hover { background: #3a56e0; }

.filter-bar {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.filter-input {
  padding: 8px 14px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 13px;
  outline: none;
  transition: border-color 0.2s;
  width: 160px;
}

.filter-input:focus { border-color: #4f6ef7; }

/* 数据卡片 */
.data-card {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
  overflow: hidden;
}

/* 表格 */
.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.data-table th {
  padding: 12px 16px;
  text-align: left;
  font-size: 12px;
  font-weight: 600;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  background: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
  white-space: nowrap;
}

.data-table td {
  padding: 14px 16px;
  border-bottom: 1px solid #f1f5f9;
  color: #374151;
  vertical-align: middle;
}

.data-table tbody tr:last-child td { border-bottom: none; }
.data-table tbody tr:hover td { background: #f8fafc; }

.user-cell {
  display: flex;
  align-items: center;
  gap: 10px;
}

.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: linear-gradient(135deg, #4f6ef7, #7c3aed);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 600;
  flex-shrink: 0;
}

.role-tag {
  padding: 3px 10px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

.role-tag.admin { background: #ede9fe; color: #7c3aed; }
.role-tag.interviewer { background: #eff6ff; color: #3b82f6; }

.status-tag {
  padding: 3px 10px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

.status-tag.active { background: #f0fdf4; color: #22c55e; }
.status-tag.inactive { background: #fef2f2; color: #ef4444; }
.status-tag.submitted { background: #fff7ed; color: #f97316; }
.status-tag.graded { background: #f0fdf4; color: #22c55e; }
.status-tag.in_progress { background: #eff6ff; color: #3b82f6; }

.total-score {
  font-weight: 700;
  color: #4f6ef7;
  font-size: 15px;
}

.violation-tag {
  font-size: 12px;
  color: #ef4444;
  font-weight: 500;
}

.text-muted { color: #94a3b8; }

.btn-action {
  padding: 5px 14px;
  border: none;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: opacity 0.2s;
}

.btn-action.danger { background: #fef2f2; color: #ef4444; }
.btn-action.danger:hover { background: #fee2e2; }
.btn-action.success { background: #f0fdf4; color: #22c55e; }
.btn-action.success:hover { background: #dcfce7; }
.btn-action.delete { background: #fef2f2; color: #ef4444; }
.btn-action.delete:hover { background: #fee2e2; }

.action-group {
  display: flex;
  gap: 6px;
}

.empty-row {
  text-align: center;
  color: #94a3b8;
  padding: 48px !important;
  font-size: 14px;
}

/* 弹窗 */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
}

.modal-box {
  background: #fff;
  border-radius: 16px;
  padding: 32px;
  width: 100%;
  max-width: 420px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.15);
}

.modal-box h3 {
  font-size: 18px;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 24px;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  font-size: 13px;
  font-weight: 500;
  color: #374151;
  margin-bottom: 6px;
}

.form-input {
  width: 100%;
  padding: 10px 14px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 14px;
  outline: none;
  transition: border-color 0.2s;
}

.form-input:focus { border-color: #4f6ef7; }

.modal-actions {
  display: flex;
  gap: 12px;
  margin-top: 24px;
  justify-content: flex-end;
}

.btn-cancel {
  padding: 9px 20px;
  background: #f1f5f9;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  color: #64748b;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-cancel:hover { background: #e2e8f0; }
</style>
