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


if __name__ == '__main__':
    s = LeadScraper()
    leads = s.scrape(['上海'], ['美容'], leads_per_city=3)
    for l in leads:
        print(f"  {l['business_name']} [{l['source']}]")
