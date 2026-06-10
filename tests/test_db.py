# tests/test_db.py
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from engines.db import Database

DB_PATH = os.path.join(os.path.dirname(__file__), 'test_autopilot.db')


def teardown_module():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)


def test_init_creates_tables():
    db = Database(DB_PATH)
    tables = db.conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    ).fetchall()
    table_names = [t[0] for t in tables]
    assert 'articles' in table_names
    assert 'leads' in table_names
    assert 'config' in table_names
    db.close()


def test_insert_article():
    db = Database(DB_PATH)
    db.insert_article(
        title='Test Article',
        content='Test content',
        keywords='test,article',
        affiliate_links='[]',
        source_trend='test trend'
    )
    row = db.conn.execute("SELECT title, status FROM articles").fetchone()
    assert row['title'] == 'Test Article'
    assert row['status'] == 'draft'
    db.close()


def test_get_pending_articles():
    db = Database(DB_PATH)
    db.insert_article(title='A1', content='x', keywords='x', affiliate_links='[]')
    db.insert_article(title='A2', content='x', keywords='x', affiliate_links='[]')
    pending = db.get_pending_articles()
    assert len(pending) == 3
    assert pending[0]['title'] == 'Test Article'
    db.close()


def test_approve_article():
    db = Database(DB_PATH)
    pending = db.get_pending_articles()
    aid = pending[0]['id']
    db.approve_article(aid)
    row = db.conn.execute("SELECT status FROM articles WHERE id=?", (aid,)).fetchone()
    assert row['status'] == 'approved'
    db.close()
