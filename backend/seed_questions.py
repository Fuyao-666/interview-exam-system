"""
生成简答题和编程/设计题的测试数据
"""
import json
from models import db, Question
from app import app

essay_questions = [
    {
        'question_type': 'essay',
        'question_text': '请简述Python中列表(list)和元组(tuple)的区别，包括它们的特性、使用场景和性能差异。',
        'max_score': 10
    },
    {
        'question_type': 'essay',
        'question_text': '请解释什么是RPA（机器人流程自动化），它的核心优势有哪些？请至少列举3个RPA在企业中的典型应用场景。',
        'max_score': 10
    },
    {
        'question_type': 'essay',
        'question_text': '请解释Python中异常处理机制（try-except-finally），并说明在RPA开发中为什么异常处理特别重要。',
        'max_score': 10
    },
    {
        'question_type': 'essay',
        'question_text': '请描述你对Web页面元素定位的理解，常用的定位方式有哪些？在自动化操作中遇到动态加载元素时应如何处理？',
        'max_score': 10
    },
    {
        'question_type': 'essay',
        'question_text': '请简述Python中装饰器(decorator)的作用和基本原理，并举一个实际使用场景的例子。',
        'max_score': 10
    },
]

programming_questions = [
    {
        'question_type': 'programming',
        'question_text': '请编写一个Python函数，接收一个包含多个文件路径的列表，自动将所有Excel文件(.xlsx/.xls)中的数据合并到一个新的Excel文件中。请写出核心代码逻辑和思路说明。\n\n要求：\n1. 处理文件不存在的情况\n2. 每个源文件的数据作为独立的sheet\n3. 添加适当的错误处理',
        'max_score': 20
    },
    {
        'question_type': 'programming',
        'question_text': '设计一个自动化脚本的整体框架：需要每天定时从某网站抓取指定数据，清洗后存入数据库，并在出错时发送邮件通知。\n\n请描述：\n1. 整体架构设计思路\n2. 各模块的职责划分\n3. 写出数据抓取和错误通知模块的核心伪代码或Python代码',
        'max_score': 20
    },
    {
        'question_type': 'programming',
        'question_text': '请编写一个Python函数，实现以下功能：读取一个CSV文件，找出其中所有重复的行，并生成一份去重报告。\n\n要求：\n1. 函数签名：def find_duplicates(csv_path: str) -> dict\n2. 返回值包含：总行数、重复行数、去重后行数、具体重复内容\n3. 处理文件编码问题（支持UTF-8和GBK）\n4. 添加日志记录',
        'max_score': 20
    },
]

if __name__ == '__main__':
    with app.app_context():
        count = 0
        for q in essay_questions + programming_questions:
            question = Question(
                question_type=q['question_type'],
                question_text=q['question_text'],
                options=None,
                answer=None,
                max_score=q['max_score'],
                created_by=1
            )
            db.session.add(question)
            count += 1
        db.session.commit()
        print(f'Successfully imported {count} questions')

        from sqlalchemy import func
        results = db.session.query(Question.question_type, func.count(Question.id)).group_by(Question.question_type).all()
        print('Question counts by type:')
        for qtype, cnt in results:
            print(f'  {qtype}: {cnt}')
