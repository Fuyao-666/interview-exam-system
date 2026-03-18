"""测试候选人开始考试"""
import requests
import json

resp = requests.post('http://localhost:5000/api/candidate/start', json={
    'name': 'zhangsan',
    'phone': '13800138000',
    'company': 'TestCo'
})
print(f'Status: {resp.status_code}')
print(json.dumps(resp.json(), indent=2, ensure_ascii=False))
