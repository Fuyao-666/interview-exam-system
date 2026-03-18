import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from app import app, db
from models import User, Question

with app.app_context():
    users = User.query.all()
    for u in users:
        print(f'User: {u.username}, role: {u.role}, active: {u.is_active}')
    
    total = Question.query.count()
    single = Question.query.filter_by(question_type='single').count()
    print(f'\nTotal questions: {total}, single: {single}')
    
    recent = Question.query.order_by(Question.id.desc()).limit(5).all()
    for q in recent:
        print(f'  [{q.id}] {q.question_text[:50]}... answer={q.answer}')
