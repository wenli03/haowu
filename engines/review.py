import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from engines.db import Database
from engines.config import Config


def show_articles(db):
    articles = db.get_pending_articles()
    if not articles:
        print("暂无待审核文章\n")
        return
    print(f"待审核文章 ({len(articles)}篇):\n")
    for a in articles:
        preview = a['content'][:80].replace('\n', ' ')
        print(f"  [{a['id']}] {a['title']}")
        print(f"      关键词: {a['keywords']} | 已存草稿: drafts/articles/")
        print(f"      预览: {preview}...")
        print()


def show_leads(db):
    leads = db.get_pending_leads()
    if not leads:
        print("暂无待审核线索\n")
        return
    print(f"待审核线索 ({len(leads)}条) - 按评分降序:\n")
    for l in leads[:15]:
        print(f"  [{l['id']}] {l['business_name']} | {l['industry']} | {l['city']}")
        print(f"      评分: {l['score']} | 机会: {l['opportunity']}")
        if l.get('outreach_text'):
            preview = l['outreach_text'][:60].replace('\n', ' ')
            print(f"      触达: {preview}...")
        print()


def run():
    db = Database('data/autopilot.db')

    while True:
        print("=" * 50)
        print("  AI 自动营销 审核中心")
        print("=" * 50)

        show_articles(db)
        show_leads(db)

        print("命令: [v]iew <id> [a]pprove <id> [r]eject <id> [A]ll-approve [q]uit")
        print("示例: a 5  (批准文章/线索ID=5)")
        print("示例: v 3  (查看文章/线索ID=3)")
        print("示例: A    (一键批准全部)")

        cmd = input("\n> ").strip()

        if not cmd:
            continue

        parts = cmd.split()
        action = parts[0].lower()

        if action == 'q':
            break
        elif action == 'a':
            if len(parts) >= 2:
                aid = int(parts[1])
                try:
                    db.approve_article(aid)
                    print(f"  文章 {aid} 已批准")
                except Exception:
                    db.approve_lead(aid)
                    print(f"  线索 {aid} 已批准")
            else:
                print("  请输入: a <id>")
        elif action == 'r':
            if len(parts) >= 2:
                aid = int(parts[1])
                try:
                    db.reject_article(aid)
                    print(f"  文章 {aid} 已丢弃")
                except Exception:
                    db.reject_lead(aid)
                    print(f"  线索 {aid} 已丢弃")
        elif action == 'v':
            if len(parts) >= 2:
                aid = int(parts[1])
                article = db.get_article(aid)
                lead = db.get_lead(aid)
                if article:
                    print("\n" + "=" * 50)
                    print(article['content'])
                    print("=" * 50 + "\n")
                elif lead:
                    print("\n" + "=" * 50)
                    print(f"商家: {lead['business_name']}")
                    print(f"行业: {lead['industry']} | 城市: {lead['city']}")
                    print(f"评分: {lead['score']} | 机会: {lead['opportunity']}")
                    print(f"\n触达文案:\n{lead['outreach_text']}")
                    print("=" * 50 + "\n")
                else:
                    print(f"  ID {aid} 未找到")
        elif action == 'A' or action == 'A':
            articles = db.get_pending_articles()
            leads = db.get_pending_leads()
            for a in articles:
                db.approve_article(a['id'])
            for l in leads:
                db.approve_lead(l['id'])
            print(f"  已批准 {len(articles)} 篇文章 + {len(leads)} 条线索")

    db.close()
    print("\n审核完毕。运行 /dashboard 查看最新数据。")


if __name__ == '__main__':
    run()
