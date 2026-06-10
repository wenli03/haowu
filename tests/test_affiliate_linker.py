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
