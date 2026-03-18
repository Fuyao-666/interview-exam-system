<template>
  <div class="questions-page">
    <!-- 顶部导航 -->
    <header class="top-header">
      <div class="header-brand">
        <span class="brand-icon">📋</span>
        <span class="brand-name">面试考试系统</span>
        <span class="role-badge">面试官</span>
      </div>
      <div class="header-user">
        <button class="btn-back" @click="$router.push('/interviewer')">← 返回首页</button>
      </div>
    </header>

    <!-- 主内容 -->
    <div class="page-content">
      <!-- 工具栏 -->
      <div class="toolbar">
        <div class="toolbar-left">
          <h2>题库管理</h2>
          <div class="type-filters">
            <button
              v-for="t in typeOptions"
              :key="t.value"
              class="filter-btn"
              :class="{ active: filterType === t.value }"
              @click="filterType = t.value; loadQuestions()"
            >{{ t.label }}</button>
          </div>
        </div>
        <button class="btn-create" @click="openCreate">
          + 新建题目
        </button>
      </div>

      <!-- 题目列表 -->
      <div v-if="questions.length" class="question-list">
        <div v-for="(q, idx) in questions" :key="q.id" class="q-card">
          <div class="q-card-header">
            <div class="q-badges">
              <span class="type-badge" :class="q.question_type">
                {{ getTypeText(q.question_type) }}
              </span>
              <span class="score-badge">{{ q.max_score }} 分</span>
            </div>
            <span class="q-index">NO.{{ idx + 1 }}</span>
            <div class="q-actions">
              <button class="btn-edit" @click="editQuestion(q)">编辑</button>
              <button class="btn-delete" @click="deleteQuestion(q.id)">删除</button>
            </div>
          </div>

          <div class="q-text">{{ q.question_text }}</div>

          <div v-if="q.options && q.options.length" class="q-options">
            <div v-for="(opt, i) in q.options" :key="i" class="opt-row">
              <span class="opt-key">{{ String.fromCharCode(65 + i) }}</span>
              <span class="opt-text">{{ opt.substring(3) }}</span>
            </div>
          </div>

          <div v-if="q.answer" class="q-answer">
            <span class="answer-label">参考答案</span>
            <span class="answer-val">{{ formatAnswer(q.answer, q.question_type) }}</span>
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-else class="empty-state">
        <div class="empty-icon">📭</div>
        <p>暂无题目，点击右上角新建</p>
      </div>
    </div>

    <!-- 新建/编辑弹窗 -->
    <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal-box">
        <div class="modal-header">
          <h3>{{ editingQuestion ? '编辑题目' : '新建题目' }}</h3>
          <button class="modal-close" @click="closeModal">✕</button>
        </div>
        <form @submit.prevent="saveQuestion">
          <div class="form-group">
            <label>题型</label>
            <div class="type-radio-group">
              <label v-for="t in typeOptions.slice(1)" :key="t.value" class="type-radio">
                <input type="radio" :value="t.value" v-model="formData.question_type" />
                <span>{{ t.label }}</span>
              </label>
            </div>
          </div>

          <div class="form-group">
            <label>题干 <span class="required">*</span></label>
            <textarea
              v-model="formData.question_text"
              class="form-textarea"
              rows="4"
              placeholder="请输入题目内容..."
              required
            ></textarea>
          </div>

          <div v-if="formData.question_type === 'single' || formData.question_type === 'multiple'" class="form-group">
            <label>选项 <span class="hint">（每行一个，格式：A. 选项内容）</span></label>
            <textarea
              v-model="optionsText"
              class="form-textarea"
              rows="6"
              placeholder="A. 选项 1&#10;B. 选项 2&#10;C. 选项 3&#10;D. 选项 4"
            ></textarea>
          </div>

          <div v-if="formData.question_type === 'single'" class="form-group">
            <label>正确答案 <span class="required">*</span></label>
            <select v-model="formData.answer" class="form-select" required>
              <option value="">请选择</option>
              <option v-for="k in ['A','B','C','D','E']" :key="k" :value="k">{{ k }}</option>
            </select>
          </div>

          <div v-if="formData.question_type === 'multiple'" class="form-group">
            <label>正确答案（多选）</label>
            <div class="checkbox-row">
              <label v-for="k in ['A','B','C','D','E']" :key="k" class="checkbox-item">
                <input type="checkbox" :value="k" v-model="multipleAnswer" />
                <span>{{ k }}</span>
              </label>
            </div>
          </div>

          <div v-if="formData.question_type === 'essay' || formData.question_type === 'programming'" class="form-group">
            <label>分值</label>
            <input v-model.number="formData.max_score" class="form-input" type="number" min="1" required />
          </div>

          <div class="modal-footer">
            <button type="button" class="btn-cancel" @click="closeModal">取消</button>
            <button type="submit" class="btn-save">保存题目</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import api from '@/api'

const typeOptions = [
  { value: '', label: '全部' },
  { value: 'single', label: '单选题' },
  { value: 'multiple', label: '多选题' },
  { value: 'essay', label: '简答题' },
  { value: 'programming', label: '编程/设计题' }
]

const questions = ref([])
const filterType = ref('')
const showModal = ref(false)
const editingQuestion = ref(null)
const optionsText = ref('')
const multipleAnswer = ref([])

const formData = reactive({
  question_type: 'single',
  question_text: '',
  answer: '',
  max_score: 5
})

onMounted(() => loadQuestions())

async function loadQuestions() {
  try {
    const params = filterType.value ? `?type=${filterType.value}` : ''
    const data = await api.get(`/questions${params}`)
    questions.value = data.questions
  } catch (err) {
    console.error('加载题目失败:', err)
  }
}

function getTypeText(type) {
  return { single: '单选题', multiple: '多选题', essay: '简答题', programming: '编程/设计题' }[type] || type
}

function formatAnswer(answer, type) {
  if (!answer) return ''
  try {
    const parsed = typeof answer === 'string' ? JSON.parse(answer) : answer
    return type === 'multiple' && Array.isArray(parsed) ? parsed.join(', ') : parsed
  } catch {
    return answer
  }
}

function openCreate() {
  editingQuestion.value = null
  formData.question_type = 'single'
  formData.question_text = ''
  formData.answer = ''
  formData.max_score = 5
  optionsText.value = ''
  multipleAnswer.value = []
  showModal.value = true
}

function editQuestion(q) {
  editingQuestion.value = q
  formData.question_type = q.question_type
  formData.question_text = q.question_text
  formData.answer = typeof q.answer === 'string' ? q.answer : JSON.stringify(q.answer)
  formData.max_score = q.max_score
  optionsText.value = q.options ? q.options.join('\n') : ''
  if (q.question_type === 'multiple' && q.answer) {
    multipleAnswer.value = typeof q.answer === 'string' ? JSON.parse(q.answer) : q.answer
  }
  showModal.value = true
}

function deleteQuestion(id) {
  if (!confirm('确定要删除这道题吗？')) return
  api.delete(`/questions/${id}`)
    .then(() => loadQuestions())
    .catch(err => alert('删除失败：' + (err.response?.data?.error || '未知错误')))
}

function closeModal() {
  showModal.value = false
  editingQuestion.value = null
}

async function saveQuestion() {
  const payload = {
    question_type: formData.question_type,
    question_text: formData.question_text,
    max_score: formData.max_score
  }
  if ((formData.question_type === 'single' || formData.question_type === 'multiple') && optionsText.value) {
    payload.options = optionsText.value.split('\n').filter(l => l.trim())
  }
  if (formData.question_type === 'single') payload.answer = formData.answer
  else if (formData.question_type === 'multiple') payload.answer = multipleAnswer.value

  try {
    if (editingQuestion.value) {
      await api.put(`/questions/${editingQuestion.value.id}`, payload)
    } else {
      await api.post('/questions', payload)
    }
    closeModal()
    loadQuestions()
  } catch (err) {
    alert('保存失败：' + (err.response?.data?.error || '未知错误'))
  }
}
</script>

<style scoped>
.questions-page {
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
  max-width: 1000px;
  width: 100%;
  margin: 0 auto;
  padding: 28px 24px;
}

/* 工具栏 */
.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 12px;
}

.toolbar-left { display: flex; align-items: center; gap: 16px; flex-wrap: wrap; }

.toolbar-left h2 {
  font-size: 20px;
  font-weight: 700;
  color: #1e293b;
  white-space: nowrap;
}

.type-filters { display: flex; gap: 6px; }

.filter-btn {
  padding: 6px 16px;
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 20px;
  font-size: 13px;
  color: #64748b;
  cursor: pointer;
  transition: all 0.2s;
}

.filter-btn:hover { border-color: #4f6ef7; color: #4f6ef7; }
.filter-btn.active { background: #4f6ef7; border-color: #4f6ef7; color: #fff; }

.btn-create {
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

.btn-create:hover { background: #3a56e0; }

/* 题目列表 */
.question-list { display: flex; flex-direction: column; gap: 16px; }

.q-card {
  background: #fff;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.06);
  transition: box-shadow 0.2s;
}

.q-card:hover { box-shadow: 0 4px 16px rgba(0,0,0,0.1); }

.q-card-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;
  padding-bottom: 14px;
  border-bottom: 1px solid #f1f5f9;
}

.q-badges { display: flex; align-items: center; gap: 8px; }

.type-badge {
  padding: 3px 10px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

.type-badge.single { background: #eff6ff; color: #3b82f6; }
.type-badge.multiple { background: #f0fdf4; color: #22c55e; }
.type-badge.essay { background: #fff7ed; color: #f97316; }
.type-badge.programming { background: #faf5ff; color: #7c3aed; }

.score-badge {
  padding: 3px 10px;
  background: #fef2f2;
  color: #ef4444;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

.q-index { font-size: 12px; color: #cbd5e1; margin-left: auto; }

.q-actions { display: flex; gap: 8px; }

.btn-edit, .btn-delete {
  padding: 5px 14px;
  border: none;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: opacity 0.2s;
}

.btn-edit { background: #eff6ff; color: #3b82f6; }
.btn-edit:hover { background: #dbeafe; }
.btn-delete { background: #fef2f2; color: #ef4444; }
.btn-delete:hover { background: #fee2e2; }

.q-text {
  font-size: 16px;
  line-height: 1.7;
  color: #1e293b;
  margin-bottom: 16px;
}

.q-options {
  background: #f8fafc;
  border-radius: 8px;
  padding: 12px 16px;
  margin-bottom: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.opt-row { display: flex; align-items: center; gap: 10px; font-size: 14px; }

.opt-key {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: #e2e8f0;
  color: #64748b;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
  flex-shrink: 0;
}

.opt-text { color: #374151; }

.q-answer {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 14px;
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  border-radius: 8px;
  font-size: 13px;
}

.answer-label { color: #166534; font-weight: 600; }
.answer-val { color: #166534; }

/* 空状态 */
.empty-state {
  text-align: center;
  padding: 80px 20px;
}

.empty-icon { font-size: 52px; margin-bottom: 16px; }
.empty-state p { font-size: 16px; color: #94a3b8; }

/* 弹窗 */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
  padding: 20px;
}

.modal-box {
  background: #fff;
  border-radius: 16px;
  padding: 0;
  width: 100%;
  max-width: 580px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.2);
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 24px 28px 0;
  margin-bottom: 24px;
}

.modal-header h3 {
  font-size: 18px;
  font-weight: 700;
  color: #1e293b;
}

.modal-close {
  background: none;
  border: none;
  font-size: 18px;
  color: #94a3b8;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 6px;
  transition: all 0.2s;
}

.modal-close:hover { background: #f1f5f9; color: #1e293b; }

.modal-box form { padding: 0 28px 28px; }

.form-group { margin-bottom: 18px; }

.form-group label {
  display: block;
  font-size: 13px;
  font-weight: 600;
  color: #374151;
  margin-bottom: 8px;
}

.required { color: #ef4444; }
.hint { color: #94a3b8; font-weight: 400; font-size: 12px; }

.type-radio-group { display: flex; gap: 12px; }

.type-radio {
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  font-size: 14px;
  color: #374151;
}

.form-textarea, .form-select, .form-input {
  width: 100%;
  padding: 10px 14px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 14px;
  font-family: inherit;
  outline: none;
  transition: border-color 0.2s;
  line-height: 1.6;
  color: #1e293b;
  background: #fff;
}

.form-textarea:focus, .form-select:focus, .form-input:focus {
  border-color: #4f6ef7;
}

.form-textarea { resize: vertical; }

.checkbox-row { display: flex; gap: 16px; flex-wrap: wrap; }

.checkbox-item {
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  font-size: 14px;
  color: #374151;
}

.modal-footer {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 24px;
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
