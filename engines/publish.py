import sys
import os
import re
import json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from engines.db import Database

HTML_HEAD = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{description}">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#f5f5f5;color:#333;line-height:1.8}}
header{{background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);color:#fff;padding:30px 20px;text-align:center}}
header a{{color:#fff;text-decoration:none}}
header h1{{font-size:1.5em}}
.container{{max-width:800px;margin:0 auto;padding:20px}}
.article-meta{{color:#999;font-size:.85em;margin-bottom:20px;padding-bottom:15px;border-bottom:1px solid #eee}}
.content{{background:#fff;border-radius:12px;padding:30px;box-shadow:0 2px 12px rgba(0,0,0,.08);margin-bottom:20px}}
.content h1{{font-size:1.6em;margin-bottom:15px;color:#333}}
.content h2{{font-size:1.3em;margin:25px 0 15px;color:#444;padding-bottom:8px;border-bottom:2px solid #667eea}}
.content h3{{font-size:1.1em;margin:20px 0 10px}}
.content p{{margin-bottom:15px}}
.content ul,.content ol{{margin:10px 0 15px 25px}}
.content li{{margin-bottom:5px}}
.content table{{width:100%;border-collapse:collapse;margin:15px 0}}
.content th{{background:#667eea;color:#fff;padding:10px;text-align:left}}
.content td{{padding:10px;border-bottom:1px solid #eee}}
.content blockquote{{border-left:4px solid #667eea;padding:10px 20px;margin:15px 0;background:#f8f9ff;color:#666}}
.content strong{{color:#333}}
.content a{{color:#667eea;text-decoration:none;border-bottom:1px solid #667eea}}
.content a:hover{{color:#764ba2}}
.content hr{{border:none;border-top:1px solid #eee;margin:30px 0}}
.content img{{max-width:100%;border-radius:8px;margin:15px 0}}
.content code{{background:#f0f0f0;padding:2px 6px;border-radius:4px;font-size:.9em}}
.content pre{{background:#282c34;color:#abb2bf;padding:20px;border-radius:8px;overflow-x:auto;margin:15px 0}}
footer{{text-align:center;padding:40px 20px;color:#999;font-size:.85em}}
.btn-back{{display:inline-block;margin-top:20px;padding:10px 25px;background:#667eea;color:#fff;border-radius:25px;text-decoration:none;font-size:.9em}}
.btn-back:hover{{background:#764ba2}}
@media(max-width:600px){{.container{{padding:15px}}.content{{padding:20px}}}}
</style>
</head>
<body>
<header>
  <a href="/"><h1>🛒 好物推荐</h1></a>
  <p>精选产品评测与选购指南</p>
</header>
<div class="container">
<div class="article-meta">{meta}</div>
<div class="content">
{content}
</div>
<a href="/" class="btn-back">← 返回首页</a>
</div>
<footer><p>本站文章由AI辅助生成 | 部分链接含联盟佣金</p></footer>
</body>
</html>'''

INDEX_HEAD = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>好物推荐 | 精选家电数码健身产品评测</title>
<meta name="description" content="专业家电数码健身产品评测与选购指南">
<link rel="alternate" type="application/rss+xml" href="/feed.xml" title="好物推荐">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#f5f5f5;color:#333;line-height:1.6}}
header{{background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);color:#fff;padding:60px 20px;text-align:center}}
header h1{{font-size:2em;margin-bottom:10px}}
header p{{opacity:.9;font-size:1.1em}}
.container{{max-width:800px;margin:0 auto;padding:20px}}
.article-card{{background:#fff;border-radius:12px;padding:25px;margin-bottom:20px;box-shadow:0 2px 12px rgba(0,0,0,.08);transition:transform .2s}}
.article-card:hover{{transform:translateY(-2px)}}
.article-card h2{{font-size:1.3em;margin-bottom:10px}}
.article-card h2 a{{color:#333;text-decoration:none}}
.article-card h2 a:hover{{color:#667eea}}
.article-card .meta{{color:#999;font-size:.85em;margin-bottom:10px}}
.article-card .excerpt{{color:#666;font-size:.95em}}
.tag{{display:inline-block;background:#667eea;color:#fff;padding:2px 10px;border-radius:12px;font-size:.8em;margin-right:6px}}
footer{{text-align:center;padding:40px 20px;color:#999;font-size:.85em}}
.empty-state{{text-align:center;padding:60px 20px;color:#999}}
@media(max-width:600px){{header h1{{font-size:1.5em}}.container{{padding:15px}}}}
</style>
</head>
<body>
<header>
  <h1>🛒 好物推荐</h1>
  <p>精选家电、数码、健身产品评测与选购指南</p>
</header>
<div class="container">
{articles}
</div>
<footer><p>本站文章由AI辅助生成 | 部分链接含联盟佣金</p></footer>
</body>
</html>'''


def md_to_html(text):
    """简单 Markdown 转 HTML"""
    text = re.sub(r'^### (.+)$', r'<h3>\1</h3>', text, flags=re.MULTILINE)
    text = re.sub(r'^## (.+)$', r'<h2>\1</h2>', text, flags=re.MULTILINE)
    text = re.sub(r'^# (.+)$', r'<h1>\1</h1>', text, flags=re.MULTILINE)
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2" rel="nofollow sponsored" target="_blank">\1</a>', text)
    text = re.sub(r'^> (.+)$', r'<blockquote>\1</blockquote>', text, flags=re.MULTILINE)
    text = re.sub(r'^- (.+)$', r'<li>\1</li>', text, flags=re.MULTILINE)
    text = re.sub(r'(<li>.*</li>\n?)+', r'<ul>\g<0></ul>', text)
    text = re.sub(r'^---$', r'<hr>', text, flags=re.MULTILINE)
    paragraphs = re.split(r'\n\n+', text)
    result = []
    for p in paragraphs:
        p = p.strip()
        if not p:
            continue
        if p.startswith('<h') or p.startswith('<ul') or p.startswith('<blockquote') or p.startswith('<hr'):
            result.append(p)
        else:
            lines = p.split('\n')
            if len(lines) == 1 and not lines[0].startswith('<'):
                result.append(f'<p>{lines[0]}</p>')
            else:
                result.append('<p>' + '<br>'.join(lines) + '</p>')
    return '\n'.join(result)


def generate_article_page(article, output_dir='docs/articles'):
    """生成单篇文章 HTML"""
    os.makedirs(output_dir, exist_ok=True)
    html_content = md_to_html(article['content'])
    meta = f"发布于 {article['created_at'][:10]} | 关键词: {article['keywords'] or 'N/A'}"
    html = HTML_HEAD.format(
        title=article['title'],
        description=article['keywords'] or article['title'],
        meta=meta,
        content=html_content
    )
    safe_name = re.sub(r'[^\w\-]', '_', article['title'])[:50]
    filepath = os.path.join(output_dir, f'{safe_name}.html')
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)
    return safe_name + '.html', filepath


def generate_index(articles, output_dir='docs'):
    """生成首页"""
    cards = []
    for row in articles:
        a = dict(row)
        safe_name = re.sub(r'[^\w\-]', '_', a['title'])[:50]
        excerpt = a['content'][:150].replace('#', '').replace('\n', ' ').strip()
        date = a['created_at'][:10] if a['created_at'] else ''
        keywords = (a['keywords'] or '').split(',')
        source_trend = a.get('source_trend', '')
        tags_html = ''.join(f'<span class="tag">{k.strip()}</span>' for k in keywords if k.strip())
        card = f'''<div class="article-card">
  <h2><a href="/articles/{safe_name}.html">{a['title']}</a></h2>
  <div class="meta">{date} | {source_trend}</div>
  <div class="excerpt">{excerpt}...</div>
  <div style="margin-top:10px">{tags_html}</div>
</div>'''
        cards.append(card)
    html = INDEX_HEAD.replace('{articles}', '\n'.join(cards) if cards else '<div class="empty-state"><p>暂无推荐文章</p></div>')
    filepath = os.path.join(output_dir, 'index.html')
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)
    return filepath


def publish():
    db = Database('data/autopilot.db')
    articles = db.conn.execute(
        "SELECT * FROM articles WHERE status='approved' ORDER BY created_at DESC"
    ).fetchall()

    if not articles:
        print("没有已批准的文章。请先用 /review 批准一些文章。")
        db.close()
        return

    print(f"发布 {len(articles)} 篇文章...")
    for a in articles:
        name, path = generate_article_page(dict(a))
        print(f"  OK {name}")

    path = generate_index(articles)
    print(f"  OK index.html")
    print(f"\n站点已生成到 docs/ 目录")
    print(f"下一步：git add docs/ && git commit && git push")
    db.close()


if __name__ == '__main__':
    publish()
