<template>
  <div class="interviewer-page">
    <!-- 顶部导航 -->
    <header class="top-header">
      <div class="header-brand">
        <span class="brand-icon">📋</span>
        <span class="brand-name">面试考试系统</span>
        <span class="role-badge interviewer">面试官</span>
      </div>
      <div class="header-user">
        <span class="username">{{ userStore.user?.username }}</span>
        <button class="btn-logout" @click="logout">退出登录</button>
      </div>
    </header>

    <!-- 主体 -->
    <div class="page-body">
      <!-- 侧边栏 -->
      <aside class="sidebar">
        <nav class="sidebar-nav">
          <router-link class="nav-item" to="/interviewer" exact-active-class="active">
            <span class="nav-icon">🏠</span>
            首页
          </router-link>
          <router-link class="nav-item" to="/interviewer/questions" active-class="active">
            <span class="nav-icon">📝</span>
            题库管理
          </router-link>
          <router-link class="nav-item" to="/interviewer/review" active-class="active">
            <span class="nav-icon">✅</span>
            试卷批阅
            <span v-if="pendingCount > 0" class="badge">{{ pendingCount }}</span>
          </router-link>
        </nav>
      </aside>

      <!-- 主内容 -->
      <main class="main-content">
        <!-- 欢迎横幅 -->
        <div class="welcome-banner">
          <div class="welcome-text">
            <h2>欢迎回来，{{ userStore.user?.username }}</h2>
            <p>今天是个好日子，开始工作吧！</p>
          </div>
          <div class="welcome-graphic">📋</div>
        </div>

        <!-- 统计卡片 -->
        <div class="stat-cards">
          <div class="stat-card pending-card" @click="$router.push('/interviewer/review')">
            <div class="stat-icon">📄</div>
            <div class="stat-info">
              <div class="stat-num">{{ pendingCount }}</div>
              <div class="stat-label">待批阅试卷</div>
            </div>
            <div class="stat-arrow">→</div>
          </div>
          <div class="stat-card" @click="$router.push('/interviewer/questions')">
            <div class="stat-icon">📝</div>
            <div class="stat-info">
              <div class="stat-num">-</div>
              <div class="stat-label">题库题目数</div>
            </div>
            <div class="stat-arrow">→</div>
          </div>
        </div>

        <!-- 功能入口 -->
        <div class="section-title">功能入口</div>
        <div class="action-grid">
          <div class="action-card" @click="$router.push('/interviewer/questions')">
            <div class="action-icon-wrap blue">📝</div>
            <div class="action-info">
              <h3>题库管理</h3>
              <p>录入、编辑和管理考题，支持单选、多选、简答三种题型</p>
            </div>
            <span class="action-arrow">›</span>
          </div>

          <div class="action-card" @click="$router.push('/interviewer/review')">
            <div class="action-icon-wrap green">✅</div>
            <div class="action-info">
              <h3>试卷批阅</h3>
              <p>批阅考生简答题答案，给出评分和评语</p>
              <span v-if="pendingCount > 0" class="pending-tip">{{ pendingCount }} 份待批阅</span>
            </div>
            <span class="action-arrow">›</span>
          </div>

          <div class="action-card" @click="showConfig = true">
            <div class="action-icon-wrap purple">⚙️</div>
            <div class="action-info">
              <h3>考试配置</h3>
              <p>设置抽题规则、每题分值和考试时长</p>
            </div>
            <span class="action-arrow">›</span>
          </div>
        </div>
      </main>
    </div>

    <!-- 考试配置弹窗 -->
    <div v-if="showConfig" class="modal-overlay" @click.self="showConfig = false">
      <div class="modal-box large-modal">
        <h3>考试配置</h3>
        <form @submit.prevent="saveConfig">
          <div class="config-grid">
            <div class="config-section">
              <div class="config-section-title">
                <span class="section-dot blue"></span> 单选题设置
              </div>
              <div class="config-row">
                <div class="form-group">
                  <label>题目数量</label>
                  <input v-model.number="config.single_count" type="number" class="form-input" min="0" />
                </div>
                <div class="form-group">
                  <label>每题分值</label>
                  <input v-model.number="config.single_score" type="number" class="form-input" min="0" />
                </div>
              </div>
            </div>

            <div class="config-section">
              <div class="config-section-title">
                <span class="section-dot green"></span> 多选题设置
              </div>
              <div class="config-row">
                <div class="form-group">
                  <label>题目数量</label>
                  <input v-model.number="config.multiple_count" type="number" class="form-input" min="0" />
                </div>
                <div class="form-group">
                  <label>每题分值</label>
                  <input v-model.number="config.multiple_score" type="number" class="form-input" min="0" />
                </div>
              </div>
            </div>

            <div class="config-section">
              <div class="config-section-title">
                <span class="section-dot orange"></span> 简答题设置
              </div>
              <div class="config-row">
                <div class="form-group">
                  <label>题目数量</label>
                  <input v-model.number="config.essay_count" type="number" class="form-input" min="0" />
                </div>
                <div class="form-group">
                  <label>每题分值</label>
                  <input v-model.number="config.essay_score" type="number" class="form-input" min="0" />
                </div>
              </div>
            </div>

            <div class="config-section full-width">
              <div class="config-section-title">
                <span class="section-dot purple"></span> 考试时长
              </div>
              <div class="form-group">
                <label>时长（分钟）</label>
                <input v-model.number="config.duration_minutes" type="number" class="form-input" min="1" style="max-width:160px" />
              </div>
            </div>
          </div>

          <div class="score-preview">
            总分预估：
            <strong>{{ config.single_count * config.single_score + config.multiple_count * config.multiple_score + config.essay_count * config.essay_score }}</strong> 分
          </div>

          <div class="modal-actions">
            <button type="button" class="btn-cancel" @click="showConfig = false">取消</button>
            <button type="submit" class="btn-save">保存配置</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import api from '@/api'

const router = useRouter()
const userStore = useUserStore()

const showConfig = ref(false)
const config = ref({
  single_count: 10,
  single_score: 2,
  multiple_count: 5,
  multiple_score: 4,
  essay_count: 2,
  essay_score: 15,
  duration_minutes: 60
})
const pendingPapers = ref([])
const pendingCount = computed(() => pendingPapers.value.length)

onMounted(() => {
  loadConfig()
  loadPendingPapers()
})

async function loadConfig() {
  try {
    const data = await api.get('/exam/config')
    config.value = data
  } catch (err) {
    console.error('加载配置失败:', err)
  }
}

async function loadPendingPapers() {
  try {
    pendingPapers.value = await api.get('/review/pending')
  } catch (err) {
    console.error('加载待办失败:', err)
  }
}

async function saveConfig() {
  try {
    await api.put('/exam/config', config.value)
    showConfig.value = false
  } catch (err) {
    alert('保存失败：' + (err.response?.data?.error || '未知错误'))
  }
}

function logout() {
  userStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.interviewer-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f0f2f5;
}

/* 顶部导航 */
.top-header {
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

.header-brand { display: flex; align-items: center; gap: 10px; }
.brand-icon { font-size: 22px; }
.brand-name { font-size: 16px; font-weight: 700; color: #1e293b; }

.role-badge {
  padding: 2px 10px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

.role-badge.interviewer { background: #eff6ff; color: #3b82f6; }

.header-user { display: flex; align-items: center; gap: 14px; }
.username { font-size: 14px; color: #64748b; }

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

.btn-logout:hover { border-color: #ef4444; color: #ef4444; }

/* 布局 */
.page-body { flex: 1; display: flex; }

.sidebar {
  width: 220px;
  flex-shrink: 0;
  background: #fff;
  border-right: 1px solid #e2e8f0;
  padding: 20px 12px;
}

.sidebar-nav { display: flex; flex-direction: column; gap: 4px; }

.nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  border-radius: 8px;
  font-size: 14px;
  color: #64748b;
  cursor: pointer;
  text-decoration: none;
  transition: all 0.2s;
  position: relative;
}

.nav-item:hover { background: #f1f5f9; color: #1e293b; }
.nav-item.active { background: #eef1fe; color: #4f6ef7; font-weight: 600; }
.nav-icon { font-size: 16px; }

.badge {
  margin-left: auto;
  background: #ef4444;
  color: #fff;
  border-radius: 10px;
  padding: 1px 7px;
  font-size: 11px;
  font-weight: 600;
}

/* 主内容 */
.main-content { flex: 1; padding: 28px; min-width: 0; }

/* 欢迎横幅 */
.welcome-banner {
  background: linear-gradient(135deg, #4f6ef7 0%, #7c3aed 100%);
  border-radius: 14px;
  padding: 28px 32px;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
}

.welcome-text h2 { font-size: 22px; font-weight: 700; margin-bottom: 6px; }
.welcome-text p { font-size: 14px; opacity: 0.85; }
.welcome-graphic { font-size: 52px; opacity: 0.6; }

/* 统计卡片 */
.stat-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 28px;
}

.stat-card {
  background: #fff;
  border-radius: 12px;
  padding: 20px 24px;
  display: flex;
  align-items: center;
  gap: 16px;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  transition: all 0.2s;
}

.stat-card:hover { transform: translateY(-2px); box-shadow: 0 6px 16px rgba(0,0,0,0.1); }

.stat-card.pending-card { border-left: 4px solid #ef4444; }

.stat-icon { font-size: 28px; }

.stat-info { flex: 1; }

.stat-num {
  font-size: 28px;
  font-weight: 800;
  color: #1e293b;
  line-height: 1;
  margin-bottom: 4px;
}

.stat-label { font-size: 13px; color: #64748b; }
.stat-arrow { font-size: 20px; color: #94a3b8; }

/* 功能入口 */
.section-title {
  font-size: 14px;
  font-weight: 600;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 16px;
}

.action-grid {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.action-card {
  background: #fff;
  border-radius: 12px;
  padding: 20px 24px;
  display: flex;
  align-items: center;
  gap: 16px;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  transition: all 0.2s;
  border: 1px solid transparent;
}

.action-card:hover {
  border-color: #4f6ef7;
  transform: translateX(4px);
  box-shadow: 0 4px 16px rgba(79,110,247,0.12);
}

.action-icon-wrap {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  flex-shrink: 0;
}

.action-icon-wrap.blue { background: #eff6ff; }
.action-icon-wrap.green { background: #f0fdf4; }
.action-icon-wrap.purple { background: #faf5ff; }

.action-info { flex: 1; }
.action-info h3 { font-size: 15px; font-weight: 600; color: #1e293b; margin-bottom: 4px; }
.action-info p { font-size: 13px; color: #64748b; }

.pending-tip {
  display: inline-block;
  margin-top: 4px;
  padding: 2px 8px;
  background: #fef2f2;
  color: #ef4444;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.action-arrow { font-size: 22px; color: #94a3b8; font-weight: 300; }

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
  max-height: 90vh;
  overflow-y: auto;
}

.large-modal { max-width: 600px; }

.modal-box h3 {
  font-size: 18px;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 24px;
}

.config-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.config-section { }
.full-width { grid-column: 1 / -1; }

.config-section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  font-weight: 600;
  color: #374151;
  margin-bottom: 12px;
}

.section-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.section-dot.blue { background: #3b82f6; }
.section-dot.green { background: #22c55e; }
.section-dot.orange { background: #f97316; }
.section-dot.purple { background: #7c3aed; }

.config-row { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }

.form-group { margin-bottom: 12px; }

.form-group label {
  display: block;
  font-size: 12px;
  font-weight: 500;
  color: #64748b;
  margin-bottom: 6px;
}

.form-input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 14px;
  outline: none;
  transition: border-color 0.2s;
}

.form-input:focus { border-color: #4f6ef7; }

.score-preview {
  padding: 12px 16px;
  background: #f8fafc;
  border-radius: 8px;
  font-size: 14px;
  color: #64748b;
  margin: 20px 0 0;
  text-align: center;
}

.score-preview strong { color: #4f6ef7; font-size: 18px; font-weight: 700; }

.modal-actions {
  display: flex;
  gap: 12px;
  margin-top: 20px;
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

.btn-save {
  padding: 9px 24px;
  background: #4f6ef7;
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-save:hover { background: #3a56e0; }
</style>
