# 面试考试系统 - 快速启动指南

## 项目结构
```
interview-system/
├── backend/          # Flask 后端 API
│   ├── app.py       # 主应用入口
│   ├── models.py    # 数据库模型
│   └── instance/    # SQLite 数据库文件
├── frontend/         # Vue 3 前端
│   ├── src/
│   └── dist/        # 构建输出目录
└── README.md
```

## 快速启动

### 方式一：仅启动后端（推荐）
后端已配置静态文件服务，可直接访问前端页面。

```bash
cd backend
python app.py
```

然后访问 http://localhost:5000

### 方式二：开发模式（前后端分离）

**终端 1 - 启动后端:**
```bash
cd backend
python app.py
```

**终端 2 - 启动前端开发服务器:**
```bash
cd frontend
npm run dev
```

然后访问 http://localhost:3000

## 默认账号

**管理员账号:**
- 用户名：`admin`
- 密码：`admin123`

## 功能模块

### 候选人端
1. 访问 `/exam` 进入考试入口
2. 填写姓名、手机号、应聘岗位
3. 开始考试，系统自动随机抽题
4. 答题过程中切屏 3 次将被强制交卷
5. 交卷后可查看客观题得分

### 面试官端
1. 登录 `/login` 进入后台
2. **题库管理**: 录入单选、多选、简答题
3. **考试配置**: 设置抽题规则和考试时长
4. **试卷批阅**: 批阅考生的简答题并给出评语

### 管理员端
1. **账号管理**: 创建和管理面试官账号
2. **成绩档案**: 查看所有考生成绩和违纪记录

## API 接口

### 认证
- POST `/api/auth/login` - 用户登录

### 题库
- GET `/api/questions` - 获取题目列表
- POST `/api/questions` - 创建题目
- PUT `/api/questions/:id` - 更新题目
- DELETE `/api/questions/:id` - 删除题目

### 考试
- GET `/api/exam/config` - 获取考试配置
- PUT `/api/exam/config` - 更新考试配置
- POST `/api/candidate/start` - 开始考试
- GET `/api/exam/paper/:id` - 获取试卷
- POST `/api/exam/submit` - 提交试卷
- POST `/api/exam/focus-loss` - 记录切屏

### 阅卷
- GET `/api/review/pending` - 待批阅列表
- POST `/api/review/grade` - 提交批阅

### 管理
- GET `/api/admin/users` - 用户列表
- POST `/api/admin/users` - 创建用户
- POST `/api/admin/users/:id/toggle` - 启用/停用用户
- GET `/api/admin/results` - 成绩档案

## 部署到 Render

1. 将代码推送到 GitHub
2. 在 Render 创建新 Web Service
3. 连接 GitHub 仓库
4. 配置环境变量：
   - `JWT_SECRET_KEY`: 自定义密钥
   - `DATABASE_URL`: 数据库连接（可选）
5. 选择 Singapore 区域
6. 部署

## 技术栈

- **后端**: Python 3.8 + Flask + SQLite
- **前端**: Vue 3 + Vite + Pinia + Vue Router
- **认证**: JWT
- **部署**: Render (新加坡)
