import hashlib
import time
import json
import requests


class JDUnionClient:
    """京东联盟 API 客户端"""

    BASE_URL = "https://api.jd.com/routerjson"

    def __init__(self, app_key, app_secret, site_id=None):
        self.app_key = app_key
        self.app_secret = app_secret
        self.site_id = site_id

    def _sign(self, params):
        sorted_keys = sorted(params.keys())
        param_str = ''.join(f'{k}{params[k]}' for k in sorted_keys)
        sign_str = self.app_secret + param_str + self.app_secret
        return hashlib.md5(sign_str.encode('utf-8')).hexdigest().upper()

    def _call(self, method, params):
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

    def _parse_inner(self, data, key):
        result = data.get(key, {})
        inner_keys = [k for k in result.keys() if k != 'code']
        for ik in inner_keys:
            val = result.get(ik)
            if isinstance(val, str) and val.startswith('{'):
                result[ik] = json.loads(val)
        return result

    def get_promotion_link(self, material_url):
        for req in [
            {'materialId': material_url, 'siteId': self.site_id},
            {'materialId': material_url, 'siteId': self.site_id, 'subUnionId': 'haowu'},
        ]:
            try:
                result = self._call('jd.union.open.promotion.common.get', {
                    '360buy_param_json': json.dumps({'promotionCodeReq': req})
                })
                inner = self._parse_inner(result, 'jd_union_open_promotion_common_get_responce')
                gr = inner.get('getResult', {})
                if gr.get('code') == 200:
                    return gr.get('data', {}).get('clickURL', '')
            except Exception as e:
                print(f"  [JD] 转链失败: {e}")
        return ''

    def search_and_link(self, keyword, count=5, min_commission=0):
        results = []
        try:
            result = self._call('jd.union.open.goods.query', {
                '360buy_param_json': json.dumps({
                    'goodsReqDTO': {
                        'keyword': keyword,
                        'pageIndex': 1,
                        'pageSize': count * 3,
                        'sortName': 'commissionShare',
                        'sort': 'desc',
                    }
                })
            })
            inner = self._parse_inner(result, 'jd_union_open_goods_query_responce')
            qr = inner.get('queryResult', {})

            if qr.get('code') != 200:
                print(f"  [JD] 搜索失败: {qr.get('message', '')}")
                return results

            for item in qr.get('data', []):
                ci = item.get('commissionInfo', {})
                pi = item.get('priceInfo', {})
                comm = ci.get('commission', 0)
                if comm < min_commission:
                    continue

                sku_id = str(item.get('skuId', ''))
                material_url = f'https://item.jd.com/{sku_id}.html'
                link = self.get_promotion_link(material_url) or material_url

                results.append({
                    'name': item.get('goodsName', ''),
                    'price': pi.get('price', 0),
                    'commission': comm,
                    'sku_id': sku_id,
                    'affiliate_url': link,
                })

            return results[:count]
        except Exception as e:
            print(f"  [JD] API异常: {e}")
            return []
