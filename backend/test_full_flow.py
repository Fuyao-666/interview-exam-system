"""测试获取试卷和提交"""
import requests
import json

# 获取试卷
paper_id = 4
resp = requests.get(f'http://localhost:5000/api/exam/paper/{paper_id}')
print(f'Get paper status: {resp.status_code}')
data = resp.json()
print(f'Candidate: {data.get("candidate_name")}')
print(f'Duration: {data.get("duration_minutes")} min')
print(f'Total questions: {len(data["questions"])}')

# 统计题型
type_counts = {}
for q in data['questions']:
    t = q['question_type']
    type_counts[t] = type_counts.get(t, 0) + 1
    
print(f'Question types: {type_counts}')

# 打分统计
type_scores = {}
for q in data['questions']:
    t = q['question_type']
    type_scores[t] = type_scores.get(t, 0) + q['max_score']
print(f'Score by type: {type_scores}')
print(f'Total score: {sum(type_scores.values())}')

# 展示每题信息
print('\n--- Questions ---')
for i, q in enumerate(data['questions']):
    text_preview = q['question_text'][:50] + '...' if len(q['question_text']) > 50 else q['question_text']
    print(f'{i+1}. [{q["question_type"]}] ({q["max_score"]}pts) {text_preview}')

# 模拟提交答案
answers = []
for q in data['questions']:
    if q['question_type'] in ('single', 'multiple'):
        # 选择题随机选A
        answers.append({'question_id': q['id'], 'answer_content': 'A'})
    else:
        answers.append({'question_id': q['id'], 'answer_content': 'This is my test answer for the question.'})

resp2 = requests.post('http://localhost:5000/api/exam/submit', json={
    'paper_id': paper_id,
    'answers': answers,
    'screen_focus_loss_count': 0
})
print(f'\nSubmit status: {resp2.status_code}')
print(json.dumps(resp2.json(), indent=2, ensure_ascii=False))

# 测试月度次数限制 - 尝试第2、3、4次
for i in range(3):
    resp3 = requests.post('http://localhost:5000/api/candidate/start', json={
        'name': 'zhangsan',
        'phone': '13800138000',
        'company': 'TestCo'
    })
    print(f'\nAttempt {i+2}: Status {resp3.status_code} - {resp3.json().get("error", resp3.json().get("paper_id", "OK"))}')
