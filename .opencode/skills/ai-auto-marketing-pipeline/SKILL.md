---
name: ai-auto-marketing-pipeline
description: AI自动营销流水线 - 一键运行双引擎生成文章和线索
---

# AI 自动营销流水线

一键运行内容引擎和线索引擎，生成文章草稿和线索列表。

## 使用方式

```
/pipeline
```

## 执行脚本

```python
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from engines.config import Config
from engines.db import Database
from engines.llm_client import LLMClient
from engines.scheduler import Scheduler

config = Config('data/config.yaml')
db = Database('data/autopilot.db')

llm = LLMClient(
    api_key=config.get('llm.api_key'),
    model=config.get('llm.model', 'deepseek-ai/DeepSeek-V4-Pro')
)

scheduler = Scheduler(config, db, llm_client=llm)

print("=" * 50)
print("  AI 自动营销系统")
print("=" * 50)

result = scheduler.run()

print(f"\n状态: {result['status']}")
print(f"文章生成: {result['articles_generated']} 篇")
print(f"线索生成: {result['leads_generated']} 条")

if result['errors']:
    for err in result['errors']:
        print(f"  ! {err}")

report = scheduler.generate_report()
print(f"\n待审核: {report['articles']['draft']} 篇文章 + {report['leads']['pending']} 条线索")
print("运行 /review 开始审核")

db.close()
```
