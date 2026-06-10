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
