class LeadEnricher:
    """线索信息补全、质量评分、机会识别"""

    def enrich(self, leads):
        return [self.enrich_one(lead) for lead in leads]

    def enrich_one(self, lead):
        score = self.calculate_score(lead)
        opportunity = self.detect_opportunity(lead)
        lead['score'] = score
        lead['opportunity'] = opportunity
        return lead

    def calculate_score(self, lead):
        score = 50
        if not lead.get('has_website', False):
            score += 30
        rating = lead.get('rating', None)
        if rating is not None and rating < 3.5:
            score += 20
        if lead.get('is_new', False):
            score += 20
        if lead.get('is_chain', False):
            score -= 20
        high_demand = ['美甲', '美容', '宠物', '餐饮', '教育', '健身']
        if lead.get('industry', '') in high_demand:
            score += 10
        return max(0, min(100, score))

    def detect_opportunity(self, lead):
        opportunities = []
        if not lead.get('has_website', True):
            opportunities.append('建站服务')
        rating = lead.get('rating', None)
        if rating is not None and rating < 3.5:
            opportunities.append('口碑优化')
        if lead.get('is_new', False):
            opportunities.append('新店推广')
        industry = lead.get('industry', '')
        if industry in ['美容', '美甲', '餐饮']:
            opportunities.append('社交媒体运营')
        if not opportunities:
            opportunities.append('综合营销')
        return ' + '.join(opportunities)
