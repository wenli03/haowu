# Skill: AI 自动营销 - 数据看板

## 触发命令

/dashboard

## 功能

展示今日营销数据和预估收益。

## 执行脚本

```python
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from engines.db import Database

db = Database('data/autopilot.db')
stats = db.get_stats()

print("=" * 40)
print("  AI 自动营销 数据看板")
print("=" * 40)
print(f"
 内容引擎:")
print(f"  待审核文章: {stats['draft_articles']}")
print(f"  已发布文章: {stats['published_articles']}")
print(f"  预估日流量: {stats['published_articles'] * 100} 次")
print(f"  预估佣金: {stats['published_articles'] * 5} - {stats['published_articles'] * 50}元/天")
print(f"
 线索引擎:")
print(f"  待审核线索: {stats['pending_leads']}")
print(f"  已发送触达: {stats['sent_leads']}")
conversions = stats['sent_leads'] * 0.05
print(f"  预估转化: {conversions:.1f} 单")
print(f"  预估收入: {conversions * 500:.0f} - {conversions * 3000:.0f}元")

db.close()
```
