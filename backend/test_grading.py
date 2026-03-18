"""
批阅流程演示脚本

使用方法：
1. 启动后端：python app.py
2. 在浏览器访问 http://localhost:5000/login
3. 使用管理员账号登录（默认 admin/123456）
4. 切换到面试官角色，或直接用面试官账号登录
5. 点击"试卷批阅"进入批阅页面

批阅步骤：
==========

【方式一：通过面试官后台】
1. 登录系统（面试官账号）
2. 点击左侧菜单"试卷批阅"
3. 在待批阅列表中，找到要批阅的试卷
4. 点击"开始批阅"按钮
5. 查看考生信息（姓名、岗位、客观题得分、切屏次数）
6. 逐题批阅简答题：
   - 阅读题目和考生答案
   - 输入得分（0 到满分之间）
   - 可选：输入批注
7. 在底部"总体评价"输入框填写总评
8. 确认总分无误后，点击"提交批阅"
9. 系统返回待批阅列表，该试卷已消失（批阅完成）

【方式二：通过管理员后台】
1. 登录系统（管理员账号）
2. 点击"成绩档案"标签
3. 找到状态为"待批阅"的试卷
4. 记录考生信息（需要手动批阅时切换到面试官角色）

评分说明：
=========
- 客观题（单选/多选）：系统自动评分
- 主观题（简答）：需要人工评分
- 总分 = 客观题得分 + 主观题得分总和

防作弊提示：
===========
- 切屏次数 > 0 时会显示警告标识
- 切屏 3 次及以上会被强制交卷
- 批阅时可参考切屏次数给出适当评价

API 接口说明：
============
GET  /review/pending          # 获取待批阅列表
GET  /exam/paper/{id}         # 获取试卷详情（含答题记录）
POST /review/grade            # 提交批阅结果

批阅数据结构示例：
{
  "paper_id": 1,
  "subjective_scores": [
    {"answer_id": 1, "score": 12, "comment": "回答完整"},
    {"answer_id": 2, "score": 8, "comment": "思路清晰但不够深入"}
  ],
  "grader_comment": "基础知识扎实，表达能力良好"
}
"""

if __name__ == '__main__':
    print(__doc__)
    
    # 检查数据库状态
    from app import db, app
    
    with app.app_context():
        from models import ExamPaper, Answer, Question
        
        # 统计各状态试卷数量
        total = ExamPaper.query.count()
        submitted = ExamPaper.query.filter_by(status='submitted').count()
        graded = ExamPaper.query.filter_by(status='graded').count()
        
        print(f"\n📊 当前数据库状态:")
        print(f"   总试卷数：{total}")
        print(f"   待批阅：{submitted}")
        print(f"   已批阅：{graded}")
        
        if submitted == 0:
            print(f"\n⚠️  暂无待批阅试卷")
            print(f"   请先让候选人完成考试并提交试卷")
            print(f"   访问地址：http://localhost:5000/exam")
        else:
            print(f"\n✅ 有待批阅试卷，可以开始批阅")
            print(f"   访问地址：http://localhost:5000/interviewer/review")
