import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from engines.lead_engine.lead_enricher import LeadEnricher


def test_score_lead_no_website():
    enricher = LeadEnricher()
    lead = {'business_name': '小花美甲', 'industry': '美甲', 'city': '上海', 'contact': ''}
    enriched = enricher.enrich_one(lead)
    assert 'score' in enriched
    assert enriched['score'] > 0
    assert enriched.get('opportunity') is not None


def test_score_lead_with_website():
    enricher = LeadEnricher()
    lead = {'business_name': '大牌连锁', 'industry': '餐饮', 'city': '北京', 'has_website': True, 'rating': 4.5}
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
