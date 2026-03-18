<template>
  <div class="result-page">
    <div class="result-container">
      <!-- 加载状态 -->
      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <p>加载中...</p>
      </div>

      <!-- 结果内容 -->
      <template v-else-if="paper">
        <!-- 顶部成绩卡 -->
        <div class="score-hero">
          <div class="hero-bg"></div>
          <div class="score-header">
            <div class="result-icon">
              <span v-if="paper.status === 'graded'">🎉</span>
              <span v-else>📋</span>
            </div>
            <h1>{{ paper.status === 'graded' ? '考试成绩' : '已成功交卷' }}</h1>
            <p>{{ paper.status === 'graded' ? '以下是您的考试成绩' : '简答题正在等待批阅' }}</p>
          </div>
          <div class="score-display">
            <div class="score-block">
              <div class="score-num">{{ paper.objective_score ?? '-' }}</div>
              <div class="score-lbl">客观题</div>
            </div>
            <div class="score-plus">+</div>
            <div class="score-block">
              <div class="score-num">{{ paper.subjective_score ?? '待批阅' }}</div>
              <div class="score-lbl">主观题</div>
            </div>
            <div class="score-equals">=</div>
            <div class="score-block total">
              <div class="score-num">{{ paper.status === 'graded' ? paper.total_score : '-' }}</div>
              <div class="score-lbl">总分</div>
            </div>
          </div>
        </div>

        <!-- 详情卡片 -->
        <div class="detail-cards">
          <!-- 考生信息 -->
          <div class="info-card">
            <div class="card-title">考生信息</div>
            <div class="info-row">
              <span class="info-key">姓名</span>
              <span class="info-val">{{ paper.candidate_name }}</span>
            </div>
            <div class="info-row">
              <span class="info-key">应聘岗位</span>
              <span class="info-val">RPA专员</span>
            </div>
            <div class="info-row">
              <span class="info-key">面试公司</span>
              <span class="info-val">{{ paper.company || '未填写' }}</span>
            </div>
            <div class="info-row">
              <span class="info-key">考试时间</span>
              <span class="info-val">{{ formatDate(paper.start_time) }}</span>
            </div>
          </div>

          <!-- 违规记录 -->
          <div v-if="paper.screen_focus_loss_count > 0" class="info-card violation-card">
            <div class="card-title warning-title">违规记录</div>
            <div class="violation-detail">
              <span class="violation-icon">⚠️</span>
              <div>
                <p>切换屏幕次数：<strong>{{ paper.screen_focus_loss_count }} 次</strong></p>
                <p class="violation-tip">该记录已提交给面试官参考</p>
              </div>
            </div>
          </div>

          <!-- 面试官评语 -->
          <div v-if="paper.grader_comment" class="info-card comment-card">
            <div class="card-title success-title">面试官评语</div>
            <p class="comment-text">{{ paper.grader_comment }}</p>
          </div>
        </div>

        <!-- 状态提示 -->
        <div v-if="paper.status === 'submitted'" class="status-notice pending">
          <span class="notice-icon">📝</span>
          <div>
            <p class="notice-title">等待批阅</p>
            <p>简答题正在等待面试官批阅，批阅完成后您可以查看完整成绩。</p>
          </div>
        </div>
        <div v-else-if="paper.status === 'graded'" class="status-notice graded">
          <span class="notice-icon">✅</span>
          <div>
            <p class="notice-title">批阅完成</p>
            <p>试卷已完成全部批阅，以上为您的最终成绩。</p>
          </div>
        </div>

        <!-- 返回按钮 -->
        <div class="result-actions">
          <button class="btn-home" @click="goHome">返回首页</button>
        </div>
      </template>

      <!-- 错误状态 -->
      <div v-else class="empty-state">
        <div class="empty-icon">😕</div>
        <p>暂时无法获取考试结果</p>
        <button class="btn-home" @click="goHome">返回首页</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '@/api'

const route = useRoute()
const paperId = route.params.paperId

const paper = ref(null)
const loading = ref(true)

onMounted(async () => {
  try {
    paper.value = await api.get(`/exam/result/${paperId}`)
  } catch (err) {
    console.error('获取结果失败:', err)
  } finally {
    loading.value = false
  }
})

function formatDate(dateStr) {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleString('zh-CN')
}

function goHome() {
  window.location.href = '/exam'
}
</script>

<style scoped>
.result-page {
  min-height: 100vh;
  background: #f0f2f5;
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding: 40px 20px 60px;
}

.result-container {
  width: 100%;
  max-width: 700px;
}

/* 加载 */
.loading-state {
  text-align: center;
  padding: 80px 20px;
  color: #64748b;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #e2e8f0;
  border-top-color: #4f6ef7;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin: 0 auto 16px;
}

@keyframes spin { to { transform: rotate(360deg); } }

/* 成绩英雄区 */
.score-hero {
  position: relative;
  background: linear-gradient(135deg, #4f6ef7 0%, #7c3aed 100%);
  border-radius: 16px;
  padding: 40px 40px 48px;
  color: #fff;
  margin-bottom: 24px;
  overflow: hidden;
}

.hero-bg {
  position: absolute;
  inset: 0;
  background: radial-gradient(circle at 80% 20%, rgba(255,255,255,0.15) 0%, transparent 50%);
  pointer-events: none;
}

.score-header {
  text-align: center;
  margin-bottom: 32px;
  position: relative;
}

.result-icon { font-size: 48px; margin-bottom: 12px; }

.score-header h1 {
  font-size: 26px;
  font-weight: 700;
  margin-bottom: 6px;
}

.score-header p {
  font-size: 15px;
  opacity: 0.8;
}

.score-display {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  position: relative;
}

.score-block {
  text-align: center;
  background: rgba(255,255,255,0.15);
  border-radius: 12px;
  padding: 16px 24px;
  min-width: 100px;
  backdrop-filter: blur(10px);
}

.score-block.total {
  background: rgba(255,255,255,0.25);
}

.score-num {
  font-size: 36px;
  font-weight: 800;
  line-height: 1;
  margin-bottom: 6px;
}

.score-lbl {
  font-size: 13px;
  opacity: 0.8;
}

.score-plus, .score-equals {
  font-size: 24px;
  font-weight: 300;
  opacity: 0.7;
}

/* 详情卡片 */
.detail-cards {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-bottom: 24px;
}

.info-card {
  background: #fff;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
}

.card-title {
  font-size: 14px;
  font-weight: 600;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 16px;
}

.warning-title { color: #f97316; }
.success-title { color: #22c55e; }

.info-row {
  display: flex;
  padding: 10px 0;
  border-bottom: 1px solid #f1f5f9;
  font-size: 15px;
}

.info-row:last-child { border-bottom: none; }

.info-key {
  color: #64748b;
  width: 100px;
  flex-shrink: 0;
}

.info-val {
  color: #1e293b;
  font-weight: 500;
}

/* 违规卡片 */
.violation-card { border: 1px solid #fed7aa; background: #fff7ed; }

.violation-detail {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.violation-icon { font-size: 24px; flex-shrink: 0; }

.violation-detail p { font-size: 15px; color: #92400e; margin-bottom: 4px; }
.violation-detail strong { font-weight: 700; }
.violation-tip { font-size: 13px; color: #b45309; }

/* 评语卡片 */
.comment-card { border: 1px solid #bbf7d0; background: #f0fdf4; }

.comment-text {
  font-size: 15px;
  line-height: 1.75;
  color: #166534;
}

/* 状态提示 */
.status-notice {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  padding: 20px;
  border-radius: 12px;
  margin-bottom: 24px;
  font-size: 14px;
}

.status-notice.pending {
  background: #fffbeb;
  border: 1px solid #fde68a;
  color: #92400e;
}

.status-notice.graded {
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  color: #166534;
}

.notice-icon { font-size: 22px; flex-shrink: 0; }

.notice-title {
  font-weight: 600;
  margin-bottom: 4px;
  font-size: 15px;
}

/* 操作按钮 */
.result-actions { text-align: center; }

.btn-home {
  padding: 12px 40px;
  background: linear-gradient(135deg, #4f6ef7 0%, #7c3aed 100%);
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(79, 110, 247, 0.3);
  transition: all 0.2s;
}

.btn-home:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 18px rgba(79, 110, 247, 0.4);
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: 80px 20px;
}

.empty-icon { font-size: 52px; margin-bottom: 16px; }
.empty-state p { font-size: 16px; color: #64748b; margin-bottom: 24px; }
</style>
