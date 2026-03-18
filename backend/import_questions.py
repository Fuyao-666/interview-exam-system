"""
从 Excel 导入 Python 选择题到系统题库
"""
import json
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from app import app, db
from models import Question

questions_data = [
    {
        "text": "下列哪个语句在Python中是非法的？",
        "options": ["A. x = y = z = 1", "B. x = (y = z + 1)", "C. x, y = y, x", "D. x  +=  y"],
        "answer": "B"
    },
    {
        "text": "关于Python内存管理，下列说法错误的是",
        "options": ["A. 变量不必事先声明", "B. 变量无须先创建和赋值而直接使用", "C. 变量无须指定类型", "D. 可以使用del释放资源"],
        "answer": "B"
    },
    {
        "text": "以下不能创建一个字典的语句是",
        "options": ["A. dict1 = {}", "B. dict2 = { 3 : 5 }", 'C. dict3 = {[1,2,3]: "uestc"}', 'D. dict4 = {(1,2,3): "uestc"}'],
        "answer": "C"
    },
    {
        "text": "python 代码执行的方式",
        "options": ["A. 编译执行", "B. 解析执行", "C. 直接执行", "D. 边编译边执行"],
        "answer": "B"
    },
    {
        "text": "调用以下函数返回的值\ndef myfun():\n    pass",
        "options": ["A. 0", "B. 出错不能运行", "C. 空字符串", "D. None"],
        "answer": "D"
    },
    {
        "text": "导入模块的方式错误的是",
        "options": ["A. import mo", "B. from mo import *", "C. import mo as m", "D. import m from mo"],
        "answer": "D"
    },
    {
        "text": "以下关于模块说法错误的是",
        "options": ["A. 一个xx.py就是一个模块", "B. 任何一个普通的xx.py文件可以作为模块导入", "C. 模块文件的扩展名不一定是 .py", "D. 运行时会从指定的目录搜索导入的模块，如果没有，会报错异常"],
        "answer": "C"
    },
    {
        "text": "关于Python循环结构，以下选项中描述错误的是",
        "options": ["A. 每个continue语句只有能力跳出当前层次的循环", "B. break用来跳出最内层for或者while循环，脱离该循环后程序从循环代码后继续执行", "C. 遍历循环中的遍历结构可以是字符串、文件、组合数据类型和range()函数等", "D. Python通过for、while等保留字提供遍历循环和无限循环结构"],
        "answer": "A"
    },
    {
        "text": "关于Python的lambda函数，以下选项中描述错误的是",
        "options": ["A. lambda函数将函数名作为函数结果返回", "B. f = lambda x,y:x+y 执行后，f的类型为数字类型", "C. lambda用于定义简单的、能够在一行内表示的函数", "D. 可以使用lambda函数定义列表的排序原则"],
        "answer": "B"
    },
    {
        "text": '给出如下代码，下述代码的输出结果是\ns = "Alice"\nprint(s[::–1]',
        "options": ["A. ALICE", "B. ecilA", "C. Alic", "D. Alice"],
        "answer": "B"
    },
    {
        "text": "在Python中，关于全局变量和局部变量，以下选项中描述不正确的是",
        "options": ["A. 一个程序中的变量包含两类：全局变量和局部变量", "B. 全局变量不能和局部变量重名", "C. 全局变量一般没有缩进", "D. 全局变量在程序执行的全过程有效"],
        "answer": "B"
    },
    {
        "text": "下面代码的输出结果是\ndict = {'a': 1, 'b': 2, 'b': '3'};\ntemp = dict['b']\nprint(temp)",
        "options": ["A. 1", "B. { 'b' : 2 }", "C. 3", "D. 2"],
        "answer": "C"
    },
    {
        "text": "关于函数的可变参数，可变参数*args传入函数时存储的类型是",
        "options": ["A. dict", "B. tuple", "C. list", "D. set"],
        "answer": "B"
    },
    {
        "text": "以下不能创建一个字典的语句是",
        "options": ["A. dic1 = {}", "B. dic2 = {123:345}", "C. dic3 = {[1,2,3]:'uestc'}", "D. dic3 = {(1,2,3):'uestc'}"],
        "answer": "C"
    },
    {
        "text": "下面的语句哪个会无限循环下去",
        "options": ["A. for a in range(10):\\n    time.sleep(10)", "B. while 1<10:\\n    time.sleep(10)", "C. while True:\\n    break", "D. a = [3,-1,',']\\nfor i in a[:]:\\n       if not a: break"],
        "answer": "B"
    },
    {
        "text": "以下关于循环结构的描述，错误的是",
        "options": ["A. 遍历循环使用for <循环变量> in <循环结构>语句，其中循环结构不能是文件", "B. 使用range()函数可以指定for循环的次数", "C. for i in range(5)表示循环5次，i的值是从0到4", "D. 用字符串做循环结构的时候，循环的次数是字符串的长度"],
        "answer": "A"
    },
    {
        "text": "关于 Python 的分支结构，以下选项中描述错误的是",
        "options": ["A. 分支结构使用 if 保留字", "B. Python 中 if-else 语句用来形成二分支结构", "C. Python 中 if-elif-else 语句描述多分支结构", "D. 分支结构可以向已经执行过的语句部分跳转"],
        "answer": "D"
    },
    {
        "text": '以下语句执行后a、b、c的值是\na = "watermelon"\nb = "strawberry"\nc = "cherry"\nif a > b:\n    c = a\n    a = b\n    b = c',
        "options": ["A. watermelon strawberry cherry", "B. watermelon cherry strawberry", "C. strawberry cherry watermelon", "D. strawberry watermelon watermelon"],
        "answer": "D"
    },
    {
        "text": "以下代码的输出结果是什么？\n\ndef func(x, lst=[]):\n    lst.append(x)\n    return lst\n\na = func(1)\nb = func(2)\nprint(a, b)",
        "options": ["A. [1] [2]", "B. [1] [1, 2]", "C. [1, 2] [1, 2]", "D. [1, 2] [2]"],
        "answer": "C"
    },
    {
        "text": "以下代码的输出结果是什么？\n\ndata = {'a': 1, 'b': 2, 'c': 3}\nfor key in data:\n    if data[key] % 2 == 0:\n        data[key] = data[key] * 2\n    else:\n        data[key] = data[key] + 1\n\nprint(data)",
        "options": ["A. {'a': 2, 'b': 4, 'c': 2}", "B. {'a': 2, 'b': 4, 'c': 3}", "C. {'a': 2, 'b': 4, 'c': 4}", "D. {'a': 1, 'b': 4, 'c': 3}"],
        "answer": "C"
    }
]

with app.app_context():
    count = 0
    for q in questions_data:
        question = Question(
            question_type='single',
            question_text=q['text'],
            options=json.dumps(q['options'], ensure_ascii=False),
            answer=json.dumps(q['answer'], ensure_ascii=False),
            max_score=2,
            created_by=1
        )
        db.session.add(question)
        count += 1
    
    db.session.commit()
    
    total = Question.query.filter_by(question_type='single').count()
    print(f"SUCCESS: imported {count} questions, total single-choice questions in DB: {total}")
