"""
数据库模型定义
"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(db.Model):
    """用户表 - 面试官和管理员"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'interviewer' 或 'admin'
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Question(db.Model):
    """题库表"""
    __tablename__ = 'questions'
    
    id = db.Column(db.Integer, primary_key=True)
    question_type = db.Column(db.String(20), nullable=False)  # 'single', 'multiple', 'essay', 'programming'
    question_text = db.Column(db.Text, nullable=False)
    options = db.Column(db.Text)  # JSON 格式存储选项
    answer = db.Column(db.Text)  # 选择题答案
    max_score = db.Column(db.Integer, default=0)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        import json
        return {
            'id': self.id,
            'question_type': self.question_type,
            'question_text': self.question_text,
            'options': json.loads(self.options) if self.options else [],
            'answer': json.loads(self.answer) if self.answer and self.question_type in ('single', 'multiple') else None,
            'max_score': self.max_score,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class ExamConfig(db.Model):
    """考试配置表 - 固定试卷结构"""
    __tablename__ = 'exam_configs'
    
    id = db.Column(db.Integer, primary_key=True)
    # 选择题（单选+多选混合）10道 共30分
    choice_count = db.Column(db.Integer, default=10)
    choice_total_score = db.Column(db.Integer, default=30)
    # 简答题 3道 共30分
    essay_count = db.Column(db.Integer, default=3)
    essay_total_score = db.Column(db.Integer, default=30)
    # 编程题&思路设计题 2道 共40分
    programming_count = db.Column(db.Integer, default=2)
    programming_total_score = db.Column(db.Integer, default=40)
    # 考试时长
    duration_minutes = db.Column(db.Integer, default=90)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'choice_count': self.choice_count,
            'choice_total_score': self.choice_total_score,
            'essay_count': self.essay_count,
            'essay_total_score': self.essay_total_score,
            'programming_count': self.programming_count,
            'programming_total_score': self.programming_total_score,
            'duration_minutes': self.duration_minutes
        }


class Candidate(db.Model):
    """候选人表"""
    __tablename__ = 'candidates'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    company = db.Column(db.String(200))  # 面试公司
    position = db.Column(db.String(100), default='RPA专员')  # 固定 RPA专员
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('name', 'phone', name='unique_candidate'),)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'phone': self.phone,
            'company': self.company,
            'position': self.position,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class ExamPaper(db.Model):
    """试卷表"""
    __tablename__ = 'exam_papers'
    
    id = db.Column(db.Integer, primary_key=True)
    candidate_id = db.Column(db.Integer, db.ForeignKey('candidates.id'), nullable=False)
    questions = db.Column(db.Text, nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='in_progress')
    screen_focus_loss_count = db.Column(db.Integer, default=0)
    total_score = db.Column(db.Integer, default=0)
    objective_score = db.Column(db.Integer, default=0)
    subjective_score = db.Column(db.Integer, default=0)
    grader_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    grader_comment = db.Column(db.Text)
    graded_at = db.Column(db.DateTime)
    
    candidate = db.relationship('Candidate', backref=db.backref('exam_papers', lazy=True))
    
    def to_dict(self):
        import json
        return {
            'id': self.id,
            'candidate_id': self.candidate_id,
            'candidate_name': self.candidate.name if self.candidate else None,
            'position': self.candidate.position if self.candidate else None,
            'company': self.candidate.company if self.candidate else None,
            'phone': self.candidate.phone if self.candidate else None,
            'questions': json.loads(self.questions) if self.questions else [],
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'status': self.status,
            'screen_focus_loss_count': self.screen_focus_loss_count,
            'total_score': self.total_score,
            'objective_score': self.objective_score,
            'subjective_score': self.subjective_score,
            'grader_comment': self.grader_comment,
            'graded_at': self.graded_at.isoformat() if self.graded_at else None
        }


class Answer(db.Model):
    """答题记录表"""
    __tablename__ = 'answers'
    
    id = db.Column(db.Integer, primary_key=True)
    paper_id = db.Column(db.Integer, db.ForeignKey('exam_papers.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    question_type = db.Column(db.String(20), nullable=False)
    answer_content = db.Column(db.Text)
    score = db.Column(db.Integer, default=0)
    grader_comment = db.Column(db.Text)
    
    paper = db.relationship('ExamPaper', backref=db.backref('answers', lazy=True))
    question = db.relationship('Question')
    
    def to_dict(self):
        return {
            'id': self.id,
            'paper_id': self.paper_id,
            'question_id': self.question_id,
            'question_type': self.question_type,
            'answer_content': self.answer_content,
            'score': self.score,
            'grader_comment': self.grader_comment
        }
