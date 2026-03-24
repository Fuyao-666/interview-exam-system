"""
面试考试系统 - Flask 后端主应用
"""
import os
import json
import random
import math
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required, get_jwt_identity
)
from models import db, User, Question, ExamConfig, Candidate, ExamPaper, Answer

# 创建 Flask 应用
app = Flask(__name__, static_folder=None)

# 配置
basedir = os.path.abspath(os.path.dirname(__file__))
database_url = os.environ.get('DATABASE_URL')
if database_url:
    # Render PostgreSQL: fix postgres:// -> postgresql://
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    print(f"[DB] 使用 PostgreSQL 数据库")
else:
    if os.environ.get('RENDER'):
        # 在 Render 上必须使用 PostgreSQL，防止回退到 SQLite 丢数据
        raise RuntimeError("错误：未设置 DATABASE_URL 环境变量，Render 环境下不允许使用 SQLite！")
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'instance', 'interview.db')
    print(f"[DB] 使用本地 SQLite 数据库（开发模式）")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=8)

# 初始化扩展
db.init_app(app)
CORS(app)
jwt = JWTManager(app)


# ==================== 初始化数据库 ====================
def init_db():
    try:
        with app.app_context():
            db.create_all()
            admin = User.query.filter_by(role='admin').first()
            if not admin:
                admin = User(username='admin', role='admin')
                admin.set_password('admin123')
                db.session.add(admin)
                db.session.commit()
                print("已创建默认管理员账号：admin / admin123")
            # 确保考试配置存在且时长为90分钟
            config = ExamConfig.query.first()
            if not config:
                config = ExamConfig(duration_minutes=90)
                db.session.add(config)
                db.session.commit()
            elif config.duration_minutes != 90:
                config.duration_minutes = 90
                db.session.commit()
                print("已更新考试时长为90分钟")
    except Exception as e:
        print(f"初始化数据库失败: {e}")
        import traceback
        traceback.print_exc()


# ==================== 认证路由 ====================
@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return jsonify({'error': '用户名或密码错误'}), 401
    if not user.is_active:
        return jsonify({'error': '账号已被停用'}), 403
    
    access_token = create_access_token(identity=json.dumps({'id': user.id, 'role': user.role}))
    return jsonify({'access_token': access_token, 'user': user.to_dict()})


# ==================== 题库管理路由 ====================
@app.route('/api/questions', methods=['GET'])
@jwt_required()
def get_questions():
    current_user = json.loads(get_jwt_identity())
    if current_user['role'] not in ['admin', 'interviewer']:
        return jsonify({'error': '无权限访问'}), 403
    
    question_type = request.args.get('type')
    query = Question.query
    if question_type:
        query = query.filter_by(question_type=question_type)
    
    questions = query.order_by(Question.created_at.desc()).all()
    return jsonify({'questions': [q.to_dict() for q in questions], 'total': len(questions)})


@app.route('/api/questions', methods=['POST'])
@jwt_required()
def create_question():
    current_user = json.loads(get_jwt_identity())
    if current_user['role'] not in ['admin', 'interviewer']:
        return jsonify({'error': '无权限创建题目'}), 403
    
    data = request.get_json()
    question_type = data.get('question_type')
    question_text = data.get('question_text')
    options = data.get('options', [])
    answer = data.get('answer')
    max_score = data.get('max_score', 0)
    
    if not question_type or not question_text:
        return jsonify({'error': '题目类型和题干不能为空'}), 400
    
    question = Question(
        question_type=question_type,
        question_text=question_text,
        options=json.dumps(options, ensure_ascii=False) if options else None,
        answer=json.dumps(answer, ensure_ascii=False) if answer else None,
        max_score=max_score,
        created_by=current_user['id']
    )
    db.session.add(question)
    db.session.commit()
    return jsonify(question.to_dict()), 201


@app.route('/api/questions/<int:question_id>', methods=['PUT'])
@jwt_required()
def update_question(question_id):
    current_user = json.loads(get_jwt_identity())
    if current_user['role'] not in ['admin', 'interviewer']:
        return jsonify({'error': '无权限修改题目'}), 403
    
    question = Question.query.get_or_404(question_id)
    data = request.get_json()
    
    if 'question_type' in data:
        question.question_type = data['question_type']
    if 'question_text' in data:
        question.question_text = data['question_text']
    if 'options' in data:
        question.options = json.dumps(data['options'], ensure_ascii=False)
    if 'answer' in data:
        question.answer = json.dumps(data['answer'], ensure_ascii=False)
    if 'max_score' in data:
        question.max_score = data['max_score']
    
    db.session.commit()
    return jsonify(question.to_dict())


@app.route('/api/questions/<int:question_id>', methods=['DELETE'])
@jwt_required()
def delete_question(question_id):
    current_user = json.loads(get_jwt_identity())
    if current_user['role'] not in ['admin', 'interviewer']:
        return jsonify({'error': '无权限删除题目'}), 403
    
    question = Question.query.get_or_404(question_id)
    db.session.delete(question)
    db.session.commit()
    return '', 204


# ==================== 考试配置路由 ====================
@app.route('/api/exam/config', methods=['GET'])
def get_exam_config():
    config = ExamConfig.query.first()
    if not config:
        config = ExamConfig()
        db.session.add(config)
        db.session.commit()
    return jsonify(config.to_dict())


@app.route('/api/exam/config', methods=['PUT'])
@jwt_required()
def update_exam_config():
    current_user = json.loads(get_jwt_identity())
    if current_user['role'] not in ['admin', 'interviewer']:
        return jsonify({'error': '无权限修改配置'}), 403
    
    config = ExamConfig.query.first()
    if not config:
        config = ExamConfig()
        db.session.add(config)
    
    data = request.get_json()
    for field in ['choice_count', 'choice_total_score', 'essay_count', 'essay_total_score',
                  'programming_count', 'programming_total_score', 'duration_minutes']:
        if field in data:
            setattr(config, field, data[field])
    
    db.session.commit()
    return jsonify(config.to_dict())


# ==================== 候选人考试路由 ====================
@app.route('/api/candidate/start', methods=['POST'])
def start_exam():
    data = request.get_json()
    name = data.get('name')
    phone = data.get('phone')
    company = data.get('company', '')
    
    if not name or not phone:
        return jsonify({'error': '姓名和手机号不能为空'}), 400
    
    # 同月答题次数限制：每个手机号同月最多3次
    now = datetime.now()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    month_candidates = Candidate.query.filter_by(phone=phone).all()
    if month_candidates:
        candidate_ids = [c.id for c in month_candidates]
        month_exam_count = ExamPaper.query.filter(
            ExamPaper.candidate_id.in_(candidate_ids),
            ExamPaper.start_time >= month_start
        ).count()
        if month_exam_count >= 3:
            return jsonify({'error': '该手机号本月答题次数已达上限（3次）'}), 400
    
    # 查找或创建候选人
    candidate = Candidate.query.filter_by(name=name, phone=phone).first()
    if not candidate:
        candidate = Candidate(name=name, phone=phone, company=company, position='RPA专员')
        db.session.add(candidate)
        db.session.commit()
    else:
        if company:
            candidate.company = company
            db.session.commit()
    
    # 检查是否有未完成的考试
    existing_paper = ExamPaper.query.filter_by(candidate_id=candidate.id, status='in_progress').first()
    if existing_paper:
        return jsonify({
            'paper_id': existing_paper.id,
            'candidate_id': candidate.id,
            'resume': True,
            'start_time': existing_paper.start_time.isoformat()
        })
    
    # 获取考试配置
    config = ExamConfig.query.first()
    if not config:
        return jsonify({'error': '考试配置未设置'}), 500
    
    # 随机抽题：选择题（单选+多选混合）+ 简答题 + 编程/设计题
    all_single = Question.query.filter_by(question_type='single').all()
    all_multiple = Question.query.filter_by(question_type='multiple').all()
    all_choice = all_single + all_multiple
    random.shuffle(all_choice)
    
    choice_questions = all_choice[:config.choice_count]
    essay_questions = Question.query.filter_by(question_type='essay').order_by(db.func.random()).limit(config.essay_count).all()
    programming_questions = Question.query.filter_by(question_type='programming').order_by(db.func.random()).limit(config.programming_count).all()
    
    if len(choice_questions) < config.choice_count:
        return jsonify({'error': f'选择题数量不足，需要{config.choice_count}道，当前仅{len(choice_questions)}道'}), 400
    if len(essay_questions) < config.essay_count:
        return jsonify({'error': f'简答题数量不足，需要{config.essay_count}道，当前仅{len(essay_questions)}道'}), 400
    if len(programming_questions) < config.programming_count:
        return jsonify({'error': f'编程/设计题数量不足，需要{config.programming_count}道，当前仅{len(programming_questions)}道'}), 400
    
    # 计算每题分值
    choice_per = math.ceil(config.choice_total_score / config.choice_count)
    essay_per = math.ceil(config.essay_total_score / config.essay_count)
    programming_per = math.ceil(config.programming_total_score / config.programming_count)
    
    all_questions = choice_questions + essay_questions + programming_questions
    question_ids = [q.id for q in all_questions]
    
    score_map = {}
    for q in choice_questions:
        score_map[str(q.id)] = choice_per
    for q in essay_questions:
        score_map[str(q.id)] = essay_per
    for q in programming_questions:
        score_map[str(q.id)] = programming_per
    
    paper = ExamPaper(
        candidate_id=candidate.id,
        questions=json.dumps({'ids': question_ids, 'scores': score_map}),
        start_time=datetime.now(),
        status='in_progress'
    )
    db.session.add(paper)
    db.session.commit()
    
    return jsonify({
        'paper_id': paper.id,
        'candidate_id': candidate.id,
        'resume': False,
        'start_time': paper.start_time.isoformat(),
        'duration_minutes': config.duration_minutes
    })


@app.route('/api/exam/paper/<int:paper_id>', methods=['GET'])
def get_exam_paper(paper_id):
    paper = ExamPaper.query.get_or_404(paper_id)
    if paper.status != 'in_progress':
        return jsonify({'error': '考试已结束'}), 400
    
    paper_data = json.loads(paper.questions)
    if isinstance(paper_data, list):
        question_ids = paper_data
        score_map = {}
    else:
        question_ids = paper_data.get('ids', [])
        score_map = paper_data.get('scores', {})
    
    questions = Question.query.filter(Question.id.in_(question_ids)).all()
    questions.sort(key=lambda q: question_ids.index(q.id))
    
    config = ExamConfig.query.first()
    
    exam_questions = []
    for q in questions:
        q_dict = q.to_dict()
        q_dict.pop('answer', None)
        exam_score = score_map.get(str(q.id), q.max_score)
        q_dict['max_score'] = exam_score
        exam_questions.append(q_dict)
    
    # 服务器端计算剩余秒数，避免时区问题
    duration = config.duration_minutes if config else 60
    elapsed = (datetime.now() - paper.start_time).total_seconds()
    remaining_seconds = max(0, duration * 60 - int(elapsed))

    return jsonify({
        'questions': exam_questions,
        'start_time': paper.start_time.isoformat(),
        'duration_minutes': duration,
        'remaining_seconds': remaining_seconds,
        'candidate_name': paper.candidate.name if paper.candidate else '',
        'position': paper.candidate.position if paper.candidate else ''
    })


@app.route('/api/exam/submit', methods=['POST'])
def submit_exam():
    data = request.get_json()
    paper_id = data.get('paper_id')
    answers = data.get('answers', [])
    screen_focus_loss_count = data.get('screen_focus_loss_count', 0)
    
    paper = ExamPaper.query.get_or_404(paper_id)
    if paper.status != 'in_progress':
        return jsonify({'error': '考试已结束'}), 400
    
    paper.screen_focus_loss_count = screen_focus_loss_count
    
    paper_data = json.loads(paper.questions)
    if isinstance(paper_data, list):
        question_ids = paper_data
        score_map = {}
    else:
        question_ids = paper_data.get('ids', [])
        score_map = paper_data.get('scores', {})
    
    questions = {q.id: q for q in Question.query.filter(Question.id.in_(question_ids)).all()}
    
    objective_score = 0
    for ans_data in answers:
        question_id = ans_data.get('question_id')
        answer_content = ans_data.get('answer_content')
        question = questions.get(question_id)
        if not question:
            continue
        
        exam_score = score_map.get(str(question_id), question.max_score)
        
        answer = Answer(
            paper_id=paper.id,
            question_id=question.id,
            question_type=question.question_type,
            answer_content=json.dumps(answer_content, ensure_ascii=False) if isinstance(answer_content, list) else answer_content
        )
        
        # 仅自动批改选择题
        if question.question_type == 'single':
            correct = json.loads(question.answer) if question.answer else None
            if answer_content == correct:
                objective_score += exam_score
                answer.score = exam_score
        elif question.question_type == 'multiple':
            correct = set(json.loads(question.answer)) if question.answer else set()
            student = set(answer_content) if isinstance(answer_content, list) else set()
            if student == correct:
                objective_score += exam_score
                answer.score = exam_score
        
        db.session.add(answer)
    
    paper.objective_score = objective_score
    paper.end_time = datetime.now()
    paper.status = 'submitted'
    db.session.commit()
    
    return jsonify({'message': '交卷成功', 'objective_score': objective_score})


@app.route('/api/exam/result/<int:paper_id>', methods=['GET'])
def get_exam_result(paper_id):
    """公开接口 - 候选人查看自己的考试结果"""
    paper = ExamPaper.query.get_or_404(paper_id)
    candidate = paper.candidate
    result = {
        'id': paper.id,
        'candidate_name': candidate.name if candidate else '',
        'phone': candidate.phone if candidate else '',
        'company': candidate.company if candidate else '',
        'position': candidate.position if candidate else 'RPA专员',
        'objective_score': paper.objective_score,
        'subjective_score': paper.subjective_score,
        'total_score': paper.total_score,
        'status': paper.status,
        'start_time': paper.start_time.isoformat() if paper.start_time else None,
        'end_time': paper.end_time.isoformat() if paper.end_time else None,
        'screen_focus_loss_count': paper.screen_focus_loss_count or 0
    }
    return jsonify(result)


@app.route('/api/exam/focus-loss', methods=['POST'])
def record_focus_loss():
    data = request.get_json()
    paper_id = data.get('paper_id')
    paper = ExamPaper.query.get_or_404(paper_id)
    paper.screen_focus_loss_count += 1
    if paper.screen_focus_loss_count >= 3:
        paper.end_time = datetime.now()
        paper.status = 'timeout'
    db.session.commit()
    return jsonify({'focus_loss_count': paper.screen_focus_loss_count, 'forced_submit': paper.status == 'timeout'})


# ==================== 阅卷路由 ====================
@app.route('/api/review/pending', methods=['GET'])
@jwt_required()
def get_pending_papers():
    current_user = json.loads(get_jwt_identity())
    if current_user['role'] not in ['admin', 'interviewer']:
        return jsonify({'error': '无权限访问'}), 403
    
    papers = ExamPaper.query.filter_by(status='submitted').order_by(ExamPaper.end_time.desc()).all()
    result = []
    for p in papers:
        p_dict = p.to_dict()
        p_dict['answers'] = []
        for a in p.answers:
            a_dict = a.to_dict()
            a_dict['question_text'] = a.question.question_text if a.question else ''
            a_dict['max_score'] = a.question.max_score if a.question else 0
            a_dict['question_type'] = a.question_type
            p_dict['answers'].append(a_dict)
        result.append(p_dict)
    return jsonify(result)


@app.route('/api/review/grade', methods=['POST'])
@jwt_required()
def grade_paper():
    current_user = json.loads(get_jwt_identity())
    if current_user['role'] not in ['admin', 'interviewer']:
        return jsonify({'error': '无权限阅卷'}), 403
    
    data = request.get_json()
    paper_id = data.get('paper_id')
    subjective_scores = data.get('subjective_scores', [])
    grader_comment = data.get('grader_comment', '')
    
    paper = ExamPaper.query.get_or_404(paper_id)
    
    total_subjective = 0
    for sd in subjective_scores:
        answer = Answer.query.get(sd.get('answer_id'))
        if answer and answer.paper_id == paper.id:
            score = min(sd.get('score', 0), answer.question.max_score)
            answer.score = score
            answer.grader_comment = sd.get('comment', '')
            total_subjective += score
    
    paper.subjective_score = total_subjective
    paper.total_score = paper.objective_score + total_subjective
    paper.grader_id = current_user['id']
    paper.grader_comment = grader_comment
    paper.graded_at = datetime.now()
    paper.status = 'graded'
    db.session.commit()
    
    return jsonify({'message': '阅卷完成', 'total_score': paper.total_score})


# ==================== 管理员路由 ====================
@app.route('/api/admin/users', methods=['GET'])
@jwt_required()
def get_users():
    current_user = json.loads(get_jwt_identity())
    if current_user['role'] != 'admin':
        return jsonify({'error': '仅管理员可访问'}), 403
    return jsonify([u.to_dict() for u in User.query.all()])


@app.route('/api/admin/users', methods=['POST'])
@jwt_required()
def create_user():
    current_user = json.loads(get_jwt_identity())
    if current_user['role'] != 'admin':
        return jsonify({'error': '仅管理员可创建用户'}), 403
    
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if User.query.filter_by(username=username).first():
        return jsonify({'error': '用户名已存在'}), 400
    
    user = User(username=username, role='interviewer')
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return jsonify(user.to_dict()), 201


@app.route('/api/admin/users/<int:user_id>/toggle', methods=['POST'])
@jwt_required()
def toggle_user(user_id):
    current_user = json.loads(get_jwt_identity())
    if current_user['role'] != 'admin':
        return jsonify({'error': '仅管理员可操作'}), 403
    user = User.query.get_or_404(user_id)
    user.is_active = not user.is_active
    db.session.commit()
    return jsonify(user.to_dict())


@app.route('/api/admin/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    """删除面试官账号"""
    current_user = json.loads(get_jwt_identity())
    if current_user['role'] != 'admin':
        return jsonify({'error': '仅管理员可操作'}), 403
    user = User.query.get_or_404(user_id)
    if user.role == 'admin':
        return jsonify({'error': '不能删除管理员账号'}), 400
    # 清除外键引用后再删除
    try:
        Question.query.filter_by(created_by=user.id).update({'created_by': None})
        ExamPaper.query.filter_by(grader_id=user.id).update({'grader_id': None})
        db.session.flush()
        db.session.delete(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'删除失败: {str(e)}'}), 500
    return '', 204


@app.route('/api/admin/results', methods=['GET'])
@jwt_required()
def get_results():
    current_user = json.loads(get_jwt_identity())
    if current_user['role'] != 'admin':
        return jsonify({'error': '仅管理员可访问'}), 403
    
    name_filter = request.args.get('name')
    query = ExamPaper.query.join(Candidate)
    if name_filter:
        query = query.filter(Candidate.name.contains(name_filter))
    
    papers = query.order_by(ExamPaper.end_time.desc()).all()
    return jsonify([p.to_dict() for p in papers])


@app.route('/api/admin/papers/<int:paper_id>', methods=['DELETE'])
@jwt_required()
def delete_paper(paper_id):
    """删除已答试卷"""
    current_user = json.loads(get_jwt_identity())
    if current_user['role'] != 'admin':
        return jsonify({'error': '仅管理员可操作'}), 403
    paper = ExamPaper.query.get_or_404(paper_id)
    Answer.query.filter_by(paper_id=paper.id).delete()
    db.session.delete(paper)
    db.session.commit()
    return '', 204


# ==================== 创建管理员接口（一次性使用） ====================
@app.route('/api/create-admin', methods=['POST'])
def create_admin():
    """创建管理员账号"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    secret = data.get('secret')
    if secret != app.config['JWT_SECRET_KEY']:
        return jsonify({'error': '无权限'}), 403
    if User.query.filter_by(username=username).first():
        return jsonify({'error': '用户名已存在'}), 400
    user = User(username=username, role='admin')
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': f'管理员 {username} 创建成功', 'user': user.to_dict()}), 201


# ==================== 数据库种子数据接口 ====================
@app.route('/api/seed', methods=['POST'])
def seed_data():
    """初始化或重置题库数据"""
    force = request.args.get('force', 'false') == 'true'

    existing_questions = Question.query.count()
    if existing_questions > 0 and not force:
        return jsonify({'message': f'题库已有{existing_questions}道题目，如需重置请加 ?force=true 参数'}), 200

    # 确保管理员账号存在
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(username='admin', role='admin')
        admin.set_password('admin123')
        db.session.add(admin)

    # 确保考试配置存在
    config = ExamConfig.query.first()
    if not config:
        config = ExamConfig(duration_minutes=90)
        db.session.add(config)

    # 如果 force=true，清空旧题库（需先清除引用题目的答题记录）
    if force and existing_questions > 0:
        Answer.query.delete()
        Question.query.delete()
        db.session.commit()

    # ==================== 20道Python选择题 ====================
    choice_questions = [
        {"text": "下列哪个语句在Python中是非法的？", "options": ["x = y = z = 1", "x = (y = z + 1)", "x, y = y, x", "x  +=  y"], "answer": "B"},
        {"text": "关于Python内存管理，下列说法错误的是", "options": ["变量不必事先声明", "变量无须先创建和赋值而直接使用", "变量无须指定类型", "可以使用del释放资源"], "answer": "B"},
        {"text": "以下不能创建一个字典的语句是", "options": ["dict1 = {}", "dict2 = { 3 : 5 }", 'dict3 = {[1,2,3]: "uestc"}', 'dict4 = {(1,2,3): "uestc"}'], "answer": "C"},
        {"text": "python 代码执行的方式", "options": ["编译执行", "解析执行", "直接执行", "边编译边执行"], "answer": "B"},
        {"text": "调用以下函数返回的值\ndef myfun():\n    pass", "options": ["0", "出错不能运行", "空字符串", "None"], "answer": "D"},
        {"text": "导入模块的方式错误的是", "options": ["import mo", "from mo import *", "import mo as m", "import m from mo"], "answer": "D"},
        {"text": "以下关于模块说法错误的是", "options": ["一个xx.py就是一个模块", "任何一个普通的xx.py文件可以作为模块导入", "模块文件的扩展名不一定是 .py", "运行时会从指定的目录搜索导入的模块，如果没有，会报错异常"], "answer": "C"},
        {"text": "关于Python循环结构，以下选项中描述错误的是", "options": ["每个continue语句只有能力跳出当前层次的循环", "break用来跳出最内层for或者while循环，脱离该循环后程序从循环代码后继续执行", "遍历循环中的遍历结构可以是字符串、文件、组合数据类型和range()函数等", "Python通过for、while等保留字提供遍历循环和无限循环结构"], "answer": "A"},
        {"text": "关于Python的lambda函数，以下选项中描述错误的是", "options": ["lambda函数将函数名作为函数结果返回", "f = lambda x,y:x+y 执行后，f的类型为数字类型", "lambda用于定义简单的、能够在一行内表示的函数", "可以使用lambda函数定义列表的排序原则"], "answer": "B"},
        {"text": '给出如下代码，下述代码的输出结果是\ns = "Alice"\nprint(s[::-1])', "options": ["ALICE", "ecilA", "Alic", "Alice"], "answer": "B"},
        {"text": "在Python中，关于全局变量和局部变量，以下选项中描述不正确的是", "options": ["一个程序中的变量包含两类：全局变量和局部变量", "全局变量不能和局部变量重名", "全局变量一般没有缩进", "全局变量在程序执行的全过程有效"], "answer": "B"},
        {"text": "下面代码的输出结果是\ndict = {'a': 1, 'b': 2, 'b': '3'}\ntemp = dict['b']\nprint(temp)", "options": ["1", "{'b': 2}", "3", "2"], "answer": "C"},
        {"text": "关于函数的可变参数，可变参数*args传入函数时存储的类型是", "options": ["dict", "tuple", "list", "set"], "answer": "B"},
        {"text": "以下不能创建一个字典的语句是", "options": ["dic1 = {}", "dic2 = {123:345}", "dic3 = {[1,2,3]:'uestc'}", "dic3 = {(1,2,3):'uestc'}"], "answer": "C"},
        {"text": "下面的语句哪个会无限循环下去", "options": ["for a in range(10): time.sleep(10)", "while 1<10: time.sleep(10)", "while True: break", "a = [3,-1,',']\nfor i in a[:]: if not a: break"], "answer": "B"},
        {"text": "以下关于循环结构的描述，错误的是", "options": ["遍历循环使用for <循环变量> in <循环结构>语句，其中循环结构不能是文件", "使用range()函数可以指定for循环的次数", "for i in range(5)表示循环5次，i的值是从0到4", "用字符串做循环结构的时候，循环的次数是字符串的长度"], "answer": "A"},
        {"text": "关于 Python 的分支结构，以下选项中描述错误的是", "options": ["分支结构使用 if 保留字", "Python 中 if-else 语句用来形成二分支结构", "Python 中 if-elif-else 语句描述多分支结构", "分支结构可以向已经执行过的语句部分跳转"], "answer": "D"},
        {"text": '以下语句执行后a、b、c的值是\na = "watermelon"\nb = "strawberry"\nc = "cherry"\nif a > b:\n    c = a\n    a = b\n    b = c', "options": ["watermelon strawberry cherry", "watermelon cherry strawberry", "strawberry cherry watermelon", "strawberry watermelon watermelon"], "answer": "D"},
        {"text": "以下代码的输出结果是什么？\n\ndef func(x, lst=[]):\n    lst.append(x)\n    return lst\n\na = func(1)\nb = func(2)\nprint(a, b)", "options": ["[1] [2]", "[1] [1, 2]", "[1, 2] [1, 2]", "[1, 2] [2]"], "answer": "C"},
        {"text": "以下代码的输出结果是什么？\n\ndata = {'a': 1, 'b': 2, 'c': 3}\nfor key in data:\n    if data[key] % 2 == 0:\n        data[key] = data[key] * 2\n    else:\n        data[key] = data[key] + 1\n\nprint(data)", "options": ["{'a': 2, 'b': 4, 'c': 2}", "{'a': 2, 'b': 4, 'c': 3}", "{'a': 2, 'b': 4, 'c': 4}", "{'a': 1, 'b': 4, 'c': 3}"], "answer": "C"},
    ]

    for q in choice_questions:
        question = Question(
            question_type='single',
            question_text=q["text"],
            options=json.dumps(q["options"], ensure_ascii=False),
            answer=json.dumps(q["answer"], ensure_ascii=False),
            max_score=3
        )
        db.session.add(question)

    # ==================== 10道简答题 ====================
    essay_questions = [
        "请简述你印象最深刻的一个RPA项目，需要表明其中的业务细节，关键技术点，技术卡点等。越详细分数越高",
        "A,B电脑在硬件配置，网络环境一致，影刀及钉钉版本一致的情况下。A电脑使用影刀可以正常捕获元素，B电脑只能捕获到窗体，请简述一下发生此问题的原因。",
        "什么是 JS 加密，在爬虫中为什么会遇到 JS 加密？有那些加密形式？",
        "常见的HTTP状态码有哪些？分别代表什么含义？",
        "你认为完整的提示词（prompt）应该包含哪些内容",
        "什么是API？如何设计一个安全的请求API？如何测试API的性能？",
        "当你在使用用影刀操作网页时，遇到【执行相似元素出错：下标值超过最大下标】的报错，请阐述可能出现该问题的原因",
        "当你用影刀下载文件指令时，该文件肉眼可见的下载完成，但是下载文件指令仍在运行，并报了下载文件超时的错误。请简述出现该问题的原因",
        "当你设计某网页操作流程时，某元素会经常报元素失效的错误，但是进行元素检验时又可以检验到。请简述发生这种情况的原因可能有哪些？",
        "常见的HTTP请求方法有哪些？GET和POST请求有什么区别？",
    ]

    for text in essay_questions:
        question = Question(
            question_type='essay',
            question_text=text,
            max_score=10
        )
        db.session.add(question)

    # ==================== 10道编程/设计题 ====================
    programming_questions = [
        "如果遇到该题目，你可以将姓名+电话号码+面试公司提交到答案框。答完其他题目后先提交试卷，打开影刀设计器及录屏软件编写该项目，并将录屏以姓名+面试公司的方式命名提交给面试官。\n\n题目描述：打开影刀商城https://shop.yingdao.com/\n1. 需设计登录操作，账号：admin，密码：58T2$!hm\n2. 在【订单管理】页面，将所有商品名称为"篮球鞋"且订单状态为完成的商品点击发货\n3. 新建Excel文件，以当前日期命名，将已发货的订单编号，商品名称，金额，日期和"已发货"记入【已发货】sheet页中\n4. 在【工作台-退款管理页面】，导出待退款订单详情，将所有退款类型为"仅退款"且发货物流为"未发货"的订单点击同意申请，并在Excel中将"退款状态"更改为"已退款"。",
        "如果遇到该题目，你可以将姓名+电话号码+面试公司提交到答案框。答完其他题目后先提交试卷，打开影刀设计器及录屏软件编写该项目，并将录屏以姓名+面试公司的方式命名提交给面试官。\n\n题目描述：应用中请模拟人工登录，勿使用「京东登录」指令。\n1. 账号登录：登录京东商城，完成滑块验证\n2. 在首页搜索水果，按销量排序\n3. 数据获取：获取销量前20的商品信息，包括：销量排名、商品主图、商品标题、商品价格、店铺名、商品详情（品牌 商品名称 商品编号 商品产地 品种）、好评率\n4. 将获取的商品信息保存至本地Excel表格，其中若商品详情中缺少某个类目，则写入"其他"\n5. 在上述自动化流程中，对流程做异常处理\n6. 最后在完成的基础上，做流程封装。",
        "如果遇到该题目，你可以将姓名+电话号码+面试公司提交到答案框。答完其他题目后先提交试卷，打开影刀设计器及录屏软件编写该项目，并将录屏以姓名+面试公司的方式命名提交给面试官。\n\n题目描述：请根据配置文档，完成短信转发器与影刀的交互，具体要求如下：\n1. 选择自己的手机型号，在手机端完成转发器的配置。配置要求如下：只识别或转发开头为【影刀】的消息。\n2. 手机收到该消息后可以自动转发至指定邮箱（邮箱形式不限）\n3. 设计影刀应用监听该邮箱，当收到以【影刀】为开头的消息时，自动弹出对话框显示该消息",
        "DNA序列由一系列核苷酸组成，缩写为 'A', 'C', 'G' 和 'T'。例如，\"ACGAATTCCG\" 是一个DNA序列。\n给定一个表示DNA序列的字符串s，返回所有在DNA分子中出现不止一次的长度为10的序列(子字符串)。你可以按任意顺序返回答案。\n\n示例1：\n输入：s = \"AAAAACCCCCAAAAACCCCCCAAAAAGGGTTT\"\n输出：[\"AAAAACCCCC\",\"CCCCCAAAAA\"]\n\n示例2：\n输入：s = \"AAAAAAAAAAAAA\"\n输出：[\"AAAAAAAAAA\"]",
        "假设n个人站成一排，按从1到n编号。最初，排在队首的第一个人拿着一个枕头。每秒钟，拿着枕头的人会将枕头传递给队伍中的下一个人。一旦枕头到达队首或队尾，传递方向就会改变，队伍会继续沿相反方向传递枕头。\n例如，当枕头到达第n个人时，TA会将枕头传递给第n-1个人，然后传递给第n-2个人，依此类推。\n给你两个正整数n和time，返回time秒后拿着枕头的人的编号。",
        "给定一个整数列表nums和一个整数目标值target，请你在该数组中找出和为目标值target的那两个整数，并返回它们的列表下标。\n你可以假设每种输入只会对应一个答案，并且你不能使用两次相同的元素。你可以按任意顺序返回答案。\n\n示例1：\n输入：nums = [2,7,11,15], target = 9\n输出：[0,1]\n解释：因为nums[0] + nums[1] == 9，返回[0, 1]。\n\n示例2：\n输入：nums = [3,2,4], target = 6\n输出：[1,2]\n\n示例3：\n输入：nums = [3,3], target = 6\n输出：[0,1]",
        "编写一个函数来查找字符串数组中的最长公共前缀。如果不存在公共前缀，返回空字符串\"\"。\n\n示例1：\n输入：strs = [\"flower\",\"flow\",\"flight\"]\n输出：\"fl\"\n\n示例2：\n输入：strs = [\"dog\",\"racecar\",\"car\"]\n输出：\"\"\n解释：输入不存在公共前缀。",
        "某一天，老板告诉你"我需要一个数据看板"（没错，只告诉你这一句话），请你根据你以往经验设计一套沟通方案和产品方案（产品方案可不局限于RPA）",
        "你需要轮训某业务人员提供给你的100个网址，获取每个网址中商品的价格（注意不同平台的元素排列方式可能会有不同，但不完全不同。可以这么理解，这些网站来自不同的平台，有些网站可能来自一样的平台），且这些网站都有一种不定时的风控（频次未知，形式为滑动验证，且触发频次过多的时候会出现人脸识别的情况），为完成该需求，请简述你的开发方案。",
        "在使用RPA应用操作网页时，网页中出现了许多不定时的弹窗如验证码、广告等阻碍你接下来的操作，请简述解决方法",
    ]

    for text in programming_questions:
        question = Question(
            question_type='programming',
            question_text=text,
            max_score=20
        )
        db.session.add(question)

    db.session.commit()

    total = Question.query.count()
    return jsonify({
        'message': f'题库更新成功！共{total}道题目',
        'detail': {
            'choice': len(choice_questions),
            'essay': len(essay_questions),
            'programming': len(programming_questions)
        }
    })


# ==================== 前端静态文件服务 ====================
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    dist_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend', 'dist'))
    file_path = os.path.join(dist_dir, path)
    if path and os.path.isfile(file_path):
        return send_from_directory(dist_dir, path)
    return send_from_directory(dist_dir, 'index.html')


if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
else:
    # Production: gunicorn entry
    init_db()
