# 面试考试系统

一个基于 Python + Flask + Vue 3 的在线面试考试系统，支持题库管理、随机抽题、在线作答、自动阅卷和防作弊功能。

## 技术栈

- **后端**: Python 3.8+ + Flask + SQLite
- **前端**: Vue 3 + Vite
- **部署**: Render (新加坡节点)

## 功能特性

### 三类用户角色
- **候选人**: 前台答题，无需注册，通过姓名 + 手机号进入考试
- **面试官**: 题库管理、抽题规则配置、人工阅卷
- **管理员**: 面试官账号管理、全局成绩查看

### 核心功能
- ✅ 题库管理（单选/多选/简答）
- ✅ 随机抽题组卷
- ✅ 倒计时考试（服务器时间为准）
- ✅ 防作弊监控（切屏检测、三振出局）
- ✅ 自动阅卷（客观题）
- ✅ 人工阅卷（主观题）
- ✅ 成绩管理与违纪记录

## 快速开始

### 后端启动
```bash
cd backend
pip install -r requirements.txt
python app.py
```

### 前端启动
```bash
cd frontend
npm install
npm run dev
```

## 项目结构
```
interview-system/
├── backend/          # Flask 后端 API
│   ├── app.py       # 主应用入口
│   ├── models.py    # 数据库模型
│   ├── routes/      # API 路由
│   └── instance/    # SQLite 数据库文件
├── frontend/         # Vue 3 前端
│   ├── src/
│   │   ├── views/   # 页面组件
│   │   └── components/ # 通用组件
│   └── public/
└── README.md
```

## API 文档

### 认证相关
- POST /api/auth/login - 用户登录

### 题库管理
- GET /api/questions - 获取题目列表
- POST /api/questions - 创建题目
- PUT /api/questions/:id - 更新题目
- DELETE /api/questions/:id - 删除题目

### 考试相关
- POST /api/exam/start - 开始考试
- GET /api/exam/paper - 获取试卷
- POST /api/exam/submit - 提交试卷
- GET /api/exam/history - 考试历史

### 阅卷相关
- GET /api/review/pending - 待批阅列表
- POST /api/review/grade - 批阅打分

## 部署

部署到 Render 平台（新加坡节点）：
1. 连接 GitHub 仓库
2. 选择 `backend/app.py` 作为启动文件
3. 设置环境变量
4. 选择 Singapore 区域部署
