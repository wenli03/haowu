import sqlite3
import os


class Database:
    def __init__(self, db_path='data/autopilot.db'):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self._init_tables()

    def _init_tables(self):
        self.conn.executescript('''
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                keywords TEXT,
                affiliate_links TEXT DEFAULT '[]',
                source_trend TEXT,
                status TEXT DEFAULT 'draft',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                published_at TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                business_name TEXT NOT NULL,
                industry TEXT,
                city TEXT,
                contact TEXT,
                score INTEGER DEFAULT 0,
                opportunity TEXT,
                outreach_text TEXT,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                sent_at TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS config (
                key TEXT PRIMARY KEY,
                value TEXT
            );
        ''')
        self.conn.commit()

    def insert_article(self, title, content, keywords='', affiliate_links='[]', source_trend=None):
        self.conn.execute(
            "INSERT INTO articles (title, content, keywords, affiliate_links, source_trend) VALUES (?, ?, ?, ?, ?)",
            (title, content, keywords, affiliate_links, source_trend)
        )
        self.conn.commit()

    def get_pending_articles(self):
        return self.conn.execute(
            "SELECT * FROM articles WHERE status='draft' ORDER BY created_at DESC"
        ).fetchall()

    def get_article(self, article_id):
        return self.conn.execute(
            "SELECT * FROM articles WHERE id=?", (article_id,)
        ).fetchone()

    def approve_article(self, article_id):
        self.conn.execute(
            "UPDATE articles SET status='approved', published_at=CURRENT_TIMESTAMP WHERE id=?",
            (article_id,)
        )
        self.conn.commit()

    def reject_article(self, article_id):
        self.conn.execute(
            "UPDATE articles SET status='rejected' WHERE id=?",
            (article_id,)
        )
        self.conn.commit()

    def update_article(self, article_id, title=None, content=None, keywords=None):
        fields = {}
        if title:
            fields['title'] = title
        if content:
            fields['content'] = content
        if keywords:
            fields['keywords'] = keywords
        if not fields:
            return
        sets = ', '.join(f'{k}=?' for k in fields)
        values = list(fields.values()) + [article_id]
        self.conn.execute(f"UPDATE articles SET {sets} WHERE id=?", values)
        self.conn.commit()

    def insert_lead(self, business_name, industry='', city='', contact='', score=0, opportunity=None, outreach_text=None):
        self.conn.execute(
            "INSERT INTO leads (business_name, industry, city, contact, score, opportunity, outreach_text) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (business_name, industry, city, contact, score, opportunity, outreach_text)
        )
        self.conn.commit()

    def get_pending_leads(self):
        return self.conn.execute(
            "SELECT * FROM leads WHERE status='pending' ORDER BY score DESC"
        ).fetchall()

    def get_lead(self, lead_id):
        return self.conn.execute(
            "SELECT * FROM leads WHERE id=?", (lead_id,)
        ).fetchone()

    def approve_lead(self, lead_id):
        self.conn.execute(
            "UPDATE leads SET status='approved', sent_at=CURRENT_TIMESTAMP WHERE id=?",
            (lead_id,)
        )
        self.conn.commit()

    def reject_lead(self, lead_id):
        self.conn.execute(
            "UPDATE leads SET status='rejected' WHERE id=?",
            (lead_id,)
        )
        self.conn.commit()

    def get_config(self, key, default=None):
        row = self.conn.execute("SELECT value FROM config WHERE key=?", (key,)).fetchone()
        return row['value'] if row else default

    def set_config(self, key, value):
        self.conn.execute(
            "INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)",
            (key, str(value))
        )
        self.conn.commit()

    def get_stats(self):
        draft_count = self.conn.execute(
            "SELECT COUNT(*) FROM articles WHERE status='draft'"
        ).fetchone()[0]
        approved_count = self.conn.execute(
            "SELECT COUNT(*) FROM articles WHERE status='approved'"
        ).fetchone()[0]
        pending_leads = self.conn.execute(
            "SELECT COUNT(*) FROM leads WHERE status='pending'"
        ).fetchone()[0]
        approved_leads = self.conn.execute(
            "SELECT COUNT(*) FROM leads WHERE status='approved'"
        ).fetchone()[0]
        return {
            'draft_articles': draft_count,
            'published_articles': approved_count,
            'pending_leads': pending_leads,
            'sent_leads': approved_leads
        }

    def close(self):
        self.conn.close()
