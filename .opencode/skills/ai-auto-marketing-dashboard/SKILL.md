---
name: ai-auto-marketing-dashboard
description: AI自动营销数据看板 - 展示今日文章、线索、预估收益
---

# AI 自动营销数据看板

展示双引擎今日产出和预估收益。

## 使用方式

```
/dashboard
```

## 执行脚本

```python
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from engines.db import Database
from engines.config import Config

db = Database('data/autopilot.db')
config = Config('data/config.yaml')
stats = db.get_stats()

# 计数全部（含历史和今日）
total_draft = stats['draft_articles']
total_published = stats['published_articles']
total_pending_leads = stats['pending_leads']
total_sent = stats['sent_leads']

print("=" * 45)
print("  AI 自动营销 数据看板")
print("=" * 45)

print(f"\n内容引擎:")
print(f"  待审核文章: {total_draft}")
print(f"  已发布文章: {total_published}")

# 预估流量和收入
niches = config.get('niches', [])
est_traffic_per_article = 100
est_commission_low = 5
est_commission_high = 50
print(f"  预估日流量: {total_published * est_traffic_per_article} 次")
print(f"  预估日佣金: {total_published * est_commission_low} - {total_published * est_commission_high}元")

print(f"\n线索引擎:")
print(f"  待审核线索: {total_pending_leads}")
print(f"  已发送触达: {total_sent}")

conversion_rate = 0.05
conversions = total_sent * conversion_rate
service_low = 500
service_high = 3000
print(f"  预估转化: {conversions:.1f} 单 (按{conversion_rate*100:.0f}%转化率)")
print(f"  预估服务收入: {conversions * service_low:.0f} - {conversions * service_high:.0f}元")

print(f"\n预估月收入:")
monthly_commission = (total_published * est_commission_low * 30) if total_published > 0 else 0
monthly_service = (total_sent * conversion_rate * service_low) if total_sent > 0 else 0
total_monthly = monthly_commission + monthly_service
print(f"  联盟佣金: {monthly_commission:.0f}元/月")
print(f"  线索服务: {monthly_service:.0f}元/月")
print(f"  合计预估: {total_monthly:.0f}元/月")

print(f"\n配置信息:")
print(f"  关注领域: {', '.join(niches)}")
lead_cities = config.get('lead_cities', [])
lead_industries = config.get('lead_industries', [])
print(f"  目标城市: {', '.join(lead_cities)}")
print(f"  目标行业: {', '.join(lead_industries)}")
print(f"  每日文章数: {config.get('articles_per_day', 3)}")
print(f"  每城市线索数: {config.get('leads_per_city', 5)}")

db.close()
```
