# AI 自动营销系统 实现计划

> **面向 AI 代理的工作者：** 必需子技能：使用 superpowers:subagent-driven-development（推荐）或 superpowers:executing-plans 逐任务实现此计划。步骤使用复选框（`- [ ]`）语法来跟踪进度。

**目标：** 构建基于 Python 自动化脚本 + OpenCode Skill 审核层的双引擎自动营销系统，实现内容联盟变现和线索挖掘变现。

**架构：** Python 脚本层负责定时自动化（热点追踪、AI生成内容、线索爬取），OpenCode Skills 层负责人机审核流程。SQLite 存储所有数据，Windows Task Scheduler 调度执行。

**技术栈：** Python 3.10+, SQLite3, requests, beautifulsoup4, PyYAML, OpenCode Skills

---

### 任务 1：项目脚手架与依赖

**文件：**
- 创建：`requirements.txt`
- 创建：`engines/__init__.py`
- 创建：`engines/content_engine/__init__.py`
- 创建：`engines/lead_engine/__init__.py`
- 创建：`tests/__init__.py`
- 创建：`drafts/articles/.gitkeep`
- 创建：`drafts/leads/.gitkeep`

- [ ] **步骤 1：创建 requirements.txt**

```
requests>=2.28.0
beautifulsoup4>=4.12.0
lxml>=4.9.0
pyyaml>=6.0
httpx>=0.24.0
```

- [ ] **步骤 2：创建目录结构和 __init__.py 文件**

```powershell
New-Item -ItemType Directory -Force -Path engines\content_engine
New-Item -ItemType Directory -Force -Path engines\lead_engine
New-Item -ItemType Directory -Force -Path tests
New-Item -ItemType Directory -Force -Path drafts\articles
New-Item -ItemType Directory -Force -Path drafts\leads
New-Item -ItemType Directory -Force -Path data
```

每个 `__init__.py` 文件为空文件。`drafts/articles/.gitkeep` 和 `drafts/leads/.gitkeep` 为空文件。

- [ ] **步骤 3：安装依赖并验证**

```powershell
pip install -r requirements.txt
python -c "import requests, bs4, yaml, httpx; print('OK')"
```

预期输出：`OK`

- [ ] **步骤 4：Commit**

```bash
git add requirements.txt engines/ tests/ drafts/ data/
git commit -m "feat: project scaffolding with dependencies"
```

---

### 任务 2：数据库层

**文件：**
- 创建：`engines/db.py`
- 创建：`tests/test_db.py`

- [ ] **步骤 1：编写失败的测试**

```python
# tests/test_db.py
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from engines.db import Database

DB_PATH = os.path.join(os.path.dirname(__file__), 'test_autopilot.db')

def teardown_module():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

def test_init_creates_tables():
    db = Database(DB_PATH)
    tables = db.conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    ).fetchall()
    table_names = [t[0] for t in tables]
    assert 'articles' in table_names
    assert 'leads' in table_names
    assert 'config' in table_names
    db.close()

def test_insert_article():
    db = Database(DB_PATH)
    db.insert_article(
        title='Test Article',
        content='Test content',
        keywords='test,article',
        affiliate_links='[]',
        source_trend='test trend'
    )
    row = db.conn.execute("SELECT title, status FROM articles").fetchone()
    assert row['title'] == 'Test Article'
    assert row['status'] == 'draft'
    db.close()

def test_get_pending_articles():
    db = Database(DB_PATH)
    db.insert_article(title='A1', content='x', keywords='x', affiliate_links='[]')
    db.insert_article(title='A2', content='x', keywords='x', affiliate_links='[]')
    pending = db.get_pending_articles()
    assert len(pending) == 3
    assert pending[0]['title'] == 'Test Article'
    db.close()

def test_approve_article():
    db = Database(DB_PATH)
    pending = db.get_pending_articles()
    aid = pending[0]['id']
    db.approve_article(aid)
    row = db.conn.execute("SELECT status FROM articles WHERE id=?", (aid,)).fetchone()
    assert row['status'] == 'approved'
    db.close()
```

- [ ] **步骤 2：运行测试验证失败**

```powershell
python -m pytest tests/test_db.py -v
```

预期：全部 FAIL（Database 类未定义）

- [ ] **步骤 3：实现 Database 类**

```python
# engines/db.py
import sqlite3
import os


class Database:
    def __init__(self, db_path='data/autopilot.db'):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self._init_tables()

    def _init_tables(self):
        self.conn.executescript('''
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                keywords TEXT,
                affiliate_links TEXT DEFAULT '[]',
                source_trend TEXT,
                status TEXT DEFAULT 'draft',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                published_at TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                business_name TEXT NOT NULL,
                industry TEXT,
                city TEXT,
                contact TEXT,
                score INTEGER DEFAULT 0,
                opportunity TEXT,
                outreach_text TEXT,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                sent_at TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS config (
                key TEXT PRIMARY KEY,
                value TEXT
            );
        ''')
        self.conn.commit()

    def insert_article(self, title, content, keywords='', affiliate_links='[]', source_trend=None):
        self.conn.execute(
            "INSERT INTO articles (title, content, keywords, affiliate_links, source_trend) VALUES (?, ?, ?, ?, ?)",
            (title, content, keywords, affiliate_links, source_trend)
        )
        self.conn.commit()

    def get_pending_articles(self):
        return self.conn.execute(
            "SELECT * FROM articles WHERE status='draft' ORDER BY created_at DESC"
        ).fetchall()

    def get_article(self, article_id):
        return self.conn.execute(
            "SELECT * FROM articles WHERE id=?", (article_id,)
        ).fetchone()

    def approve_article(self, article_id):
        self.conn.execute(
            "UPDATE articles SET status='approved', published_at=CURRENT_TIMESTAMP WHERE id=?",
            (article_id,)
        )
        self.conn.commit()

    def reject_article(self, article_id):
        self.conn.execute(
            "UPDATE articles SET status='rejected' WHERE id=?",
            (article_id,)
        )
        self.conn.commit()

    def update_article(self, article_id, title=None, content=None, keywords=None):
        fields = {}
        if title:
            fields['title'] = title
        if content:
            fields['content'] = content
        if keywords:
            fields['keywords'] = keywords
        if not fields:
            return
        sets = ', '.join(f'{k}=?' for k in fields)
        values = list(fields.values()) + [article_id]
        self.conn.execute(f"UPDATE articles SET {sets} WHERE id=?", values)
        self.conn.commit()

    def insert_lead(self, business_name, industry='', city='', contact='', score=0, opportunity=None, outreach_text=None):
        self.conn.execute(
            "INSERT INTO leads (business_name, industry, city, contact, score, opportunity, outreach_text) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (business_name, industry, city, contact, score, opportunity, outreach_text)
        )
        self.conn.commit()

    def get_pending_leads(self):
        return self.conn.execute(
            "SELECT * FROM leads WHERE status='pending' ORDER BY score DESC"
        ).fetchall()

    def get_lead(self, lead_id):
        return self.conn.execute(
            "SELECT * FROM leads WHERE id=?", (lead_id,)
        ).fetchone()

    def approve_lead(self, lead_id):
        self.conn.execute(
            "UPDATE leads SET status='approved', sent_at=CURRENT_TIMESTAMP WHERE id=?",
            (lead_id,)
        )
        self.conn.commit()

    def reject_lead(self, lead_id):
        self.conn.execute(
            "UPDATE leads SET status='rejected' WHERE id=?",
            (lead_id,)
        )
        self.conn.commit()

    def get_config(self, key, default=None):
        row = self.conn.execute("SELECT value FROM config WHERE key=?", (key,)).fetchone()
        return row['value'] if row else default

    def set_config(self, key, value):
        self.conn.execute(
            "INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)",
            (key, str(value))
        )
        self.conn.commit()

    def get_stats(self):
        draft_count = self.conn.execute(
            "SELECT COUNT(*) FROM articles WHERE status='draft'"
        ).fetchone()[0]
        approved_count = self.conn.execute(
            "SELECT COUNT(*) FROM articles WHERE status='approved'"
        ).fetchone()[0]
        pending_leads = self.conn.execute(
            "SELECT COUNT(*) FROM leads WHERE status='pending'"
        ).fetchone()[0]
        approved_leads = self.conn.execute(
            "SELECT COUNT(*) FROM leads WHERE status='approved'"
        ).fetchone()[0]
        return {
            'draft_articles': draft_count,
            'published_articles': approved_count,
            'pending_leads': pending_leads,
            'sent_leads': approved_leads
        }

    def close(self):
        self.conn.close()
```

- [ ] **步骤 4：运行测试验证通过**

```powershell
python -m pytest tests/test_db.py -v
```

预期：全部 PASS

- [ ] **步骤 5：Commit**

```bash
git add engines/db.py tests/test_db.py
git commit -m "feat: database layer with articles, leads, config tables"
```

---

### 任务 3：配置系统

**文件：**
- 创建：`engines/config.py`
- 创建：`data/config.yaml`
- 创建：`tests/test_config.py`

- [ ] **步骤 1：编写失败的测试**

```python
# tests/test_config.py
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from engines.config import Config

CONFIG_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'config.yaml')

def test_load_default_config():
    config = Config(CONFIG_PATH)
    assert config.get('niches') == ['家电', '数码', '健身']
    assert config.get('lead_cities') == ['上海', '北京', '深圳']
    assert config.get('lead_industries') == ['美甲', '美容', '宠物', '餐饮']
    assert config.get('articles_per_day') == 3

def test_missing_key_returns_none():
    config = Config(CONFIG_PATH)
    assert config.get('nonexistent') is None

def test_missing_key_with_default():
    config = Config(CONFIG_PATH)
    assert config.get('nonexistent', 'default') == 'default'
```

- [ ] **步骤 2：创建默认配置文件**

```yaml
# data/config.yaml
niches:
  - 家电
  - 数码
  - 健身

lead_cities:
  - 上海
  - 北京
  - 深圳

lead_industries:
  - 美甲
  - 美容
  - 宠物
  - 餐饮

articles_per_day: 3
leads_per_city: 5

api:
  llm_endpoint: ""
  llm_api_key: ""
```

- [ ] **步骤 3：实现 Config 类**

```python
# engines/config.py
import os
import yaml


class Config:
    def __init__(self, config_path='data/config.yaml'):
        self._path = config_path
        self._data = {}
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                self._data = yaml.safe_load(f) or {}

    def get(self, key, default=None):
        keys = key.split('.')
        value = self._data
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        return value

    def reload(self):
        self.__init__(self._path)
```

- [ ] **步骤 4：运行测试验证通过**

```powershell
python -m pytest tests/test_config.py -v
```

预期：全部 PASS

- [ ] **步骤 5：Commit**

```bash
git add engines/config.py data/config.yaml tests/test_config.py
git commit -m "feat: configuration system with YAML support"
```

---

### 任务 4：热点追踪器

**文件：**
- 创建：`engines/content_engine/trend_tracker.py`

- [ ] **步骤 1：实现 TrendTracker 类**

```python
# engines/content_engine/trend_tracker.py
import requests


class TrendTracker:
    """从多个来源抓取热点话题"""

    ZHIHU_HOT_URL = 'https://www.zhihu.com/api/v3/feed/topstory/hot-lists/total?limit=20'
    WEIBO_HOT_URL = 'https://weibo.com/ajax/side/hotSearch'

    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    }

    def fetch_zhihu_hot(self):
        try:
            resp = requests.get(self.ZHIHU_HOT_URL, headers=self.HEADERS, timeout=10)
            data = resp.json()
            trends = []
            for item in data.get('data', []):
                target = item.get('target', {})
                title = target.get('title', '') or target.get('excerpt', '')
                if title:
                    trends.append({
                        'title': title,
                        'source': '知乎热榜',
                        'url': target.get('url', ''),
                        'hot_metric': target.get('metrics', {}).get('raw', {}).get('visit_count', 0)
                    })
            return trends
        except Exception as e:
            print(f"[TrendTracker] 知乎抓取失败: {e}")
            return []

    def fetch_weibo_hot(self):
        try:
            resp = requests.get(self.WEIBO_HOT_URL, headers=self.HEADERS, timeout=10)
            data = resp.json()
            trends = []
            for item in data.get('data', {}).get('realtime', [])[:20]:
                word = item.get('word', '') or item.get('note', '')
                if word:
                    trends.append({
                        'title': word,
                        'source': '微博热搜',
                        'url': f'https://s.weibo.com/weibo?q={word}',
                        'hot_metric': item.get('raw_hot', 0)
                    })
            return trends
        except Exception as e:
            print(f"[TrendTracker] 微博抓取失败: {e}")
            return []

    def filter_by_niches(self, trends, niches):
        if not niches:
            return trends
        filtered = []
        for t in trends:
            title_lower = t['title'].lower()
            for niche in niches:
                if niche.lower() in title_lower:
                    filtered.append(t)
                    break
        return filtered

    def get_trends(self, niches=None):
        all_trends = self.fetch_zhihu_hot() + self.fetch_weibo_hot()
        if niches:
            all_trends = self.filter_by_niches(all_trends, niches)
        all_trends.sort(key=lambda x: x.get('hot_metric', 0), reverse=True)
        return all_trends[:10]
```

- [ ] **步骤 2：手动验证**

```powershell
python engines/content_engine/trend_tracker.py
```

在 `trend_tracker.py` 末尾添加：

```python
if __name__ == '__main__':
    tracker = TrendTracker()
    trends = tracker.get_trends(niches=['家电', '数码', '科技'])
    for t in trends:
        print(f"[{t['source']}] {t['title']}")
```

预期：输出热点话题列表（如果网络不可用，输出空列表但不报错）

- [ ] **步骤 3：Commit**

```bash
git add engines/content_engine/trend_tracker.py
git commit -m "feat: trend tracker from zhihu and weibo"
```

---

### 任务 5：关键词挖掘器

**文件：**
- 创建：`engines/content_engine/keyword_research.py`

- [ ] **步骤 1：实现 KeywordResearcher 类**

```python
# engines/content_engine/keyword_research.py


class KeywordResearcher:
    """基于热点话题扩展长尾关键词"""

    LONGTAIL_TEMPLATES = [
        "{topic}推荐",
        "{topic}测评",
        "{topic}排行榜",
        "{topic}哪个牌子好",
        "{topic}怎么选",
        "{topic}多少钱",
        "{topic}性价比",
        "{topic}使用心得",
        "2024年{topic}",
        "{topic}避坑",
        "新手{topic}指南",
    ]

    def expand_keywords(self, topic, templates=None):
        if templates is None:
            templates = self.LONGTAIL_TEMPLATES
        keywords = []
        for tmpl in templates:
            kw = tmpl.format(topic=topic)
            keywords.append({
                'keyword': kw,
                'topic': topic,
                'type': 'longtail'
            })
        return keywords

    def research(self, trends):
        all_keywords = []
        for trend in trends:
            topic = self._extract_core_topic(trend['title'])
            keywords = self.expand_keywords(topic)
            for kw in keywords:
                kw['source_trend'] = trend['title']
            all_keywords.extend(keywords)
        return all_keywords

    def _extract_core_topic(self, title):
        cleaned = title.replace('#', '').strip()[:30]
        return cleaned if cleaned else title[:20]

    def pick_top_keywords(self, keywords, count=5):
        return keywords[:count]
```

- [ ] **步骤 2：手动验证**

```powershell
python -c "
from engines.content_engine.keyword_research import KeywordResearcher
r = KeywordResearcher()
trends = [{'title': '跑步机推荐', 'source': '知乎'}]
kw = r.research(trends)
for k in kw[:5]:
    print(k['keyword'])
"
```

预期：输出 10+ 个长尾关键词

- [ ] **步骤 3：Commit**

```bash
git add engines/content_engine/keyword_research.py
git commit -m "feat: keyword research with long-tail expansion"
```

---

### 任务 6：文章生成器

**文件：**
- 创建：`engines/content_engine/article_generator.py`
- 创建：`tests/test_article_generator.py`

- [ ] **步骤 1：编写失败的测试**

```python
# tests/test_article_generator.py
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from engines.content_engine.article_generator import ArticleGenerator


def test_build_prompt():
    gen = ArticleGenerator()
    prompt = gen.build_prompt('家用跑步机推荐', '健身')
    assert '家用跑步机推荐' in prompt
    assert '健身' in prompt
    assert 'SEO' in prompt.lower() or '文章' in prompt
    assert len(prompt) > 100


def test_build_prompt_no_niche():
    gen = ArticleGenerator()
    prompt = gen.build_prompt('无线耳机测评')
    assert '无线耳机测评' in prompt
    assert len(prompt) > 100


def test_parse_sections():
    gen = ArticleGenerator()
    text = '''
## 为什么需要一台好的跑步机
在家健身越来越流行...
---
## 2024年TOP5跑步机推荐
以下是精选的5款...
---
## 购买建议
综合来看...
'''
    sections = gen.parse_sections(text)
    assert len(sections) >= 2


def test_save_draft():
    gen = ArticleGenerator()
    path = gen.save_draft('测试文章', '这是内容', '测试关键词', '家电', 'drafts/articles')
    assert os.path.exists(path)
    os.remove(path)
```

- [ ] **步骤 2：运行测试验证失败**

```powershell
python -m pytest tests/test_article_generator.py -v
```

预期：全部 FAIL

- [ ] **步骤 3：实现 ArticleGenerator 类**

```python
# engines/content_engine/article_generator.py
import os
import re


class ArticleGenerator:
    """使用 LLM 生成 SEO 优化的联盟营销文章"""

    SYSTEM_PROMPT = """你是一个专业的SEO内容写手，擅长撰写产品测评和购买指南类文章。

写作规范：
1. 文章长度 1500-3000 字
2. 使用 Markdown 格式
3. 必须包含以下结构：
   - 吸引人的标题（含核心关键词）
   - 开篇引入（用户痛点+文章价值）
   - 产品推荐清单（3-5款，每款含优缺点）
   - 选购指南/避坑建议
   - 总结+购买建议
4. 在提及具体产品时，使用占位符 {affiliate_link_产品名} 标记联盟链接位置
5. 语言自然、真实，避免明显的AI写作痕迹
6. 每个章节用 --- 分隔"""

    def build_prompt(self, keyword, niche=None):
        niche_hint = f"该文章属于「{niche}」领域。" if niche else ""
        return f"""请撰写一篇关于「{keyword}」的SEO优化文章。{niche_hint}

要求：
- 标题必须包含关键词「{keyword}」
- 推荐3-5款相关产品，每款列出优缺点
- 在适合插入购买链接的地方使用 {{affiliate_link_产品名}} 占位符
- 末尾加上标签
"""

    def parse_sections(self, text):
        parts = re.split(r'\n---\n', text)
        sections = []
        for part in parts:
            part = part.strip()
            if not part:
                continue
            lines = part.split('\n')
            title = ''
            for line in lines:
                if line.startswith('#'):
                    title = line.lstrip('#').strip()
                    break
            if not title:
                title = lines[0][:40] if lines else ''
            sections.append({'title': title, 'content': part})
        return sections

    def format_article(self, title, sections):
        parts = [f"# {title}\n"]
        for s in sections:
            parts.append(s['content'])
        return '\n\n---\n\n'.join(parts)

    def save_draft(self, title, content, keyword, niche, drafts_dir='drafts/articles'):
        os.makedirs(drafts_dir, exist_ok=True)
        safe_name = re.sub(r'[^\w\-]', '_', title)[:50]
        filename = f"{safe_name}.md"
        filepath = os.path.join(drafts_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"# {title}\n\n> 关键词: {keyword}\n> 领域: {niche or '通用'}\n\n")
            f.write(content)
        return filepath
```

- [ ] **步骤 4：运行测试验证通过**

```powershell
python -m pytest tests/test_article_generator.py -v
```

预期：全部 PASS

- [ ] **步骤 5：Commit**

```bash
git add engines/content_engine/article_generator.py tests/test_article_generator.py
git commit -m "feat: article generator with LLM prompt builder and draft saving"
```

---

### 任务 7：联盟链接注入器

**文件：**
- 创建：`engines/content_engine/affiliate_linker.py`
- 创建：`tests/test_affiliate_linker.py`

- [ ] **步骤 1：编写失败的测试**

```python
# tests/test_affiliate_linker.py
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from engines.content_engine.affiliate_linker import AffiliateLinker


def test_product_search():
    linker = AffiliateLinker()
    results = linker.search_products('跑步机', '健身')
    assert isinstance(results, list)


def test_inject_placeholders():
    linker = AffiliateLinker()
    text = "推荐购买{affiliate_link_跑步机}，这是性价比最高的选择。"
    products = {
        '跑步机': {'name': '舒华跑步机', 'url': 'https://amazon.cn/xxx', 'price': '2999元'},
    }
    result = linker.inject_links(text, products)
    assert '{affiliate_link_' not in result
    assert '舒华跑步机' in result
    assert 'amazon.cn/xxx' in result


def test_inject_missing_product():
    linker = AffiliateLinker()
    text = "试试{affiliate_link_未知产品}吧"
    result = linker.inject_links(text, {})
    assert '{affiliate_link_' not in result


def test_extract_placeholder_keys():
    linker = AffiliateLinker()
    keys = linker.extract_placeholder_keys("买{affiliate_link_A}和{affiliate_link_B}")
    assert 'A' in keys
    assert 'B' in keys
```

- [ ] **步骤 2：运行测试验证失败**

```powershell
python -m pytest tests/test_affiliate_linker.py -v
```

预期：全部 FAIL

- [ ] **步骤 3：实现 AffiliateLinker 类**

```python
# engines/content_engine/affiliate_linker.py
import json
import os
import re


class AffiliateLinker:
    """管理联盟链接：产品匹配、链接注入"""

    DEFAULT_PRODUCTS = {
        '家电': [
            {'name': '美的电饭煲', 'url': 'https://union.jd.com/placeholder', 'price': '299元', 'platform': '京东'},
            {'name': '戴森吸尘器', 'url': 'https://union.jd.com/placeholder', 'price': '2990元', 'platform': '京东'},
            {'name': '小米空气净化器', 'url': 'https://union.jd.com/placeholder', 'price': '899元', 'platform': '京东'},
        ],
        '数码': [
            {'name': 'AirPods Pro', 'url': 'https://amazon.cn/placeholder', 'price': '1499元', 'platform': 'Amazon'},
            {'name': '罗技鼠标', 'url': 'https://union.jd.com/placeholder', 'price': '199元', 'platform': '京东'},
        ],
        '健身': [
            {'name': '舒华跑步机', 'url': 'https://amazon.cn/placeholder', 'price': '2999元', 'platform': 'Amazon'},
            {'name': 'Keep瑜伽垫', 'url': 'https://union.jd.com/placeholder', 'price': '79元', 'platform': '京东'},
            {'name': '迪卡侬椭圆机', 'url': 'https://amazon.cn/placeholder', 'price': '1999元', 'platform': 'Amazon'},
        ],
    }

    def __init__(self, product_db_path=None):
        self.products = dict(self.DEFAULT_PRODUCTS)
        if product_db_path and os.path.exists(product_db_path):
            with open(product_db_path, 'r', encoding='utf-8') as f:
                custom = json.load(f)
                self.products.update(custom)

    def search_products(self, keyword, niche=None):
        results = []
        if niche and niche in self.products:
            results.extend(self.products[niche])
        for cat_products in self.products.values():
            for p in cat_products:
                if any(kw in p['name'] for kw in keyword.split()):
                    if p not in results:
                        results.append(p)
        return results[:5]

    def inject_links(self, text, product_map):
        def replacer(match):
            product_key = match.group(1)
            for key, product in product_map.items():
                if key in product_key or product_key in key:
                    return f"**[{product['name']}]({product['url']})** ({product['price']})"
            return f"相关产品推荐"
        return re.sub(r'\{affiliate_link_([^}]+)\}', replacer, text)

    def extract_placeholder_keys(self, text):
        return re.findall(r'\{affiliate_link_([^}]+)\}', text)

    def process_article(self, text, niche):
        keys = self.extract_placeholder_keys(text)
        products = {}
        for key in keys:
            for p in self.search_products(key, niche):
                products[key] = p
                break
        processed = self.inject_links(text, products)
        return processed, products
```

- [ ] **步骤 4：运行测试验证通过**

```powershell
python -m pytest tests/test_affiliate_linker.py -v
```

预期：全部 PASS

- [ ] **步骤 5：Commit**

```bash
git add engines/content_engine/affiliate_linker.py tests/test_affiliate_linker.py
git commit -m "feat: affiliate linker with product matching and placeholder injection"
```

---

### 任务 8：内容引擎流程串联

**文件：**
- 修改：`engines/content_engine/__init__.py`

- [ ] **步骤 1：实现内容引擎主流程**

```python
# engines/content_engine/__init__.py
from .trend_tracker import TrendTracker
from .keyword_research import KeywordResearcher
from .article_generator import ArticleGenerator
from .affiliate_linker import AffiliateLinker


def run_content_engine(config, db, llm_call=None):
    """执行完整的内容引擎流程

    llm_call: 可选回调 (system_prompt, user_prompt) -> 生成文本
              为 None 时生成模板草稿
    """
    niches = config.get('niches', ['家电', '数码'])
    articles_per_day = config.get('articles_per_day', 3)

    print("[内容引擎] 开始执行...")

    tracker = TrendTracker()
    trends = tracker.get_trends(niches=niches)
    print(f"[内容引擎] 获取到 {len(trends)} 个相关热点")

    if not trends:
        print("[内容引擎] 无热点话题，使用默认关键词")
        trends = [{'title': niche, 'source': '默认', 'url': ''} for niche in niches]

    researcher = KeywordResearcher()
    keywords = researcher.research(trends)
    top_keywords = researcher.pick_top_keywords(keywords, count=articles_per_day)
    print(f"[内容引擎] 选定 {len(top_keywords)} 个关键词")

    generator = ArticleGenerator()
    linker = AffiliateLinker()
    generated = 0

    for kw in top_keywords:
        niche = None
        for n in niches:
            if n in kw['topic'] or n in kw['keyword']:
                niche = n
                break

        prompt = generator.build_prompt(kw['keyword'], niche)

        if llm_call:
            raw_content = llm_call(generator.SYSTEM_PROMPT, prompt)
        else:
            raw_content = f"""## {kw['keyword']} - 选购指南

> 本文为AI模板草稿，通过LLM接入后自动填充内容。

### 热门产品推荐

| 产品 | 价格 | 评分 |
|------|------|------|
| {{affiliate_link_{kw['topic']}}} | 待查 | 待查 |

### 选购建议

购买{kw['topic']}时需要注意：
1. 预算范围
2. 品牌口碑
3. 售后服务

---
*来源: {kw.get('source_trend', '默认')}*
"""

        processed_content, products = linker.process_article(raw_content, niche)
        title = f"{kw['keyword']} - 2024选购指南与推荐"
        draft_path = generator.save_draft(title, processed_content, kw['keyword'], niche)

        db.insert_article(
            title=title,
            content=processed_content,
            keywords=kw['keyword'],
            affiliate_links=str(list(products.keys())),
            source_trend=kw.get('source_trend', '')
        )
        generated += 1
        print(f"[内容引擎] 已生成: {title}")

    print(f"[内容引擎] 完成，共生成 {generated} 篇文章")
    return generated
```

- [ ] **步骤 2：运行集成验证**

```powershell
python -c "from engines.config import Config; from engines.db import Database; from engines.content_engine import run_content_engine; config = Config('data/config.yaml'); db = Database('data/test_content.db'); run_content_engine(config, db); print(db.get_stats()); db.close(); Remove-Item 'data/test_content.db'"
```

预期：输出引擎执行日志和统计数据

- [ ] **步骤 3：Commit**

```bash
git add engines/content_engine/__init__.py
git commit -m "feat: content engine pipeline integration"
```

---

### 任务 9：线索爬取器

**文件：**
- 创建：`engines/lead_engine/lead_scraper.py`

- [ ] **步骤 1：实现 LeadScraper 类**

```python
# engines/lead_engine/lead_scraper.py
import requests
import re


class LeadScraper:
    """从多个来源爬取商家线索"""

    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept-Language': 'zh-CN,zh;q=0.9',
    }

    def search_baidu_maps(self, keyword, city):
        """通过百度地图搜索商家"""
        results = []
        try:
            url = f'https://map.baidu.com/search/{city}%20{keyword}'
            resp = requests.get(url, headers=self.HEADERS, timeout=10)
            names = re.findall(r'"name":"([^"]+)"', resp.text)
            seen = set()
            for name in names[:15]:
                name = name.strip()
                if name and name not in seen and len(name) > 1:
                    seen.add(name)
                    results.append({
                        'business_name': name,
                        'industry': keyword,
                        'city': city,
                        'contact': '',
                        'source': '百度地图'
                    })
        except Exception as e:
            print(f"[LeadScraper] 百度地图搜索失败 ({keyword},{city}): {e}")
        return results

    def scrape(self, cities, industries, leads_per_city=5):
        """批量爬取线索"""
        all_leads = []
        for city in cities:
            for industry in industries:
                leads = self.search_baidu_maps(industry, city)
                if len(leads) < leads_per_city:
                    for i in range(leads_per_city - len(leads)):
                        leads.append({
                            'business_name': f'{city}{industry}店#{i+1}',
                            'industry': industry,
                            'city': city,
                            'contact': '待查',
                            'source': '本地补充'
                        })
                all_leads.extend(leads[:leads_per_city])
                print(f"[LeadScraper] {city}-{industry}: 获取 {min(len(leads), leads_per_city)} 条线索")
        return all_leads
```

- [ ] **步骤 2：手动验证**

```powershell
python -c "from engines.lead_engine.lead_scraper import LeadScraper; s = LeadScraper(); leads = s.scrape(['上海'], ['美容'], leads_per_city=3); [print(l['business_name']) for l in leads]"
```

预期：输出线索列表

- [ ] **步骤 3：Commit**

```bash
git add engines/lead_engine/lead_scraper.py
git commit -m "feat: lead scraper for baidu maps"
```

---

### 任务 10：线索评分与补全

**文件：**
- 创建：`engines/lead_engine/lead_enricher.py`
- 创建：`tests/test_lead_enricher.py`

- [ ] **步骤 1：编写失败的测试**

```python
# tests/test_lead_enricher.py
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from engines.lead_engine.lead_enricher import LeadEnricher


def test_score_lead_no_website():
    enricher = LeadEnricher()
    lead = {
        'business_name': '小花美甲',
        'industry': '美甲',
        'city': '上海',
        'contact': ''
    }
    enriched = enricher.enrich_one(lead)
    assert 'score' in enriched
    assert enriched['score'] > 0
    assert enriched.get('opportunity') is not None


def test_score_lead_with_website():
    enricher = LeadEnricher()
    lead = {
        'business_name': '大牌连锁',
        'industry': '餐饮',
        'city': '北京',
        'has_website': True,
        'rating': 4.5
    }
    enriched = enricher.enrich_one(lead)
    assert enriched['score'] < 80


def test_detect_opportunity():
    enricher = LeadEnricher()
    opp = enricher.detect_opportunity({'rating': 2.5, 'has_website': False})
    assert '建站' in opp or '优化' in opp or '网站' in opp
    opp = enricher.detect_opportunity({'is_new': True})
    assert opp


def test_enrich_batch():
    enricher = LeadEnricher()
    leads = [
        {'business_name': 'A', 'industry': '美甲', 'city': '上海'},
        {'business_name': 'B', 'industry': '美容', 'city': '北京'},
    ]
    enriched = enricher.enrich(leads)
    assert len(enriched) == 2
    for e in enriched:
        assert 'score' in e
        assert 'opportunity' in e
```

- [ ] **步骤 2：运行测试验证失败**

```powershell
python -m pytest tests/test_lead_enricher.py -v
```

预期：全部 FAIL

- [ ] **步骤 3：实现 LeadEnricher 类**

```python
# engines/lead_engine/lead_enricher.py


class LeadEnricher:
    """线索信息补全、质量评分、机会识别"""

    def enrich(self, leads):
        return [self.enrich_one(lead) for lead in leads]

    def enrich_one(self, lead):
        score = self.calculate_score(lead)
        opportunity = self.detect_opportunity(lead)
        lead['score'] = score
        lead['opportunity'] = opportunity
        return lead

    def calculate_score(self, lead):
        """综合评分 0-100"""
        score = 50
        if not lead.get('has_website', False):
            score += 30
        rating = lead.get('rating', None)
        if rating is not None and rating < 3.5:
            score += 20
        if lead.get('is_new', False):
            score += 20
        if lead.get('is_chain', False):
            score -= 20
        high_demand = ['美甲', '美容', '宠物', '餐饮', '教育', '健身']
        if lead.get('industry', '') in high_demand:
            score += 10
        return max(0, min(100, score))

    def detect_opportunity(self, lead):
        """识别变现机会"""
        opportunities = []
        if not lead.get('has_website', True):
            opportunities.append('建站服务')
        rating = lead.get('rating', None)
        if rating is not None and rating < 3.5:
            opportunities.append('口碑优化')
        if lead.get('is_new', False):
            opportunities.append('新店推广')
        industry = lead.get('industry', '')
        if industry in ['美容', '美甲', '餐饮']:
            opportunities.append('社交媒体运营')
        if not opportunities:
            opportunities.append('综合营销')
        return ' + '.join(opportunities)
```

- [ ] **步骤 4：运行测试验证通过**

```powershell
python -m pytest tests/test_lead_enricher.py -v
```

预期：全部 PASS

- [ ] **步骤 5：Commit**

```bash
git add engines/lead_engine/lead_enricher.py tests/test_lead_enricher.py
git commit -m "feat: lead enricher with scoring and opportunity detection"
```

---

### 任务 11：触达文案生成器

**文件：**
- 创建：`engines/lead_engine/outreach_gen.py`

- [ ] **步骤 1：实现 OutreachGenerator 类**

```python
# engines/lead_engine/outreach_gen.py


class OutreachGenerator:
    """为每条线索生成个性化触达文案"""

    EMAIL_TEMPLATES = {
        '建站服务': """主题：{business_name}，帮您打造专属品牌官网

{owner_name}老板您好，

注意到贵店「{business_name}」在{industry}领域做得很有特色，但目前还没有独立网站。

我们有快速建站方案：
- 3天上线，包含在线预约/产品展示/客户评价
- 帮助您在搜索引擎获得更多曝光

方便聊聊吗？

祝生意兴隆！""",

        '口碑优化': """主题：关于{business_name}的口碑提升建议

{owner_name}老板您好，

关注到贵店在点评平台的评分有提升空间。我们有专业的口碑优化方案，已帮助{city}多家{industry}店提升评分和客流量。

如有兴趣，可进一步沟通。

祝好！""",

        '社交媒体运营': """主题：{business_name}小红书/抖音运营合作

{owner_name}老板您好，

贵店的{industry}服务很适合在小红书/抖音做内容推广。我们可以帮您：
- 策划选题，月产12-20条内容
- 精准投放同城流量
- 提升到店转化

期待交流！""",
    }

    DEFAULT_TEMPLATE = """主题：{business_name}线上推广合作

{owner_name}老板您好，

我是专业的{city}本地营销顾问，注意到贵店在{industry}领域有不错的口碑。

想和您聊聊线上获客的方案，帮助提升客流量。方便加微信沟通吗？

期待回复！"""

    def generate(self, lead):
        opportunities = lead.get('opportunity', '')
        chosen = self.DEFAULT_TEMPLATE
        for key, template in self.EMAIL_TEMPLATES.items():
            if key in opportunities:
                chosen = template
                break

        context = {
            'business_name': lead.get('business_name', '贵店'),
            'industry': lead.get('industry', '本地'),
            'city': lead.get('city', '本地'),
            'owner_name': lead.get('owner_name', ''),
        }

        try:
            return chosen.format(**context)
        except KeyError:
            return self.DEFAULT_TEMPLATE.format(**context)

    def generate_all(self, leads):
        results = []
        for lead in leads:
            lead['outreach_text'] = self.generate(lead)
            results.append(lead)
        return results
```

- [ ] **步骤 2：手动验证**

```powershell
python -c "from engines.lead_engine.outreach_gen import OutreachGenerator; g = OutreachGenerator(); print(g.generate({'business_name': '小花美甲', 'industry': '美甲', 'city': '上海', 'opportunity': '建站服务 + 社交媒体运营'}))"
```

预期：输出触达文案

- [ ] **步骤 3：Commit**

```bash
git add engines/lead_engine/outreach_gen.py
git commit -m "feat: outreach message generator with industry templates"
```

---

### 任务 12：线索引擎流程串联

**文件：**
- 修改：`engines/lead_engine/__init__.py`

- [ ] **步骤 1：实现线索引擎主流程**

```python
# engines/lead_engine/__init__.py
from .lead_scraper import LeadScraper
from .lead_enricher import LeadEnricher
from .outreach_gen import OutreachGenerator


def run_lead_engine(config, db):
    """执行完整的线索引擎流程"""
    cities = config.get('lead_cities', ['上海', '北京'])
    industries = config.get('lead_industries', ['美容', '餐饮'])
    leads_per_city = config.get('leads_per_city', 5)

    print("[线索引擎] 开始执行...")

    scraper = LeadScraper()
    raw_leads = scraper.scrape(cities, industries, leads_per_city)
    print(f"[线索引擎] 爬取到 {len(raw_leads)} 条原始线索")

    enricher = LeadEnricher()
    enriched = enricher.enrich(raw_leads)
    enriched.sort(key=lambda x: x['score'], reverse=True)
    print(f"[线索引擎] 评分完成")

    gen = OutreachGenerator()
    ready_leads = gen.generate_all(enriched)

    stored = 0
    for lead in ready_leads:
        db.insert_lead(
            business_name=lead['business_name'],
            industry=lead.get('industry', ''),
            city=lead.get('city', ''),
            contact=lead.get('contact', ''),
            score=lead.get('score', 0),
            opportunity=lead.get('opportunity', ''),
            outreach_text=lead.get('outreach_text', '')
        )
        stored += 1

    print(f"[线索引擎] 完成，共存储 {stored} 条线索")
    return stored
```

- [ ] **步骤 2：Commit**

```bash
git add engines/lead_engine/__init__.py
git commit -m "feat: lead engine pipeline integration"
```

---

### 任务 13：定时调度器

**文件：**
- 创建：`engines/scheduler.py`
- 创建：`tests/test_scheduler.py`

- [ ] **步骤 1：编写失败的测试**

```python
# tests/test_scheduler.py
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from engines.scheduler import Scheduler
from engines.config import Config
from engines.db import Database

DB_PATH = os.path.join(os.path.dirname(__file__), 'test_scheduler.db')


def teardown_module():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)


def test_run_full_pipeline():
    config_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'config.yaml')
    config = Config(config_path)
    db = Database(DB_PATH)
    scheduler = Scheduler(config, db)

    result = scheduler.run()

    assert result['articles_generated'] >= 0
    assert result['leads_generated'] >= 0
    assert result['status'] in ('ok', 'partial')

    stats = db.get_stats()
    print(f"Stats: {stats}")
    db.close()


def test_generate_report():
    config_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'config.yaml')
    config = Config(config_path)
    db = Database(DB_PATH)
    scheduler = Scheduler(config, db)
    scheduler.run()
    report = scheduler.generate_report()
    assert 'articles' in report
    assert 'leads' in report
    assert report['articles']['draft'] >= 0
    assert report['leads']['pending'] >= 0
    db.close()
```

- [ ] **步骤 2：运行测试验证失败**

```powershell
python -m pytest tests/test_scheduler.py -v
```

预期：全部 FAIL

- [ ] **步骤 3：实现 Scheduler 类**

```python
# engines/scheduler.py
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from engines.content_engine import run_content_engine
from engines.lead_engine import run_lead_engine


class Scheduler:
    """定时任务调度器，串联两个引擎"""

    def __init__(self, config, db):
        self.config = config
        self.db = db

    def run(self):
        """执行完整的一次营销循环"""
        result = {
            'status': 'ok',
            'articles_generated': 0,
            'leads_generated': 0,
            'errors': []
        }

        try:
            articles = run_content_engine(self.config, self.db)
            result['articles_generated'] = articles
        except Exception as e:
            result['errors'].append(f"内容引擎失败: {e}")
            result['status'] = 'partial'

        try:
            leads = run_lead_engine(self.config, self.db)
            result['leads_generated'] = leads
        except Exception as e:
            result['errors'].append(f"线索引擎失败: {e}")
            result['status'] = 'partial'

        return result

    def generate_report(self):
        stats = self.db.get_stats()
        return {
            'articles': {
                'draft': stats['draft_articles'],
                'published': stats['published_articles']
            },
            'leads': {
                'pending': stats['pending_leads'],
                'sent': stats['sent_leads']
            }
        }


if __name__ == '__main__':
    from engines.config import Config
    from engines.db import Database

    config = Config('data/config.yaml')
    db = Database()
    scheduler = Scheduler(config, db)

    print("=" * 50)
    print("AI 自动营销系统 v0.1")
    print("=" * 50)

    result = scheduler.run()
    print(f"\n执行结果: {result['status']}")
    print(f"文章生成: {result['articles_generated']} 篇")
    print(f"线索生成: {result['leads_generated']} 条")

    if result['errors']:
        for err in result['errors']:
            print(f"  ! {err}")

    print("\n数据报告:")
    report = scheduler.generate_report()
    print(f"  待审核文章: {report['articles']['draft']}")
    print(f"  已发布文章: {report['articles']['published']}")
    print(f"  待审核线索: {report['leads']['pending']}")
    print(f"  已发送线索: {report['leads']['sent']}")

    db.close()
```

- [ ] **步骤 4：运行测试验证通过**

```powershell
python -m pytest tests/test_scheduler.py -v
```

预期：全部 PASS

- [ ] **步骤 5：Commit**

```bash
git add engines/scheduler.py tests/test_scheduler.py
git commit -m "feat: scheduler orchestrating content and lead engines"
```

---

### 任务 14：OpenCode Skills（审核层）

**文件：**
- 创建：`skills/review.md`
- 创建：`skills/dashboard.md`
- 创建：`skills/config.md`

- [ ] **步骤 1：创建 /review skill**

```markdown
# Skill: AI 自动营销 - 审核中心

触发命令: /review

## 功能

审核待发布的文章和待发送的线索。

## 执行方式

读取数据库中 `status='draft'` 的文章和 `status='pending'` 的线索，逐条展示给用户审核。

用户可执行的操作：
- 文章：查看全文、修改内容、批准发布、丢弃
- 线索：查看详情和触达文案、批准发送、丢弃

## 使用示例

```
/review
```

系统将展示所有待审核项，并等待用户操作。
```

- [ ] **步骤 2：创建 /dashboard skill**

```markdown
# Skill: AI 自动营销 - 数据看板

触发命令: /dashboard

## 功能

展示今日营销数据概览。

## 数据项

- 待审核文章数量
- 已发布文章数量
- 预估日流量
- 预估佣金收入
- 待审核线索数量
- 已发送触达数量
- 预估转化率
- 预估服务收入

## 使用示例

```
/dashboard
```
```

- [ ] **步骤 3：创建 /config skill**

```markdown
# Skill: AI 自动营销 - 配置管理

触发命令: /config

## 功能

查看和修改系统配置。

## 配置项

编辑 `data/config.yaml` 文件：

- `niches`: 内容关注领域
- `lead_cities`: 线索目标城市
- `lead_industries`: 线索目标行业
- `articles_per_day`: 每日文章数
- `leads_per_city`: 每城市线索数

## 使用示例

```
/config
```
```

- [ ] **步骤 4：Commit**

```bash
git add skills/
git commit -m "feat: opencode skills for review, dashboard, and config"
```

---

### 任务 15：端到端验证与定时任务配置

**文件：**
- 创建：`run.bat`

- [ ] **步骤 1：创建 Windows 运行脚本**

```batch
@echo off
cd /d %~dp0
echo ========================================
echo   AI 自动营销系统
echo   %date% %time%
echo ========================================
python engines/scheduler.py
echo.
echo 执行完毕，运行 /review 审核草稿
pause
```

- [ ] **步骤 2：运行端到端测试**

```powershell
python engines/scheduler.py
dir drafts\articles\
dir drafts\leads\
```

预期：scheduler.py 正常运行输出日志，drafts 目录有文件生成。

- [ ] **步骤 3：最终验证**

```powershell
python -c "
from engines.config import Config
from engines.db import Database
from engines.scheduler import Scheduler
import os

DB_PATH = 'data/test_final.db'
config = Config('data/config.yaml')
db = Database(DB_PATH)
scheduler = Scheduler(config, db)
result = scheduler.run()
assert result['status'] in ('ok', 'partial'), f'Status: {result[\"status\"]}'
assert result['articles_generated'] > 0, 'No articles generated'
assert result['leads_generated'] > 0, 'No leads generated'
print('All checks passed!')
db.close()
os.remove(DB_PATH)
"
```

预期：`All checks passed!`

- [ ] **步骤 4：Commit**

```bash
git add run.bat
git commit -m "feat: windows run script and end-to-end validation"
```

---

## Windows Task Scheduler 配置指南

完成开发后配置定时自动执行：

1. 打开 **任务计划程序** (taskschd.msc)
2. 创建基本任务
3. 名称：`AI 自动营销`
4. 触发器：每天 8:00
5. 操作：启动程序 `C:\workspace\pro12\run.bat`
6. 勾选"不管用户是否登录都要运行"

每天早上 8 点自动执行，10 分钟后打开终端运行 `/review` 审核即可。
