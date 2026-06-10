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


if __name__ == '__main__':
    tracker = TrendTracker()
    trends = tracker.get_trends(niches=['家电', '数码', '科技'])
    for t in trends:
        print(f"[{t['source']}] {t['title']}")