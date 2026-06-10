class OutreachGenerator:
    """为每条线索生成个性化触达文案"""

    EMAIL_TEMPLATES = {
        '建站服务': """主题：{business_name}，帮您打造专属品牌官网

{owner_name}老板您好，

注意到贵店「{business_name}」在{industry}领域做得很有特色，但目前还没有独立网站。

我们有快速建站方案：
- 3天上线，包含在线预约/产品展示/客户评价
- 帮助您在搜索引擎获得更多曝光

方便聊聊吗？

祝生意兴隆！""",

        '口碑优化': """主题：关于{business_name}的口碑提升建议

{owner_name}老板您好，

关注到贵店在点评平台的评分有提升空间。我们有专业的口碑优化方案，已帮助{city}多家{industry}店提升评分和客流量。

如有兴趣，可进一步沟通。

祝好！""",

        '社交媒体运营': """主题：{business_name}小红书/抖音运营合作

{owner_name}老板您好，

贵店的{industry}服务很适合在小红书/抖音做内容推广。我们可以帮您：
- 策划选题，月产12-20条内容
- 精准投放同城流量
- 提升到店转化

期待交流！""",
    }

    DEFAULT_TEMPLATE = """主题：{business_name}线上推广合作

{owner_name}老板您好，

我是专业的{city}本地营销顾问，注意到贵店在{industry}领域有不错的口碑。

想和您聊聊线上获客的方案，帮助提升客流量。方便加微信沟通吗？

期待回复！"""

    def generate(self, lead):
        opportunities = lead.get('opportunity', '')
        chosen = self.DEFAULT_TEMPLATE
        for key, template in self.EMAIL_TEMPLATES.items():
            if key in opportunities:
                chosen = template
                break

        context = {
            'business_name': lead.get('business_name', '贵店'),
            'industry': lead.get('industry', '本地'),
            'city': lead.get('city', '本地'),
            'owner_name': lead.get('owner_name', ''),
        }

        try:
            return chosen.format(**context)
        except KeyError:
            return self.DEFAULT_TEMPLATE.format(**context)

    def generate_all(self, leads):
        results = []
        for lead in leads:
            lead['outreach_text'] = self.generate(lead)
            results.append(lead)
        return results


if __name__ == '__main__':
    g = OutreachGenerator()
    lead = {
        'business_name': '小花美甲',
        'industry': '美甲',
        'city': '上海',
        'opportunity': '建站服务 + 社交媒体运营'
    }
    print(g.generate(lead))
