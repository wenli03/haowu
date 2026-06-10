# Skill: AI 自动营销 - 审核中心

## 触发命令

/review

## 功能

审核待发布的文章和待发送的线索。读取数据库中 `status='draft'` 的文章和 `status='pending'` 的线索，逐条展示。

## 执行脚本

```python
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from engines.db import Database

db = Database('data/autopilot.db')

# 待审核文章
articles = db.get_pending_articles()
if articles:
    print(f"
 待审核文章 ({len(articles)}篇):
")
    for a in articles:
        print(f"  [{a['id']}] {a['title']}")
        print(f"      关键词: {a['keywords']} | 来源: {a.get('source_trend', 'N/A')}")
else:
    print("  暂无待审核文章")

# 待审核线索
leads = db.get_pending_leads()
if leads:
    print(f"
 待审核线索 ({len(leads)}条):
")
    for l in leads[:15]:
        print(f"  [{l['id']}] {l['business_name']} | {l['industry']} | {l['city']}")
        print(f"      评分: {l['score']} | 机会: {l['opportunity']}")
else:
    print("  暂无待审核线索")

db.close()
```

## 操作

**文章操作：**
- `/view article <id>` — 查看全文
- `/approve article <id>` — 批准发布
- `/edit article <id>` — 修改内容后批准
- `/reject article <id>` — 丢弃

**线索操作：**
- `/view lead <id>` — 查看详情和触达文案
- `/approve lead <id>` — 批准发送
- `/reject lead <id>` — 丢弃
