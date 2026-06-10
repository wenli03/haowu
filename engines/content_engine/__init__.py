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

        if llm_call:
            raw_content = llm_call(generator.SYSTEM_PROMPT, generator.build_prompt(kw['keyword'], niche))
        else:
            raw_content = f"""## {kw['keyword']} - 选购指南

> 本文为AI模板草稿，对接LLM后自动填充。

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
        generator.save_draft(title, processed_content, kw['keyword'], niche)

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
