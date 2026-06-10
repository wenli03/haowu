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


if __name__ == '__main__':
    r = KeywordResearcher()
    trends = [{'title': '跑步机推荐', 'source': '知乎'}]
    kw = r.research(trends)
    for k in kw[:5]:
        print(k['keyword'])
