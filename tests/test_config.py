import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from engines.config import Config

CONFIG_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'config.yaml')


def test_load_default_config():
    config = Config(CONFIG_PATH)
    assert config.get('niches') == ['家电', '数码', '健身']
    assert config.get('lead_cities') == ['上海', '北京', '深圳']
    assert config.get('lead_industries') == ['美甲', '美容', '宠物', '餐饮']
    assert config.get('articles_per_day') == 3


def test_missing_key_returns_none():
    config = Config(CONFIG_PATH)
    assert config.get('nonexistent') is None


def test_missing_key_with_default():
    config = Config(CONFIG_PATH)
    assert config.get('nonexistent', 'default') == 'default'
