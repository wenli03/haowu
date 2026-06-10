import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from engines.content_engine.article_generator import ArticleGenerator


def test_build_prompt():
    gen = ArticleGenerator()
    prompt = gen.build_prompt('家用跑步机推荐', '健身')
    assert '家用跑步机推荐' in prompt
    assert '健身' in prompt
    assert len(prompt) > 100


def test_build_prompt_no_niche():
    gen = ArticleGenerator()
    prompt = gen.build_prompt('无线耳机测评')
    assert '无线耳机测评' in prompt
    assert len(prompt) > 100


def test_parse_sections():
    gen = ArticleGenerator()
    text = '''
## 为什么需要一台好的跑步机
在家健身越来越流行...
---
## 2024年TOP5跑步机推荐
以下是精选的5款...
---
## 购买建议
综合来看...
'''
    sections = gen.parse_sections(text)
    assert len(sections) >= 2


def test_save_draft():
    gen = ArticleGenerator()
    path = gen.save_draft('测试文章', '这是内容', '测试关键词', '家电', 'drafts/articles')
    assert os.path.exists(path)
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
        assert '测试文章' in content
        assert '测试关键词' in content
    os.remove(path)