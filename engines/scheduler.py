import sys
import os
import re

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from engines.content_engine import run_content_engine
from engines.lead_engine import run_lead_engine


class Scheduler:
    """定时任务调度器，串联两个引擎"""

    def __init__(self, config, db, llm_client=None):
        self.config = config
        self.db = db
        self.llm_client = llm_client

    def run(self):
        """执行完整的一次营销循环"""
        result = {
            'status': 'ok',
            'articles_generated': 0,
            'leads_generated': 0,
            'errors': []
        }

        try:
            articles = run_content_engine(self.config, self.db, llm_call=self.llm_client)
            result['articles_generated'] = articles
        except Exception as e:
            result['errors'].append(f"内容引擎失败: {e}")
            result['status'] = 'partial'

        try:
            leads = run_lead_engine(self.config, self.db)
            result['leads_generated'] = leads
        except Exception as e:
            result['errors'].append(f"线索引擎失败: {e}")
            result['status'] = 'partial'

        return result

    def generate_report(self):
        stats = self.db.get_stats()
        return {
            'articles': {
                'draft': stats['draft_articles'],
                'published': stats['published_articles']
            },
            'leads': {
                'pending': stats['pending_leads'],
                'sent': stats['sent_leads']
            }
        }


if __name__ == '__main__':
    from engines.config import Config
    from engines.db import Database
    from engines.llm_client import LLMClient

    # 加载 .env 文件到环境变量
    env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, val = line.split('=', 1)
                    os.environ[key.strip()] = val.strip()

    config = Config('data/config.yaml')
    db = Database()

    api_key = config.get('llm.api_key')
    if api_key and api_key.startswith('$'):
        env_match = re.match(r'\$\{(\w+)\}', api_key)
        if env_match:
            api_key = os.environ.get(env_match.group(1), '')

    llm = LLMClient(
        api_key=api_key,
        model=config.get('llm.model', 'deepseek-ai/DeepSeek-V4-Pro')
    )

    scheduler = Scheduler(config, db, llm_client=llm)

    print("=" * 50)
    print("AI 自动营销系统 v0.1")
    print("=" * 50)

    result = scheduler.run()
    print(f"\n执行结果: {result['status']}")
    print(f"文章生成: {result['articles_generated']} 篇")
    print(f"线索生成: {result['leads_generated']} 条")

    if result['errors']:
        for err in result['errors']:
            print(f"  ! {err}")

    print("\n数据报告:")
    report = scheduler.generate_report()
    print(f"  待审核文章: {report['articles']['draft']}")
    print(f"  已发布文章: {report['articles']['published']}")
    print(f"  待审核线索: {report['leads']['pending']}")
    print(f"  已发送线索: {report['leads']['sent']}")

    db.close()
