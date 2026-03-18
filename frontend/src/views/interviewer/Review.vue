<template>
  <div class="review-page">
    <!-- 顶部导航 -->
    <header class="top-header">
      <div class="header-brand">
        <span class="brand-icon">📋</span>
        <span class="brand-name">面试考试系统</span>
        <span class="role-badge">面试官</span>
      </div>
      <div class="header-right">
        <button v-if="selectedPaper" class="btn-back" @click="selectedPaper = null">
          ← 返回列表
        </button>
        <button v-else class="btn-back" @click="$router.push('/interviewer')">
          ← 返回首页
        </button>
      </div>
    </header>

    <div class="page-content">
      <!-- ===== 待批阅列表 ===== -->
      <template v-if="!selectedPaper">
        <div class="page-title-row">
          <h2>试卷批阅</h2>
          <span class="count-badge">{{ pendingPapers.length }} 份待批阅</span>
        </div>

        <!-- 空状态 -->
        <div v-if="!pendingPapers.length" class="empty-state">
          <div class="empty-icon">🎉</div>
          <p>所有试卷均已批阅完毕！</p>
        </div>

        <!-- 列表 -->
        <div v-else class="paper-list">
          <div v-for="paper in pendingPapers" :key="paper.id" class="paper-row">
            <div class="paper-info">
              <div class="paper-avatar">{{ paper.candidate_name?.[0] || '?' }}</div>
              <div class="paper-meta">
                <div class="paper-name">{{ paper.candidate_name }}</div>
                <div class="paper-sub">{{ paper.position || '未填写岗位' }}</div>
              </div>
            </div>
            <div class="paper-stats">
              <div class="stat-item">
                <span class="stat-l">客观题</span>
                <span class="stat-v score">{{ paper.objective_score }}</span>
              </div>
              <div class="stat-item" v-if="paper.screen_focus_loss_count > 0">
                <span class="stat-l">切屏</span>
                <span class="stat-v warn">⚠️ {{ paper.screen_focus_loss_count }}次</span>
              </div>
              <div class="stat-item">
                <span class="stat-l">交卷时间</span>
                <span class="stat-v muted">{{ formatTime(paper.end_time) }}</span>
              </div>
            </div>
            <button class="btn-grade" @click="selectPaper(paper)">开始批阅</button>
          </div>
        </div>
      </template>

      <!-- ===== 批阅界面 ===== -->
      <template v-else>
        <!-- 考生信息面板 -->
        <div class="candidate-panel">
          <div class="candidate-avatar">{{ selectedPaper.candidate_name?.[0] }}</div>
          <div class="candidate-detail">
            <h3>{{ selectedPaper.candidate_name }}</h3>
            <p>{{ selectedPaper.position || '未填写岗位' }} · 考试时间：{{ formatTime(selectedPaper.start_time) }}</p>
          </div>
          <div class="candidate-scores">
            <div class="score-pill">
              <span>客观题</span>
              <strong>{{ selectedPaper.objective_score }}</strong>
            </div>
            <div v-if="selectedPaper.screen_focus_loss_count > 0" class="score-pill warn">
              <span>切屏次数</span>
              <strong>{{ selectedPaper.screen_focus_loss_count }}</strong>
            </div>
          </div>
        </div>

        <!-- 主观题批阅区 -->
        <div class="grading-area">
          <div v-if="!essayQuestions.length" class="no-essay">
            <p>本试卷无主观题，直接填写总体评价后提交即可。</p>
          </div>

          <div v-for="(item, idx) in essayQuestions" :key="item.answer_id" class="essay-card">
            <div class="essay-card-header">
              <span class="essay-num">{{ item.question_type === 'programming' ? '编程/设计题' : '简答题' }} {{ idx + 1 }}</span>
              <span class="essay-score-info">满分 {{ item.max_score }} 分</span>
            </div>

            <div class="question-text">{{ item.question_text }}</div>

            <div class="answer-block">
              <div class="answer-block-title">考生答案</div>
              <div class="answer-content" :class="{ empty: !item.answer_content }">
                {{ item.answer_content || '考生未作答' }}
              </div>
            </div>

            <div class="grading-row">
              <div class="grade-field">
                <label>得分</label>
                <div class="score-input-wrap">
                  <input
                    type="number"
                    v-model.number="item.score"
                    :max="item.max_score"
                    min="0"
                    class="score-input"
                    :placeholder="`0 ~ ${item.max_score}`"
                  />
                  <span class="score-max">/ {{ item.max_score }}</span>
                </div>
              </div>
              <div class="grade-field flex-1">
                <label>批注（可选）</label>
                <input
                  type="text"
                  v-model="item.comment"
                  class="comment-input"
                  placeholder="请输入批注..."
                />
              </div>
            </div>
          </div>
        </div>

        <!-- 总体评价 + 提交 -->
        <div class="overall-card">
          <h4>总体评价</h4>
          <textarea
            v-model="graderComment"
            class="overall-textarea"
            rows="4"
            placeholder="请输入对本次考生表现的总体评价..."
          ></textarea>

          <div class="final-score-bar">
            <div class="final-score-breakdown">
              客观题 <strong>{{ selectedPaper.objective_score }}</strong>
              <span class="sep">+</span>
              主观题 <strong>{{ subjectiveScore }}</strong>
              <span class="sep">=</span>
              <span class="total-label">总分</span>
            </div>
            <div class="total-num">{{ totalScore }}</div>
          </div>

          <button class="btn-submit-grade" @click="submitGrade" :disabled="submitting">
            {{ submitting ? '提交中...' : '提交批阅' }}
          </button>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '@/api'

const pendingPapers = ref([])
const selectedPaper = ref(null)
const essayQuestions = ref([])
const graderComment = ref('')
const submitting = ref(false)

const subjectiveScore = computed(() =>
  essayQuestions.value.reduce((sum, q) => sum + (q.score || 0), 0)
)

const totalScore = computed(() =>
  (selectedPaper.value?.objective_score || 0) + subjectiveScore.value
)

onMounted(() => loadPendingPapers())

async function loadPendingPapers() {
  try {
    pendingPapers.value = await api.get('/review/pending')
  } catch (err) {
    console.error('加载待批阅列表失败:', err)
  }
}

async function selectPaper(paper) {
  selectedPaper.value = paper
  graderComment.value = ''
  essayQuestions.value = paper.answers?.filter(a => a.question_type === 'essay' || a.question_type === 'programming').map(a => ({
    answer_id: a.id,
    question_id: a.question_id,
    question_type: a.question_type,
    question_text: a.question_text || (a.question_type === 'programming' ? '编程/设计题' : '简答题'),
    max_score: a.max_score || 10,
    answer_content: a.answer_content,
    score: a.score || 0,
    comment: a.grader_comment || ''
  })) || []
}

async function submitGrade() {
  if (!confirm('确定提交批阅？提交后不可修改。')) return
  submitting.value = true
  try {
    await api.post('/review/grade', {
      paper_id: selectedPaper.value.id,
      subjective_scores: essayQuestions.value.map(q => ({
        answer_id: q.answer_id,
        score: q.score || 0,
        comment: q.comment || ''
      })),
      grader_comment: graderComment.value
    })
    selectedPaper.value = null
    loadPendingPapers()
  } catch (err) {
    alert('提交失败：' + (err.response?.data?.error || '未知错误'))
  } finally {
    submitting.value = false
  }
}

function formatTime(dateStr) {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}
</script>

<style scoped>
.review-page {
  min-height: 100vh;
  background: #f0f2f5;
  display: flex;
  flex-direction: column;
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
  background: #eff6ff;
  color: #3b82f6;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

.btn-back {
  padding: 7px 16px;
  background: #f1f5f9;
  border: none;
  border-radius: 8px;
  font-size: 13px;
  color: #64748b;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-back:hover { background: #e2e8f0; color: #1e293b; }

/* 主内容 */
.page-content {
  flex: 1;
  max-width: 960px;
  width: 100%;
  margin: 0 auto;
  padding: 28px 24px;
}

.page-title-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 24px;
}

.page-title-row h2 {
  font-size: 20px;
  font-weight: 700;
  color: #1e293b;
}

.count-badge {
  padding: 4px 12px;
  background: #fef2f2;
  color: #ef4444;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 500;
}

/* 空状态 */
.empty-state { text-align: center; padding: 80px 20px; }
.empty-icon { font-size: 52px; margin-bottom: 16px; }
.empty-state p { font-size: 16px; color: #94a3b8; }

/* 待批阅列表 */
.paper-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.paper-row {
  background: #fff;
  border-radius: 12px;
  padding: 20px 24px;
  display: flex;
  align-items: center;
  gap: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  transition: box-shadow 0.2s;
  flex-wrap: wrap;
}

.paper-row:hover { box-shadow: 0 4px 16px rgba(0,0,0,0.1); }

.paper-info { display: flex; align-items: center; gap: 14px; min-width: 200px; }

.paper-avatar {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: linear-gradient(135deg, #4f6ef7, #7c3aed);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  font-weight: 700;
  flex-shrink: 0;
}

.paper-name { font-size: 15px; font-weight: 600; color: #1e293b; margin-bottom: 2px; }
.paper-sub { font-size: 13px; color: #94a3b8; }

.paper-stats {
  flex: 1;
  display: flex;
  gap: 24px;
  flex-wrap: wrap;
}

.stat-item { display: flex; flex-direction: column; gap: 2px; }
.stat-l { font-size: 12px; color: #94a3b8; }
.stat-v { font-size: 14px; font-weight: 500; color: #374151; }
.stat-v.score { color: #22c55e; }
.stat-v.warn { color: #ef4444; }
.stat-v.muted { color: #94a3b8; font-size: 13px; }

.btn-grade {
  padding: 9px 24px;
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

.btn-grade:hover { background: #3a56e0; }

/* 考生信息面板 */
.candidate-panel {
  background: linear-gradient(135deg, #4f6ef7 0%, #7c3aed 100%);
  border-radius: 14px;
  padding: 24px 28px;
  display: flex;
  align-items: center;
  gap: 20px;
  color: #fff;
  margin-bottom: 24px;
  flex-wrap: wrap;
}

.candidate-avatar {
  width: 52px;
  height: 52px;
  border-radius: 50%;
  background: rgba(255,255,255,0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  font-weight: 700;
  flex-shrink: 0;
}

.candidate-detail { flex: 1; }
.candidate-detail h3 { font-size: 18px; font-weight: 700; margin-bottom: 4px; }
.candidate-detail p { font-size: 13px; opacity: 0.8; }

.candidate-scores { display: flex; gap: 12px; }

.score-pill {
  padding: 8px 16px;
  background: rgba(255,255,255,0.15);
  border-radius: 8px;
  text-align: center;
}

.score-pill span { display: block; font-size: 12px; opacity: 0.8; margin-bottom: 2px; }
.score-pill strong { font-size: 20px; font-weight: 800; }
.score-pill.warn { background: rgba(239,68,68,0.3); }

/* 简答题批阅 */
.grading-area { display: flex; flex-direction: column; gap: 20px; margin-bottom: 20px; }

.no-essay {
  background: #fff;
  border-radius: 12px;
  padding: 32px;
  text-align: center;
  color: #94a3b8;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}

.essay-card {
  background: #fff;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}

.essay-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
  padding-bottom: 14px;
  border-bottom: 1px solid #f1f5f9;
}

.essay-num { font-size: 15px; font-weight: 600; color: #1e293b; }
.essay-score-info { font-size: 13px; color: #f97316; font-weight: 500; }

.question-text {
  font-size: 15px;
  line-height: 1.7;
  color: #1e293b;
  margin-bottom: 16px;
}

.answer-block { margin-bottom: 20px; }

.answer-block-title {
  font-size: 12px;
  font-weight: 600;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 8px;
}

.answer-content {
  padding: 14px 16px;
  background: #f8fafc;
  border-radius: 8px;
  font-size: 14px;
  line-height: 1.7;
  color: #374151;
  min-height: 80px;
  border: 1px solid #e2e8f0;
}

.answer-content.empty { color: #94a3b8; font-style: italic; }

.grading-row {
  display: flex;
  gap: 16px;
  padding-top: 16px;
  border-top: 1px solid #f1f5f9;
  flex-wrap: wrap;
}

.grade-field { display: flex; flex-direction: column; gap: 6px; }
.grade-field.flex-1 { flex: 1; min-width: 200px; }

.grade-field label { font-size: 13px; font-weight: 500; color: #64748b; }

.score-input-wrap {
  display: flex;
  align-items: center;
  gap: 8px;
}

.score-input {
  width: 90px;
  padding: 8px 12px;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 700;
  text-align: center;
  outline: none;
  color: #4f6ef7;
  transition: border-color 0.2s;
}

.score-input:focus { border-color: #4f6ef7; }
.score-max { font-size: 14px; color: #94a3b8; }

.comment-input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 14px;
  outline: none;
  transition: border-color 0.2s;
}

.comment-input:focus { border-color: #4f6ef7; }

/* 总体评价 */
.overall-card {
  background: #fff;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}

.overall-card h4 {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 12px;
}

.overall-textarea {
  width: 100%;
  padding: 12px 14px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 14px;
  font-family: inherit;
  line-height: 1.6;
  resize: vertical;
  outline: none;
  transition: border-color 0.2s;
  margin-bottom: 20px;
}

.overall-textarea:focus { border-color: #4f6ef7; }

.final-score-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  background: #f8fafc;
  border-radius: 10px;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 12px;
}

.final-score-breakdown {
  font-size: 15px;
  color: #64748b;
  display: flex;
  align-items: center;
  gap: 8px;
}

.final-score-breakdown strong { color: #1e293b; font-size: 17px; }
.sep { color: #cbd5e1; }
.total-label { color: #4f6ef7; font-weight: 600; }

.total-num {
  font-size: 40px;
  font-weight: 900;
  color: #4f6ef7;
  line-height: 1;
}

.btn-submit-grade {
  width: 100%;
  padding: 14px;
  background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
  color: #fff;
  border: none;
  border-radius: 10px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(34,197,94,0.3);
  transition: all 0.2s;
}

.btn-submit-grade:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 6px 16px rgba(34,197,94,0.4);
}

.btn-submit-grade:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
