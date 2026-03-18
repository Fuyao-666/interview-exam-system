# -*- coding: utf-8 -*-
"""批量创建示例题目"""
import requests

BASE_URL = 'http://localhost:5000/api'

# 登录获取 token
response = requests.post(f'{BASE_URL}/auth/login', json={
    'username': 'admin',
    'password': 'admin123'
})
token = response.json()['access_token']
headers = {'Authorization': f'Bearer {token}'}

print("开始批量创建题目...")

# 单选题库
single_questions = [
    {'question_type': 'single', 'question_text': 'Python 中哪个关键字用于定义函数？', 'options': ['A. function', 'B. def', 'C. define', 'D. func'], 'answer': 'B', 'max_score': 2},
    {'question_type': 'single', 'question_text': '以下哪个不是 Python 的数据类型？', 'options': ['A. list', 'B. dict', 'C. array', 'D. tuple'], 'answer': 'C', 'max_score': 2},
    {'question_type': 'single', 'question_text': 'Python 中如何注释单行代码？', 'options': ['A. //', 'B. /* */', 'C. #', 'D. --'], 'answer': 'C', 'max_score': 2},
    {'question_type': 'single', 'question_text': '哪个方法可以向列表末尾添加元素？', 'options': ['A. push()', 'B. add()', 'C. append()', 'D. insert()'], 'answer': 'C', 'max_score': 2},
    {'question_type': 'single', 'question_text': 'Python 中用于捕获异常的关键字是？', 'options': ['A. catch', 'B. except', 'C. error', 'D. handle'], 'answer': 'B', 'max_score': 2},
    {'question_type': 'single', 'question_text': '哪个模块用于处理日期时间？', 'options': ['A. time', 'B. date', 'C. datetime', 'D. calendar'], 'answer': 'C', 'max_score': 2},
    {'question_type': 'single', 'question_text': 'Python 中文件的打开模式 r 表示？', 'options': ['A. 写入', 'B. 只读', 'C. 追加', 'D. 读写'], 'answer': 'B', 'max_score': 2},
    {'question_type': 'single', 'question_text': '哪个装饰器用于定义静态方法？', 'options': ['A. @classmethod', 'B. @staticmethod', 'C. @property', 'D. @abstract'], 'answer': 'B', 'max_score': 2},
    {'question_type': 'single', 'question_text': 'Python 的 GIL 是什么的缩写？', 'options': ['A. Global Interpreter Lock', 'B. General Interface Library', 'C. Global Integration Layer', 'D. Generic Input Loop'], 'answer': 'A', 'max_score': 2},
    {'question_type': 'single', 'question_text': '以下哪个不是 Web 框架？', 'options': ['A. Flask', 'B. Django', 'C. NumPy', 'D. FastAPI'], 'answer': 'C', 'max_score': 2},
    {'question_type': 'single', 'question_text': 'Python 中 lambda 表达式的作用是？', 'options': ['A. 定义类', 'B. 导入模块', 'C. 创建匿名函数', 'D. 声明变量'], 'answer': 'C', 'max_score': 2},
    {'question_type': 'single', 'question_text': '哪个方法可以获取字典的所有键？', 'options': ['A. values()', 'B. items()', 'C. keys()', 'D. get()'], 'answer': 'C', 'max_score': 2},
    {'question_type': 'single', 'question_text': 'Python 中用于安装第三方库的工具是？', 'options': ['A. pip', 'B. npm', 'C. gem', 'D. cargo'], 'answer': 'A', 'max_score': 2},
    {'question_type': 'single', 'question_text': '以下哪个是正确的 Python 3 print 语法？', 'options': ['A. print "Hello"', 'B. echo "Hello"', 'C. print("Hello")', 'D. System.out.println("Hello")'], 'answer': 'C', 'max_score': 2},
    {'question_type': 'single', 'question_text': 'Python 中用于读取 JSON 数据的模块是？', 'options': ['A. pickle', 'B. json', 'C. xml', 'D. csv'], 'answer': 'B', 'max_score': 2},
]

# 多选题库
multiple_questions = [
    {'question_type': 'multiple', 'question_text': '以下哪些是 Python 的内置数据类型？', 'options': ['A. list', 'B. dict', 'C. set', 'D. array'], 'answer': ['A', 'B', 'C'], 'max_score': 4},
    {'question_type': 'multiple', 'question_text': '以下哪些是有效的 Python 标识符？', 'options': ['A. _name', 'B. 2name', 'C. name_2', 'D. class'], 'answer': ['A', 'C'], 'max_score': 4},
    {'question_type': 'multiple', 'question_text': 'Python 中哪些方法可以用于字符串格式化？', 'options': ['A. % 操作符', 'B. format()', 'C. f-string', 'D. concat()'], 'answer': ['A', 'B', 'C'], 'max_score': 4},
    {'question_type': 'multiple', 'question_text': '以下哪些是 Python 的魔术方法？', 'options': ['A. __init__', 'B. __str__', 'C. __main__', 'D. __repr__'], 'answer': ['A', 'B', 'D'], 'max_score': 4},
    {'question_type': 'multiple', 'question_text': 'Python 中可用于文件操作的方法有？', 'options': ['A. read()', 'B. write()', 'C. open()', 'D. close()'], 'answer': ['A', 'B', 'C', 'D'], 'max_score': 4},
    {'question_type': 'multiple', 'question_text': '以下哪些是 Python 的迭代器工具？', 'options': ['A. map()', 'B. filter()', 'C. reduce()', 'D. sort()'], 'answer': ['A', 'B', 'C'], 'max_score': 4},
    {'question_type': 'multiple', 'question_text': 'Python 中用于并发编程的模块有？', 'options': ['A. threading', 'B. multiprocessing', 'C. asyncio', 'D. os'], 'answer': ['A', 'B', 'C'], 'max_score': 4},
    {'question_type': 'multiple', 'question_text': '以下哪些数据库支持 Python？', 'options': ['A. SQLite', 'B. MySQL', 'C. PostgreSQL', 'D. MongoDB'], 'answer': ['A', 'B', 'C', 'D'], 'max_score': 4},
    {'question_type': 'multiple', 'question_text': 'Python 中属于序列类型的有？', 'options': ['A. str', 'B. list', 'C. tuple', 'D. dict'], 'answer': ['A', 'B', 'C'], 'max_score': 4},
]

# 简答题库
essay_questions = [
    {'question_type': 'essay', 'question_text': '请简述 Python 中的装饰器是什么，以及它的作用和使用场景。', 'options': [], 'answer': None, 'max_score': 15},
    {'question_type': 'essay', 'question_text': '请解释 Python 中的生成器（Generator）和迭代器（Iterator）的区别，并说明各自的使用场景。', 'options': [], 'answer': None, 'max_score': 15},
    {'question_type': 'essay', 'question_text': '请描述 Python 中的内存管理机制，包括垃圾回收的原理。', 'options': [], 'answer': None, 'max_score': 15},
]

count = 0

# 创建单选题
print("创建单选题...")
for q in single_questions:
    r = requests.post(f'{BASE_URL}/questions', json=q, headers=headers)
    if r.status_code == 201:
        count += 1
print(f"已创建 {count} 道单选题")

# 创建多选题
count = 0
print("创建多选题...")
for q in multiple_questions:
    r = requests.post(f'{BASE_URL}/questions', json=q, headers=headers)
    if r.status_code == 201:
        count += 1
print(f"已创建 {count} 道多选题")

# 创建简答题
count = 0
print("创建简答题...")
for q in essay_questions:
    r = requests.post(f'{BASE_URL}/questions', json=q, headers=headers)
    if r.status_code == 201:
        count += 1
print(f"已创建 {count} 道简答题")

print("\n所有题目创建完成！")
print("现在可以访问 http://localhost:5000/exam 开始考试了")
