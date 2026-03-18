<template>
  <div class="exam-page">
    <!-- 顶部固定导航栏 -->
    <header class="exam-topbar">
      <div class="topbar-inner">
        <div class="topbar-left">
          <span class="exam-logo">📋</span>
          <div class="candidate-meta">
            <span class="candidate-name">{{ candidateName }}</span>
            <span class="candidate-pos">{{ position }}</span>
          </div>
        </div>
        <div class="topbar-center">
          <div class="progress-bar-wrap">
            <div class="progress-bar" :style="{ width: progressPercent + '%' }"></div>
          </div>
          <span class="progress-text">已作答 {{ answeredCount }} / {{ questions.length }} 题</span>
        </div>
        <div class="topbar-right">
          <div class="timer-box" :class="{ urgent: timeLeft < 300 }">
            <span class="timer-icon">⏱</span>
            <span class="timer-val">{{ formatTime(timeLeft) }}</span>
          </div>
        </div>
      </div>
    </header>

    <!-- 主体内容 -->
    <main class="exam-main">
      <!-- 左侧答题卡 -->
      <aside class="answer-card-panel">
        <div class="panel-title">答题卡</div>
        <div class="answer-grid">
          <div
            v-for="(q, i) in questions"
            :key="q.id"
            class="answer-dot"
            :class="{ answered: hasAnswer(q.id), current: currentIndex === i }"
            @click="scrollToQuestion(i)"
          >{{ i + 1 }}</div>
        </div>
        <div class="card-legend">
          <span class="dot answered"></span> 已答
          <span class="dot" style="margin-left:12px"></span> 未答
        </div>
      </aside>

      <!-- 右侧题目区 -->
      <section class="questions-section">
        <div
          v-for="(question, index) in questions"
          :key="question.id"
          :id="`q-${index}`"
          class="question-block"
        >
          <div class="q-meta">
            <span class="q-num">第 {{ index + 1 }} 题</span>
            <span class="q-type-tag" :class="question.question_type">
              {{ getQuestionTypeText(question.question_type) }}
            </span>
            <span class="q-score-tag">{{ question.max_score }} 分</span>
          </div>
          <div class="q-text">{{ question.question_text }}</div>

          <!-- 选择题 -->
          <div v-if="question.question_type === 'single' || question.question_type === 'multiple'" class="option-list">
            <div
              v-for="(option, optIndex) in question.options"
              :key="optIndex"
              class="option-row"
              :class="{
                selected: isOptionSelected(question.id, getOptionKey(optIndex)),
                disabled: submitted
              }"
              @click="selectOption(question.id, getOptionKey(optIndex), question.question_type)"
            >
              <span class="opt-key" :class="{ selected: isOptionSelected(question.id, getOptionKey(optIndex)) }">
                {{ getOptionKey(optIndex) }}
              </span>
              <span class="opt-text">{{ option.substring(3) }}</span>
            </div>
          </div>

          <!-- 简答题 / 编程设计题 -->
          <div v-else class="essay-wrap">
            <textarea
              v-model="answers[question.id]"
              class="essay-input"
              :placeholder="question.question_type === 'programming' ? '请在此输入您的代码或设计思路...' : '请在此输入您的答案...'"
              :rows="question.question_type === 'programming' ? 12 : 8"
              @input="saveAnswersToLocal"
              :disabled="submitted"
            ></textarea>
            <div class="essay-hint">已输入 {{ (answers[question.id] || '').length }} 字</div>
          </div>
        </div>

        <!-- 底部提交区 -->
        <div class="submit-zone">
          <div class="submit-stats">
            <span>共 {{ questions.length }} 题 · 已答 <strong>{{ answeredCount }}</strong> 题 · 未答 {{ questions.length - answeredCount }} 题</span>
          </div>
          <button class="btn-submit" @click="showSubmitConfirm = true" :disabled="submitted">
            确认交卷
          </button>
        </div>
      </section>
    </main>

    <!-- 交卷确认弹窗 -->
    <div v-if="showSubmitConfirm" class="modal-overlay" @click.self="showSubmitConfirm = false">
      <div class="modal-box">
        <div class="modal-icon">📝</div>
        <h3>确认交卷？</h3>
        <p>还有 <strong>{{ questions.length - answeredCount }}</strong> 题未作答，交卷后无法修改。</p>
        <div class="modal-actions">
          <button class="btn-cancel" @click="showSubmitConfirm = false">继续答题</button>
          <button class="btn-confirm" @click="submitExam" :disabled="submitting">
            {{ submitting ? '提交中...' : '确认交卷' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 切屏警告弹窗 -->
    <div v-if="showWarning" class="modal-overlay">
      <div class="modal-box warning-box">
        <div class="modal-icon">⚠️</div>
        <h3>警告</h3>
        <p>{{ warningMessage }}</p>
        <div class="violation-count">
          切屏次数：<span>{{ focusLossCount }}</span> / 3
        </div>
        <div class="modal-actions">
          <button class="btn-confirm" @click="closeWarning">我知道了</button>
        </div>
      </div>
    </div>

    <!-- 强制交卷弹窗 -->
    <div v-if="forcedSubmit" class="modal-overlay">
      <div class="modal-box forced-box">
        <div class="modal-icon">❌</div>
        <h3>考试结束</h3>
        <p>您已多次离开考试页面，系统已强制交卷。</p>
        <div class="violation-count danger">切屏次数：<span>{{ focusLossCount }}</span> 次</div>
        <div class="modal-actions">
          <button class="btn-confirm" @click="viewResult">查看成绩</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/api'

const router = useRouter()
const paperId = router.currentRoute.value.params.paperId

const candidateName = ref('')
const position = ref('')
const questions = ref([])
const answers = ref({})
const startTime = ref(null)
const durationMinutes = ref(60)
const timeLeft = ref(0)
const timerInterval = ref(null)
const submitted = ref(false)
const submitting = ref(false)
const showSubmitConfirm = ref(false)
const currentIndex = ref(0)

// 防作弊
const focusLossCount = ref(0)
const showWarning = ref(false)
const warningMessage = ref('')
const forcedSubmit = ref(false)

const answeredCount = computed(() => Object.keys(answers.value).filter(k => {
  const v = answers.value[k]
  return v !== null && v !== undefined && v !== '' && !(Array.isArray(v) && v.length === 0)
}).length)

const progressPercent = computed(() => {
  if (!questions.value.length) return 0
  return Math.round((answeredCount.value / questions.value.length) * 100)
})

function hasAnswer(questionId) {
  const v = answers.value[questionId]
  return v !== null && v !== undefined && v !== '' && !(Array.isArray(v) && v.length === 0)
}

function getQuestionTypeText(type) {
  return { single: '单选题', multiple: '多选题', essay: '简答题', programming: '编程/设计题' }[type] || type
}

function getOptionKey(index) {
  return String.fromCharCode(65 + index)
}

function isOptionSelected(questionId, optionKey) {
  const answer = answers.value[questionId]
  if (!answer) return false
  return Array.isArray(answer) ? answer.includes(optionKey) : answer === optionKey
}

function selectOption(questionId, optionKey, type) {
  if (submitted.value) return
  if (type === 'single') {
    answers.value[questionId] = optionKey
  } else if (type === 'multiple') {
    if (!answers.value[questionId]) answers.value[questionId] = []
    const current = [...answers.value[questionId]]
    const idx = current.indexOf(optionKey)
    if (idx > -1) current.splice(idx, 1)
    else current.push(optionKey)
    answers.value[questionId] = current
  }
  saveAnswersToLocal()
}

function saveAnswersToLocal() {
  localStorage.setItem(`exam_answers_${paperId}`, JSON.stringify(answers.value))
}

function loadAnswersFromLocal() {
  const saved = localStorage.getItem(`exam_answers_${paperId}`)
  if (saved) answers.value = JSON.parse(saved)
}

function formatTime(seconds) {
  const m = Math.floor(seconds / 60)
  const s = seconds % 60
  return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`
}

function scrollToQuestion(index) {
  currentIndex.value = index
  const el = document.getElementById(`q-${index}`)
  if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' })
}

async function submitExam() {
  submitting.value = true
  try {
    const formattedAnswers = questions.value.map(q => ({
      question_id: q.id,
      answer_content: answers.value[q.id] || null
    }))
    await api.post('/exam/submit', {
      paper_id: paperId,
      answers: formattedAnswers,
      screen_focus_loss_count: focusLossCount.value
    })
    submitted.value = true
    showSubmitConfirm.value = false
    clearInterval(timerInterval.value)
    localStorage.removeItem(`exam_answers_${paperId}`)
    router.push(`/exam/result/${paperId}`)
  } catch (err) {
    alert('提交失败：' + (err.response?.data?.error || '未知错误'))
  } finally {
    submitting.value = false
  }
}

function viewResult() {
  router.push(`/exam/result/${paperId}`)
}

function closeWarning() {
  showWarning.value = false
}

function handleBlur() {
  if (submitted.value || forcedSubmit.value) return
  focusLossCount.value++
  if (focusLossCount.value >= 3) {
    forcedSubmit.value = true
    submitExam()
  } else if (focusLossCount.value === 1) {
    warningMessage.value = '检测到您切换了页面，这是第一次警告！请专心答题。'
    showWarning.value = true
  } else {
    warningMessage.value = '严重警告！这是第二次切屏，再有一次将被强制交卷！'
    showWarning.value = true
  }
  api.post('/exam/focus-loss', { paper_id: paperId }).catch(console.error)
}

function disableContextMenu(e) { e.preventDefault() }
function disableCopyPaste(e) {
  if (e.ctrlKey && ['c', 'v'].includes(e.key)) e.preventDefault()
}

const visibilityHandler = () => {
  if (document.visibilityState === 'hidden') handleBlur()
}

onMounted(async () => {
  document.addEventListener('contextmenu', disableContextMenu)
  document.addEventListener('keydown', disableCopyPaste)
  window.addEventListener('blur', handleBlur)
  document.addEventListener('visibilitychange', visibilityHandler)

  try {
    const data = await api.get(`/exam/paper/${paperId}`)
    questions.value = data.questions
    startTime.value = new Date(data.start_time)

    // 从候选人信息中读取姓名职位
    const candidate = data.candidate || {}
    candidateName.value = candidate.name || data.candidate_name || '候选人'
    position.value = candidate.position || data.position || ''
    if (data.duration_minutes) durationMinutes.value = data.duration_minutes

    loadAnswersFromLocal()

    const elapsed = Math.floor((new Date() - startTime.value) / 1000)
    // 优先使用服务器计算的剩余秒数，避免时区差异
    if (data.remaining_seconds !== undefined) {
      timeLeft.value = data.remaining_seconds
    } else {
      timeLeft.value = Math.max(0, durationMinutes.value * 60 - elapsed)
    }

    timerInterval.value = setInterval(() => {
      timeLeft.value--
      if (timeLeft.value <= 0) {
        clearInterval(timerInterval.value)
        if (!submitted.value) submitExam()
      }
    }, 1000)
  } catch (err) {
    alert('获取试卷失败：' + (err.response?.data?.error || '未知错误'))
    router.push('/exam')
  }
})

onUnmounted(() => {
  document.removeEventListener('contextmenu', disableContextMenu)
  document.removeEventListener('keydown', disableCopyPaste)
  window.removeEventListener('blur', handleBlur)
  document.removeEventListener('visibilitychange', visibilityHandler)
  if (timerInterval.value) clearInterval(timerInterval.value)
})
</script>

<style scoped>
.exam-page {
  min-height: 100vh;
  background: #f0f2f5;
  display: flex;
  flex-direction: column;
}

/* ===== 顶栏 ===== */
.exam-topbar {
  position: sticky;
  top: 0;
  z-index: 200;
  background: linear-gradient(135deg, #4f6ef7 0%, #7c3aed 100%);
  box-shadow: 0 2px 12px rgba(79, 110, 247, 0.3);
}

.topbar-inner {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 24px;
  height: 60px;
  display: flex;
  align-items: center;
  gap: 24px;
}

.topbar-left {
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 200px;
}

.exam-logo { font-size: 24px; }

.candidate-meta {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.candidate-name {
  color: #fff;
  font-weight: 600;
  font-size: 15px;
  line-height: 1;
}

.candidate-pos {
  color: rgba(255,255,255,0.7);
  font-size: 12px;
}

.topbar-center {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.progress-bar-wrap {
  width: 100%;
  height: 6px;
  background: rgba(255,255,255,0.2);
  border-radius: 3px;
  overflow: hidden;
}

.progress-bar {
  height: 100%;
  background: #4ade80;
  border-radius: 3px;
  transition: width 0.3s;
}

.progress-text {
  color: rgba(255,255,255,0.85);
  font-size: 12px;
  text-align: center;
}

.topbar-right { min-width: 120px; display: flex; justify-content: flex-end; }

.timer-box {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  background: rgba(255,255,255,0.15);
  border-radius: 8px;
  color: #fff;
}

.timer-box.urgent {
  background: #ef4444;
  animation: pulse 1s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.75; }
}

.timer-icon { font-size: 16px; }

.timer-val {
  font-size: 18px;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
  letter-spacing: 1px;
}

/* ===== 主体 ===== */
.exam-main {
  flex: 1;
  display: flex;
  max-width: 1400px;
  width: 100%;
  margin: 24px auto;
  padding: 0 24px;
  gap: 24px;
  align-items: flex-start;
}

/* ===== 答题卡 ===== */
.answer-card-panel {
  position: sticky;
  top: 84px;
  width: 200px;
  flex-shrink: 0;
  background: #fff;
  border-radius: 12px;
  padding: 20px 16px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.07);
}

.panel-title {
  font-size: 13px;
  font-weight: 600;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 16px;
}

.answer-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 8px;
}

.answer-dot {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  border: 1.5px solid #e2e8f0;
  color: #64748b;
  transition: all 0.2s;
}

.answer-dot:hover {
  border-color: #4f6ef7;
  color: #4f6ef7;
}

.answer-dot.answered {
  background: #4f6ef7;
  border-color: #4f6ef7;
  color: #fff;
}

.answer-dot.current {
  box-shadow: 0 0 0 2px #4f6ef7;
}

.card-legend {
  margin-top: 16px;
  font-size: 12px;
  color: #94a3b8;
  display: flex;
  align-items: center;
  gap: 4px;
}

.dot {
  width: 12px;
  height: 12px;
  border-radius: 3px;
  border: 1.5px solid #e2e8f0;
  display: inline-block;
}

.dot.answered {
  background: #4f6ef7;
  border-color: #4f6ef7;
}

/* ===== 题目区 ===== */
.questions-section {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.question-block {
  background: #fff;
  border-radius: 12px;
  padding: 28px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
  scroll-margin-top: 84px;
}

.q-meta {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;
  padding-bottom: 14px;
  border-bottom: 1px solid #f1f5f9;
}

.q-num {
  font-size: 15px;
  font-weight: 600;
  color: #1e293b;
}

.q-type-tag {
  padding: 3px 10px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

.q-type-tag.single { background: #eff6ff; color: #3b82f6; }
.q-type-tag.multiple { background: #f0fdf4; color: #22c55e; }
.q-type-tag.essay { background: #fff7ed; color: #f97316; }
.q-type-tag.programming { background: #faf5ff; color: #7c3aed; }

.q-score-tag {
  margin-left: auto;
  font-size: 13px;
  color: #ef4444;
  font-weight: 600;
}

.q-text {
  font-size: 16px;
  line-height: 1.75;
  color: #1e293b;
  margin-bottom: 20px;
}

/* 选项 */
.option-list { display: flex; flex-direction: column; gap: 10px; }

.option-row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border-radius: 8px;
  border: 2px solid #e2e8f0;
  cursor: pointer;
  transition: all 0.2s;
  user-select: none;
}

.option-row:hover:not(.disabled) {
  border-color: #4f6ef7;
  background: #eff6ff;
}

.option-row.selected {
  border-color: #4f6ef7;
  background: #eef1fe;
}

.option-row.disabled { cursor: not-allowed; opacity: 0.7; }

.opt-key {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 600;
  flex-shrink: 0;
  background: #f1f5f9;
  color: #64748b;
  border: 2px solid #e2e8f0;
  transition: all 0.2s;
}

.opt-key.selected {
  background: #4f6ef7;
  color: #fff;
  border-color: #4f6ef7;
}

.opt-text {
  font-size: 15px;
  line-height: 1.5;
  color: #374151;
}

/* 简答题 */
.essay-wrap { position: relative; }

.essay-input {
  width: 100%;
  padding: 14px;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  font-size: 15px;
  line-height: 1.6;
  font-family: inherit;
  resize: vertical;
  transition: border-color 0.2s;
  outline: none;
  color: #1e293b;
  background: #fafcff;
}

.essay-input:focus {
  border-color: #4f6ef7;
  background: #fff;
}

.essay-hint {
  font-size: 12px;
  color: #94a3b8;
  text-align: right;
  margin-top: 6px;
}

/* 提交区 */
.submit-zone {
  background: #fff;
  border-radius: 12px;
  padding: 28px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.submit-stats {
  font-size: 15px;
  color: #64748b;
}

.submit-stats strong { color: #4f6ef7; }

.btn-submit {
  padding: 12px 40px;
  background: linear-gradient(135deg, #4f6ef7 0%, #7c3aed 100%);
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 4px 12px rgba(79, 110, 247, 0.3);
}

.btn-submit:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 6px 18px rgba(79, 110, 247, 0.4);
}

.btn-submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* ===== 弹窗 ===== */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
}

.modal-box {
  background: #fff;
  border-radius: 16px;
  padding: 36px 40px;
  max-width: 420px;
  width: 90%;
  text-align: center;
  box-shadow: 0 20px 60px rgba(0,0,0,0.2);
}

.modal-icon { font-size: 44px; margin-bottom: 16px; }

.modal-box h3 {
  font-size: 20px;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 12px;
}

.modal-box p {
  font-size: 15px;
  color: #64748b;
  line-height: 1.6;
  margin-bottom: 8px;
}

.modal-box strong { color: #1e293b; }

.violation-count {
  margin: 16px 0;
  padding: 10px 16px;
  background: #fff7ed;
  border-radius: 8px;
  font-size: 14px;
  color: #f97316;
}

.violation-count span { font-weight: 700; font-size: 18px; }

.violation-count.danger {
  background: #fef2f2;
  color: #ef4444;
}

.modal-actions {
  margin-top: 24px;
  display: flex;
  gap: 12px;
  justify-content: center;
}

.btn-cancel {
  padding: 10px 28px;
  background: #f1f5f9;
  color: #64748b;
  border: none;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-cancel:hover { background: #e2e8f0; }

.btn-confirm {
  padding: 10px 28px;
  background: linear-gradient(135deg, #4f6ef7 0%, #7c3aed 100%);
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-confirm:hover:not(:disabled) { opacity: 0.9; }
.btn-confirm:disabled { opacity: 0.6; cursor: not-allowed; }

.warning-box .btn-confirm { background: linear-gradient(135deg, #f97316 0%, #ef4444 100%); }
.forced-box .btn-confirm { background: #ef4444; }
</style>
