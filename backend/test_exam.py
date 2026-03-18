# -*- coding: utf-8 -*-
"""测试完整考试流程"""
import requests
from datetime import datetime

BASE_URL = 'http://localhost:5000/api'

print("=" * 60)
print("面试考试系统 - 完整流程测试")
print("=" * 60)

# 1. 考生开始考试
print("\n[步骤 1] 考生开始考试")
response = requests.post(f'{BASE_URL}/candidate/start', json={
    'name': '张三',
    'phone': '13800138000',
    'position': 'Python 开发工程师'
})

if response.status_code != 200:
    print(f"失败：{response.status_code}")
    print(response.text)
    exit(1)

exam_data = response.json()
paper_id = exam_data['paper_id']
print(f"OK - 试卷 ID: {paper_id}")
print(f"   考生 ID: {exam_data['candidate_id']}")
print(f"   恢复考试：{exam_data['resume']}")

# 2. 获取试卷
print("\n[步骤 2] 获取试卷内容")
response = requests.get(f'{BASE_URL}/exam/paper/{paper_id}')
if response.status_code != 200:
    print(f"失败：{response.status_code}")
    exit(1)

paper = response.json()
print(f"OK - 题目数量：{len(paper['questions'])}")

# 统计题型
types = {}
for q in paper['questions']:
    t = q['question_type']
    types[t] = types.get(t, 0) + 1

print("   题型分布:")
type_names = {'single': '单选题', 'multiple': '多选题', 'essay': '简答题'}
for t, count in types.items():
    print(f"     {type_names.get(t, t)}: {count}道")

# 3. 模拟答题
print("\n[步骤 3] 模拟答题")
answers = []
for i, q in enumerate(paper['questions']):
    if q['question_type'] == 'single':
        # 单选都选 A
        answer = 'A'
    elif q['question_type'] == 'multiple':
        # 多选都选 AB
        answer = ['A', 'B']
    else:
        # 简答
        answer = f'这是第{i+1}道简答题的答案...'
    
    answers.append({
        'question_id': q['id'],
        'answer_content': answer
    })
    
    print(f"   第{i+1}题 ({type_names.get(q['question_type'], '?')}): 已作答")

# 4. 提交试卷
print("\n[步骤 4] 提交试卷")
response = requests.post(f'{BASE_URL}/exam/submit', json={
    'paper_id': paper_id,
    'answers': answers,
    'screen_focus_loss_count': 0
})

if response.status_code != 200:
    print(f"失败：{response.status_code}")
    print(response.text)
    exit(1)

result = response.json()
print(f"OK - {result['message']}")
print(f"   客观题得分：{result['objective_score']}")

# 5. 查看待批阅列表（需要登录）
print("\n[步骤 5] 查看待批阅试卷")
login_resp = requests.post(f'{BASE_URL}/auth/login', json={
    'username': 'admin',
    'password': 'admin123'
})
token = login_resp.json()['access_token']
headers = {'Authorization': f'Bearer {token}'}

pending_resp = requests.get(f'{BASE_URL}/review/pending', headers=headers)
if pending_resp.status_code == 200:
    pending = pending_resp.json()
    print(f"OK - 待批阅试卷数：{len(pending)}")
    for p in pending:
        if p['id'] == paper_id:
            print(f"   找到刚提交的试卷：{p['candidate_name']} - 客观题{p['objective_score']}分")
else:
    print("无法获取待批阅列表")

print("\n" + "=" * 60)
print("测试完成!")
print("=" * 60)
print(f"\n提示:")
print(f"- 考生可访问 http://localhost:5000/exam 继续答题")
print(f"- 面试官可访问 http://localhost:5000/login 登录后查看批阅")
print(f"- 本次考试的试卷 ID: {paper_id}")
