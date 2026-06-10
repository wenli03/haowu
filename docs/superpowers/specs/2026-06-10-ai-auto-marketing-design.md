# AI 自动营销系统 - 设计规格

## 概述

基于 Python 自动化脚本 + OpenCode Skill 审核层的混合系统，实现两个并行赚钱引擎：
- **内容联盟引擎**：AI生成SEO文章 + 自动插入联盟链接（Amazon/京东/淘宝），靠佣金变现
- **线索引擎**：AI爬取商家线索 + 生成触达文案，靠建站/代运营/线索转卖变现

## 系统架构

```
定时调度层 (Windows Task Scheduler)
    │
    ├── 内容引擎 (每天执行)
    │   ├── 热点追踪 → 关键词挖掘 → AI生成文章 → 联盟链接插入
    │   └── 输出: drafts/articles/
    │
    └── 线索引擎 (每天执行)
        ├── 线索爬取 → 信息补全 → 质量评分 → 触达文案生成
        └── 输出: drafts/leads/
        
审核层 (OpenCode Skills)
    ├── /review    → 审核文章和线索
    ├── /dashboard → 数据看板
    └── /config    → 配置管理
```

## 项目结构

```
pro12/
├── engines/                    # Python 自动化引擎
│   ├── content_engine/
│   │   ├── trend_tracker.py    # 热点追踪
│   │   ├── keyword_research.py # 关键词挖掘
│   │   ├── article_generator.py# AI文章生成
│   │   └── affiliate_linker.py # 联盟链接匹配与插入
│   ├── lead_engine/
│   │   ├── lead_scraper.py     # 线索爬取
│   │   ├── lead_enricher.py    # 信息补全+评分
│   │   └── outreach_gen.py     # 触达文案生成
│   └── scheduler.py            # 定时任务入口
├── skills/                     # OpenCode Skills
│   ├── review.md               # /review 审核命令
│   ├── dashboard.md            # /dashboard 数据看板
│   └── config.md               # /config 配置命令
├── drafts/                     # 审核队列
│   ├── articles/               # 待审文章
│   └── leads/                  # 待审线索
├── data/
│   ├── autopilot.db            # SQLite 数据库
│   └── config.yaml             # 配置文件
└── requirements.txt            # Python 依赖
```

## 模块详述

### 1. 内容联盟引擎

| 模块 | 功能 | 输入 | 输出 |
|------|------|------|------|
| trend_tracker | 从知乎/微博/Google Trends抓热点 | 关注的关键词niche | 热点话题列表 |
| keyword_research | 根据热点扩展长尾关键词 | 热点话题 | 关键词+搜索量+竞争度 |
| article_generator | 用LLM生成SEO优化文章 | 关键词+niche | 1000-3000字Markdown文章 |
| affiliate_linker | 自动匹配联盟商品并插入链接 | 文章内容+联盟平台 | 带链接的文章 |

**支持的联盟平台**：Amazon Associates、京东联盟、淘宝联盟

### 2. 线索引擎

| 模块 | 功能 | 输入 | 输出 |
|------|------|------|------|
| lead_scraper | 从Google Maps等爬取商家 | 城市+行业 | 商家列表 |
| lead_enricher | AI分析补全信息并打分 | 商家列表 | 带评分和机会标签的线索 |
| outreach_gen | 生成个性化触达文案 | 高分线索 | 邮件/微信话术 |

**变现方式**：建站服务、代运营、线索转卖

### 3. 数据库设计 (SQLite)

**articles 表**：id, title, content, keywords, affiliate_links, status, created_at, published_at
**leads 表**：id, business_name, industry, city, contact, score, opportunity, status, created_at
**config 表**：key, value (存储niche、API密钥等)

### 4. OpenCode Skills

- `/review`：展示待审队列，支持查看/修改/批准/丢弃
- `/dashboard`：今日发布数、线索数、预估收益
- `/config`：配置niche、关键词、联盟账号

## 技术栈

| 用途 | 技术 |
|------|------|
| 自动化脚本 | Python 3.10+ |
| HTTP请求 | requests, httpx |
| 页面解析 | beautifulsoup4, lxml |
| 数据库 | sqlite3 |
| LLM调用 | 通过现有API（opencode环境） |
| 定时任务 | Windows Task Scheduler |
| 联盟API | Amazon PAAPI / 京东联盟SDK |

## 工作流

1. 每天早上 Windows Task Scheduler 触发 scheduler.py
2. scheduler.py 按序执行内容引擎和线索引擎
3. 生成的文章和线索存入 drafts/ 目录
4. 用户运行 `/review` 审核并批准
5. 批准的文章通过 WordPress API / 手动发布
6. 批准的线索通过邮件/微信发送
7. 运行 `/dashboard` 查看当天数据

## 每日投入时间

- 自动执行：全自动，约5-10分钟
- 人工审核：10-15分钟
- 总计：约15-25分钟/天
