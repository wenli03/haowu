import os
import re


class ArticleGenerator:
    """使用 LLM 生成 SEO 优化的联盟营销文章"""

    SYSTEM_PROMPT = """你是一个专业的SEO内容写手，擅长撰写产品测评和购买指南类文章。

写作规范：
1. 文章长度 1500-3000 字
2. 使用 Markdown 格式
3. 必须包含以下结构：
   - 吸引人的标题（含核心关键词）
   - 开篇引入（用户痛点+文章价值）
   - 产品推荐清单（3-5款，每款含优缺点）
   - 选购指南/避坑建议
   - 总结+购买建议
4. 在提及具体产品时，使用占位符 {affiliate_link_产品名} 标记联盟链接位置
5. 语言自然、真实，避免明显的AI写作痕迹
6. 每个章节用 --- 分隔"""

    def build_prompt(self, keyword, niche=None):
        niche_hint = f"该文章属于「{niche}」领域。" if niche else ""
        return f"""请撰写一篇关于「{keyword}」的SEO优化文章。{niche_hint}

要求：
- 标题必须包含关键词「{keyword}」
- 推荐3-5款相关产品，每款列出优缺点
- 在适合插入购买链接的地方使用 {{affiliate_link_产品名}} 占位符
- 末尾加上标签
"""

    def parse_sections(self, text):
        parts = re.split(r'\n---\n', text)
        sections = []
        for part in parts:
            part = part.strip()
            if not part:
                continue
            lines = part.split('\n')
            title = ''
            for line in lines:
                if line.startswith('#'):
                    title = line.lstrip('#').strip()
                    break
            if not title:
                title = lines[0][:40] if lines else ''
            sections.append({'title': title, 'content': part})
        return sections

    def format_article(self, title, sections):
        parts = [f"# {title}\n"]
        for s in sections:
            parts.append(s['content'])
        return '\n\n---\n\n'.join(parts)

    def save_draft(self, title, content, keyword, niche, drafts_dir='drafts/articles'):
        os.makedirs(drafts_dir, exist_ok=True)
        safe_name = re.sub(r'[^\w\-]', '_', title)[:50]
        filename = f"{safe_name}.md"
        filepath = os.path.join(drafts_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"# {title}\n\n> 关键词: {keyword}\n> 领域: {niche or '通用'}\n\n")
            f.write(content)
        return filepath
