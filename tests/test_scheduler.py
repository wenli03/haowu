import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from engines.scheduler import Scheduler
from engines.config import Config
from engines.db import Database

DB_PATH = os.path.join(os.path.dirname(__file__), 'test_scheduler.db')


def teardown_module():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)


def test_run_full_pipeline():
    config_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'config.yaml')
    config = Config(config_path)
    db = Database(DB_PATH)
    scheduler = Scheduler(config, db)

    result = scheduler.run()

    assert result['articles_generated'] >= 0
    assert result['leads_generated'] >= 0
    assert result['status'] in ('ok', 'partial')

    stats = db.get_stats()
    print(f"Stats: {stats}")
    db.close()


def test_generate_report():
    config_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'config.yaml')
    config = Config(config_path)
    db = Database(DB_PATH)
    scheduler = Scheduler(config, db)
    scheduler.run()
    report = scheduler.generate_report()
    assert 'articles' in report
    assert 'leads' in report
    assert report['articles']['draft'] >= 0
    assert report['leads']['pending'] >= 0
    db.close()
