---
name: ai-auto-marketing-review
description: AI自动营销审核中心 - 查看、批准、修改、丢弃待发布的文章和待发送的线索
---

# AI 自动营销审核中心

审核双引擎产出的文章和线索。

## 使用方式

```
/review
```

## 执行流程

1. 运行 `python engines/scheduler.py` 确保最新数据已生成
2. 运行以下审核脚本展示待审核队列
3. 逐条展示，用户选择操作

## 审核脚本

```python
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from engines.db import Database
from engines.config import Config

db = Database('data/autopilot.db')
config = Config('data/config.yaml')

while True:
    articles = db.get_pending_articles()
    leads = db.get_pending_leads()

    print("=" * 50)
    print("AI 自动营销审核中心")
    print("=" * 50)

    if articles:
        print(f"\n待审核文章 ({len(articles)}篇):\n")
        for a in articles:
            print(f"  [{a['id']}] {a['title']}")
            print(f"      关键词: {a['keywords']}")
            print(f"      来源: {a.get('source_trend', 'N/A')}")
            print()
    else:
        print("\n暂无待审核文章")

    if leads:
        print(f"\n待审核线索 ({len(leads)}条) - 按评分降序:\n")
        for l in leads[:10]:
            print(f"  [{l['id']}] {l['business_name']} | {l['industry']} | {l['city']}")
            print(f"      评分: {l['score']} | 机会: {l['opportunity']}")
            print()
    else:
        print("\n暂无待审核线索")

    print("\n操作命令:")
    print("  /view article <id>   - 查看文章全文")
    print("  /approve article <id> - 批准发布文章")
    print("  /reject article <id>  - 丢弃文章")
    print("  /view lead <id>      - 查看线索详情+触达文案")
    print("  /approve lead <id>   - 批准发送线索")
    print("  /reject lead <id>    - 丢弃线索")
    print("  /approve all         - 一键批准全部")
    print("  /quit                - 退出审核")

    cmd = input("\n请输入命令: ").strip()

    if cmd.startswith('/quit'):
        break
    elif cmd.startswith('/approve all'):
        for a in articles:
            db.approve_article(a['id'])
        for l in leads:
            db.approve_lead(l['id'])
        print(f"已批准 {len(articles)} 篇文章 + {len(leads)} 条线索")
    elif cmd.startswith('/approve article'):
        aid = int(cmd.split()[-1])
        db.approve_article(aid)
        print(f"文章 {aid} 已批准")
    elif cmd.startswith('/reject article'):
        aid = int(cmd.split()[-1])
        db.reject_article(aid)
        print(f"文章 {aid} 已丢弃")
    elif cmd.startswith('/view article'):
        aid = int(cmd.split()[-1])
        a = db.get_article(aid)
        if a:
            print("\n" + "="*50)
            print(a['content'])
            print("="*50 + "\n")
    elif cmd.startswith('/approve lead'):
        lid = int(cmd.split()[-1])
        db.approve_lead(lid)
        print(f"线索 {lid} 已批准")
    elif cmd.startswith('/reject lead'):
        lid = int(cmd.split()[-1])
        db.reject_lead(lid)
        print(f"线索 {lid} 已丢弃")
    elif cmd.startswith('/view lead'):
        lid = int(cmd.split()[-1])
        l = db.get_lead(lid)
        if l:
            print("\n" + "="*50)
            print(f"商家: {l['business_name']}")
            print(f"行业: {l['industry']} | 城市: {l['city']}")
            print(f"评分: {l['score']} | 机会: {l['opportunity']}")
            print(f"\n触达文案:\n{l['outreach_text']}")
            print("="*50 + "\n")

db.close()
print("审核结束。运行 /dashboard 查看最新数据。")
```
