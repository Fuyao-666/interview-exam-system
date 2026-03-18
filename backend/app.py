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
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'instance', 'interview.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=8)

# 初始化扩展
db.init_app(app)
CORS(app)
jwt = JWTManager(app)


# ==================== 初始化数据库 ====================
def init_db():
    with app.app_context():
        db.create_all()
        admin = User.query.filter_by(role='admin').first()
        if not admin:
            admin = User(username='admin', role='admin')
            admin.set_password('admin123')
            db.session.add(admin)
            config = ExamConfig()
            db.session.add(config)
            db.session.commit()
            print("已创建默认管理员账号：admin / admin123")


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
    
    access_token = create_access_token(identity={'id': user.id, 'role': user.role})
    return jsonify({'access_token': access_token, 'user': user.to_dict()})


# ==================== 题库管理路由 ====================
@app.route('/api/questions', methods=['GET'])
@jwt_required()
def get_questions():
    current_user = get_jwt_identity()
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
    current_user = get_jwt_identity()
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
    current_user = get_jwt_identity()
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
    current_user = get_jwt_identity()
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
    current_user = get_jwt_identity()
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
    
    return jsonify({
        'questions': exam_questions,
        'start_time': paper.start_time.isoformat(),
        'duration_minutes': config.duration_minutes if config else 60,
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
    current_user = get_jwt_identity()
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
    current_user = get_jwt_identity()
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
    current_user = get_jwt_identity()
    if current_user['role'] != 'admin':
        return jsonify({'error': '仅管理员可访问'}), 403
    return jsonify([u.to_dict() for u in User.query.all()])


@app.route('/api/admin/users', methods=['POST'])
@jwt_required()
def create_user():
    current_user = get_jwt_identity()
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
    current_user = get_jwt_identity()
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
    current_user = get_jwt_identity()
    if current_user['role'] != 'admin':
        return jsonify({'error': '仅管理员可操作'}), 403
    user = User.query.get_or_404(user_id)
    if user.role == 'admin':
        return jsonify({'error': '不能删除管理员账号'}), 400
    db.session.delete(user)
    db.session.commit()
    return '', 204


@app.route('/api/admin/results', methods=['GET'])
@jwt_required()
def get_results():
    current_user = get_jwt_identity()
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
    current_user = get_jwt_identity()
    if current_user['role'] != 'admin':
        return jsonify({'error': '仅管理员可操作'}), 403
    paper = ExamPaper.query.get_or_404(paper_id)
    Answer.query.filter_by(paper_id=paper.id).delete()
    db.session.delete(paper)
    db.session.commit()
    return '', 204


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
