<template>
  <div class="exam-entry-page">
    <div class="entry-header">
      <div class="entry-logo">📋 面试考试系统</div>
      <div class="entry-tip">候选人通道</div>
    </div>

    <div class="entry-body">
      <div class="entry-left">
        <h1>欢迎参加<br/>在线面试测评</h1>
        <p>请如实填写个人信息，系统将为您生成专属试卷</p>

        <div class="exam-info">
          <div class="info-item">
            <span class="info-icon">⏱</span>
            <div>
              <div class="info-label">考试时长</div>
              <div class="info-value">{{ config.duration_minutes }} 分钟</div>
            </div>
          </div>
          <div class="info-item">
            <span class="info-icon">📝</span>
            <div>
              <div class="info-label">题目总数</div>
              <div class="info-value">{{ totalCount }} 题</div>
            </div>
          </div>
          <div class="info-item">
            <span class="info-icon">🎯</span>
            <div>
              <div class="info-label">满分</div>
              <div class="info-value">{{ totalScore }} 分</div>
            </div>
          </div>
        </div>

        <div class="exam-structure">
          <div class="structure-title">试卷结构</div>
          <div class="structure-items">
            <div class="structure-item">
              <span class="s-count">{{ config.choice_count }}</span>
              <span class="s-label">道选择题</span>
              <span class="s-score">{{ config.choice_total_score }}分</span>
            </div>
            <span class="s-plus">+</span>
            <div class="structure-item">
              <span class="s-count">{{ config.essay_count }}</span>
              <span class="s-label">道简答题</span>
              <span class="s-score">{{ config.essay_total_score }}分</span>
            </div>
            <span class="s-plus">+</span>
            <div class="structure-item">
              <span class="s-count">{{ config.programming_count }}</span>
              <span class="s-label">道编程/设计题</span>
              <span class="s-score">{{ config.programming_total_score }}分</span>
            </div>
          </div>
        </div>

        <div class="notice-box">
          <div class="notice-title">⚠️ 考试须知</div>
          <ul>
            <li>切换页面/最小化窗口累计 <strong>3 次</strong>将被强制交卷</li>
            <li>禁止使用右键菜单及复制粘贴</li>
            <li>中途断网可重新打开页面恢复答题</li>
            <li>时间结束后系统自动提交</li>
          </ul>
        </div>
      </div>

      <div class="entry-right">
        <div class="entry-card card">
          <h2>填写个人信息</h2>
          <p class="card-subtitle">信息将用于生成您的专属试卷</p>

          <div v-if="error" class="alert alert-error">{{ error }}</div>

          <form @submit.prevent="handleStart">
            <div class="form-group">
              <label>姓名 <span class="required">*</span></label>
              <input v-model="form.name" class="form-control" type="text" placeholder="请输入您的真实姓名" required />
            </div>
            <div class="form-group">
              <label>手机号 <span class="required">*</span></label>
              <input v-model="form.phone" class="form-control" type="tel" placeholder="请输入 11 位手机号码" required />
            </div>
            <div class="form-group">
              <label>面试公司 <span class="required">*</span></label>
              <input v-model="form.company" class="form-control" type="text" placeholder="请输入面试公司名称" required />
            </div>
            <div class="form-group">
              <label>应聘岗位</label>
              <div class="position-fixed">RPA专员</div>
            </div>

            <button type="submit" class="btn btn-success btn-full btn-lg" :disabled="loading">
              {{ loading ? '正在生成试卷...' : '开始考试' }}
            </button>
          </form>

          <div class="back-link">
            <router-link to="/login">← 返回管理后台</router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/api'

const router = useRouter()

const form = ref({ name: '', phone: '', company: '' })
const error = ref('')
const loading = ref(false)
const config = ref({ choice_count: 10, choice_total_score: 30, essay_count: 3, essay_total_score: 30, programming_count: 2, programming_total_score: 40, duration_minutes: 90 })

const totalCount = computed(() =>
  config.value.choice_count + config.value.essay_count + config.value.programming_count
)

const totalScore = computed(() =>
  config.value.choice_total_score + config.value.essay_total_score + config.value.programming_total_score
)

onMounted(async () => {
  try {
    const data = await api.get('/exam/config')
    config.value = data
  } catch {}
})

async function handleStart() {
  if (!form.value.name.trim() || !form.value.phone.trim() || !form.value.company.trim()) {
    error.value = '请填写姓名、手机号和面试公司'
    return
  }
  loading.value = true
  error.value = ''
  try {
    const data = await api.post('/candidate/start', {
      name: form.value.name.trim(),
      phone: form.value.phone.trim(),
      company: form.value.company.trim()
    })
    router.push(`/exam/${data.paper_id}`)
  } catch (err) {
    error.value = err.response?.data?.error || '开始考试失败，请稍后重试'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.exam-entry-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  flex-direction: column;
}
.entry-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 40px;
}
.entry-logo { font-size: 18px; font-weight: 600; color: #fff; }
.entry-tip { font-size: 13px; background: rgba(255,255,255,0.2); padding: 4px 14px; border-radius: 20px; color: #fff; }
.entry-body {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 60px;
  padding: 20px 40px 60px;
  max-width: 1100px;
  margin: 0 auto;
  width: 100%;
}
.entry-left { flex: 1; color: #fff; max-width: 460px; }
.entry-left h1 { font-size: 38px; font-weight: 700; line-height: 1.35; margin-bottom: 16px; }
.entry-left > p { font-size: 16px; opacity: 0.85; margin-bottom: 36px; }
.exam-info { display: flex; gap: 16px; margin-bottom: 28px; flex-wrap: wrap; }
.info-item {
  display: flex; align-items: center; gap: 12px;
  background: rgba(255,255,255,0.15); backdrop-filter: blur(10px);
  padding: 14px 18px; border-radius: 12px; flex: 1; min-width: 110px;
}
.info-icon { font-size: 24px; }
.info-label { font-size: 12px; opacity: 0.75; margin-bottom: 2px; }
.info-value { font-size: 18px; font-weight: 700; }
.exam-structure {
  background: rgba(255,255,255,0.12);
  border-radius: 12px;
  padding: 16px 20px;
  margin-bottom: 20px;
}
.structure-title { font-size: 13px; font-weight: 600; opacity: 0.8; margin-bottom: 12px; }
.structure-items { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.structure-item {
  display: flex; align-items: baseline; gap: 4px;
  background: rgba(255,255,255,0.15);
  padding: 8px 14px;
  border-radius: 8px;
}
.s-count { font-size: 22px; font-weight: 800; }
.s-label { font-size: 13px; opacity: 0.85; }
.s-score { font-size: 13px; font-weight: 600; color: #fde68a; margin-left: 4px; }
.s-plus { font-size: 18px; font-weight: 700; opacity: 0.6; }
.notice-box { background: rgba(255,255,255,0.12); border-radius: 12px; padding: 18px 20px; }
.notice-title { font-size: 14px; font-weight: 600; margin-bottom: 10px; }
.notice-box ul { list-style: none; display: flex; flex-direction: column; gap: 8px; }
.notice-box li { font-size: 13px; opacity: 0.85; padding-left: 14px; position: relative; }
.notice-box li::before { content: '·'; position: absolute; left: 0; }
.notice-box strong { color: #fde68a; }
.position-fixed {
  padding: 10px 14px;
  background: #f1f5f9;
  border-radius: 8px;
  font-size: 14px;
  color: #64748b;
  border: 1px solid #e2e8f0;
}
.entry-right { width: 400px; flex-shrink: 0; }
.entry-card { padding: 36px; }
.entry-card h2 { font-size: 22px; font-weight: 700; margin-bottom: 6px; }
.card-subtitle { font-size: 14px; color: var(--text-muted); margin-bottom: 28px; }
.required { color: var(--danger); }
.back-link { margin-top: 20px; text-align: center; }
.back-link a { font-size: 13px; color: var(--text-muted); text-decoration: none; }
.back-link a:hover { color: var(--primary); }
@media (max-width: 900px) {
  .entry-body { flex-direction: column; gap: 32px; padding: 20px 20px 40px; }
  .entry-left h1 { font-size: 28px; }
  .entry-right { width: 100%; }
}
</style>
