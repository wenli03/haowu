# Skill: AI 自动营销 - 配置管理

## 触发命令

/config

## 功能

查看和修改系统配置。

## 查看当前配置

```python
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from engines.config import Config

config = Config('data/config.yaml')
print("当前配置:")
print(f"  关注领域: {config.get('niches')}")
print(f"  目标城市: {config.get('lead_cities')}")
print(f"  目标行业: {config.get('lead_industries')}")
print(f"  每日文章数: {config.get('articles_per_day')}")
print(f"  每城市线索数: {config.get('leads_per_city')}")
```

## 修改配置

直接编辑 `data/config.yaml` 文件：

- `niches`: 内容关注领域列表
- `lead_cities`: 线索挖掘目标城市
- `lead_industries`: 线索挖掘目标行业
- `articles_per_day`: 每日生成文章数量
- `leads_per_city`: 每个城市每日线索数
- `api.llm_endpoint`: LLM API 地址（接入真实LLM后配置）
- `api.llm_api_key`: LLM API 密钥
