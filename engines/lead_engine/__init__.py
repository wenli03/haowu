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