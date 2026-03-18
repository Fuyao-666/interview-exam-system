"""
简单的 API 测试脚本
"""
# -*- coding: utf-8 -*-
import requests
import json
import sys

# 确保输出使用 UTF-8
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

BASE_URL = 'http://localhost:5000/api'

def test_login():
    """测试登录"""
    print("=== 测试登录 ===")
    response = requests.post(f'{BASE_URL}/auth/login', json={
        'username': 'admin',
        'password': 'admin123'
    })
    
    if response.status_code == 200:
        data = response.json()
        print("[OK] 登录成功")
        print(f"  用户：{data['user']['username']}")
        print(f"  角色：{data['user']['role']}")
        return data['access_token']
    else:
        print(f"[FAIL] 登录失败：{response.status_code}")
        return None

def test_get_config(token):
    """测试获取考试配置"""
    print("\n=== 测试获取考试配置 ===")
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(f'{BASE_URL}/exam/config', headers=headers)
    
    if response.status_code == 200:
        config = response.json()
        print("[OK] 获取配置成功")
        print(f"  单选题：{config['single_count']}道，每题{config['single_score']}分")
        print(f"  多选题：{config['multiple_count']}道，每题{config['multiple_score']}分")
        print(f"  简答题：{config['essay_count']}道，每题{config['essay_score']}分")
        print(f"  考试时长：{config['duration_minutes']}分钟")
        return config
    else:
        print(f"[FAIL] 获取配置失败：{response.status_code}")
        return None

def test_create_question(token):
    """测试创建题目"""
    print("\n=== 测试创建题目 ===")
    headers = {'Authorization': f'Bearer {token}'}
    
    # 创建单选题
    question_data = {
        'question_type': 'single',
        'question_text': 'Python 中哪个关键字用于定义函数？',
        'options': ['A. function', 'B. def', 'C. define', 'D. func'],
        'answer': 'B',
        'max_score': 2
    }
    
    response = requests.post(f'{BASE_URL}/questions', json=question_data, headers=headers)
    
    if response.status_code == 201:
        data = response.json()
        print(f"[OK] 创建题目成功 (ID: {data['id']})")
        return data['id']
    else:
        print(f"[FAIL] 创建题目失败：{response.status_code}")
        print(response.text)
        return None

def test_start_exam():
    """测试开始考试"""
    print("\n=== 测试候选人开始考试 ===")
    
    response = requests.post(f'{BASE_URL}/candidate/start', json={
        'name': '测试考生',
        'phone': '13800138000',
        'position': 'Python 开发工程师'
    })
    
    if response.status_code == 200:
        data = response.json()
        print("[OK] 开始考试成功")
        print(f"  试卷 ID: {data['paper_id']}")
        print(f"  考生 ID: {data['candidate_id']}")
        print(f"  是否恢复考试：{data['resume']}")
        return data['paper_id']
    else:
        print(f"[FAIL] 开始考试失败：{response.status_code}")
        print(response.text)
        return None

def test_get_paper(paper_id):
    """测试获取试卷"""
    print("\n=== 测试获取试卷 ===")
    
    response = requests.get(f'{BASE_URL}/exam/paper/{paper_id}')
    
    if response.status_code == 200:
        data = response.json()
        print("[OK] 获取试卷成功")
        print(f"  题目数量：{len(data['questions'])}")
        print(f"  开始时间：{data['start_time']}")
        
        # 显示题目类型分布
        types = {}
        for q in data['questions']:
            t = q['question_type']
            types[t] = types.get(t, 0) + 1
        
        print(f"  题型分布：{types}")
        return data
    else:
        print(f"[FAIL] 获取试卷失败：{response.status_code}")
        print(response.text)
        return None

def main():
    """主函数"""
    print("面试考试系统 - API 测试\n")
    
    # 1. 登录
    token = test_login()
    if not token:
        print("\n[FAIL] 测试终止：无法登录")
        return
    
    # 2. 获取配置
    test_get_config(token)
    
    # 3. 创建题目
    question_id = test_create_question(token)
    
    # 4. 开始考试
    paper_id = test_start_exam()
    
    # 5. 获取试卷
    if paper_id:
        test_get_paper(paper_id)
    
    print("\n=== 测试完成 ===")
    print("\n提示:")
    print("- 访问 http://localhost:5000/exam 可以体验候选人答题界面")
    print("- 访问 http://localhost:5000/login 可以体验面试官/管理员后台")

if __name__ == '__main__':
    main()
