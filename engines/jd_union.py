import hashlib
import time
import json
import requests


class JDUnionClient:
    """京东联盟 API 客户端

    接入步骤:
    1. 注册京东联盟 https://union.jd.com
    2. 创建推广位 (网站/社交媒体/导购媒体任意一种)
    3. 申请联盟API权限
    4. 获取 app_key, app_secret, site_id(推广位ID)
    5. 填入 .env 文件即可使用
    """

    BASE_URL = "https://api.jd.com/routerjson"

    def __init__(self, app_key, app_secret, site_id=None):
        self.app_key = app_key
        self.app_secret = app_secret
        self.site_id = site_id

    def _sign(self, params):
        """京东API签名算法: MD5(secret + sorted_params + secret)"""
        sorted_keys = sorted(params.keys())
        param_str = ''.join(f'{k}{params[k]}' for k in sorted_keys)
        sign_str = self.app_secret + param_str + self.app_secret
        return hashlib.md5(sign_str.encode('utf-8')).hexdigest().upper()

    def _call(self, method, params):
        """调用京东API"""
        body = {
            'method': method,
            'app_key': self.app_key,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'format': 'json',
            'v': '1.0',
            'sign_method': 'md5',
        }
        body.update(params)
        body['sign'] = self._sign(body)

        resp = requests.get(self.BASE_URL, params=body, timeout=30)
        resp.raise_for_status()
        return resp.json()

    def search_goods(self, keyword, page=1, page_size=10, min_commission=0):
        """搜索京东商品 (含佣金信息)

        返回: [{name, price, commission, img, url, sku_id}]
        """
        try:
            result = self._call('jd.union.open.goods.jingfen.query', {
                '360buy_param_json': json.dumps({
                    'goodsReq': {
                        'keyword': keyword,
                        'pageIndex': page,
                        'pageSize': page_size,
                        'sortName': 'commissionShare',
                        'sort': 'desc',
                        'isCoupon': 1,
                    }
                })
            })

            goods_list = []
            data = result.get('jd_union_open_goods_jingfen_query_responce', {})
            query_result = data.get('queryResult', {})
            code = int(query_result.get('code', -1))

            if code != 200:
                print(f"  [京东] 搜索失败: {query_result.get('message', 'Unknown')}")
                return goods_list

            for item in query_result.get('data', []):
                commission_info = item.get('commissionInfo', {})
                price_info = item.get('priceInfo', {})
                coupon_info = item.get('couponInfo', {}).get('couponList', [{}])

                commission = commission_info.get('commission', 0)
                if commission < min_commission:
                    continue

                goods_list.append({
                    'name': item.get('goodsName', ''),
                    'price': price_info.get('price', 0),
                    'commission': commission,
                    'commissionShare': commission_info.get('commissionShare', 0),
                    'img': item.get('imageInfo', {}).get('imageList', [{}])[0].get('url', ''),
                    'sku_id': item.get('skuId', ''),
                    'coupon': coupon_info[0].get('link', '') if coupon_info else '',
                })

            return goods_list
        except Exception as e:
            print(f"  [京东] API异常: {e}")
            return []

    def get_promotion_link(self, sku_id):
        """为单个商品生成联盟推广链接"""
        try:
            params = {
                '360buy_param_json': json.dumps({
                    'promotionCodeReq': {
                        'materialId': sku_id,
                        'siteId': self.site_id or '',
                    }
                })
            }
            result = self._call('jd.union.open.promotion.common.get', params)
            data = result.get('jd_union_open_promotion_common_get_responce', {})
            get_result = data.get('getResult', {})
            code = int(get_result.get('code', -1))

            if code == 200:
                return get_result.get('data', {}).get('clickURL', '')
            return ''
        except Exception as e:
            print(f"  [京东] 获取链接失败: {e}")
            return ''

    def search_and_link(self, keyword, count=5, min_commission=3):
        """搜索商品并生成带佣金的推广链接 (自动去重)"""
        goods = self.search_goods(keyword, page_size=count * 2, min_commission=min_commission)
        results = []
        seen_names = set()

        for g in goods[:count]:
            name_key = g['name'][:10]
            if name_key in seen_names:
                continue
            seen_names.add(name_key)

            link = self.get_promotion_link(g['sku_id'])
            g['affiliate_url'] = link or f"https://item.jd.com/{g['sku_id']}.html"
            results.append(g)

        return results


if __name__ == '__main__':
    import os
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from engines.config import Config

    config = Config('data/config.yaml')
    jd = JDUnionClient(
        app_key=config.get('jd.app_key', ''),
        app_secret=config.get('jd.app_secret', ''),
        site_id=config.get('jd.site_id', ''),
    )

    if not jd.app_key:
        print("未配置京东联盟API密钥。请在.env中设置 JD_APP_KEY 和 JD_APP_SECRET")
        sys.exit(1)

    goods = jd.search_and_link('跑步机', count=5)
    print(f"\n找到 {len(goods)} 个商品:\n")
    for g in goods:
        print(f"  {g['name']}")
        print(f"  价格: {g['price']}元 | 佣金: ¥{g['commission']}")
        print(f"  链接: {g['affiliate_url']}")
        print()
