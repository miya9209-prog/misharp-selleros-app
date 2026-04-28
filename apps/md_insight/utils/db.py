import sqlite3
from pathlib import Path

def _db_path() -> Path:
    folder = Path.home() / ".md_insight_data"
    folder.mkdir(parents=True, exist_ok=True)
    return folder / "md_insight.db"

DB_PATH = _db_path()

def get_conn():
    return sqlite3.connect(str(DB_PATH), check_same_thread=False)

def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source TEXT,
        keyword TEXT,
        category TEXT,
        name TEXT,
        price TEXT,
        mall TEXT,
        link TEXT,
        image_url TEXT,
        collected_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS keyword_cache (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source TEXT,
        period TEXT,
        keyword TEXT,
        score REAL,
        collected_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source TEXT,
        status TEXT,
        message TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.commit()
    conn.close()

def insert_products(rows):
    if not rows:
        return 0
    conn = get_conn()
    cur = conn.cursor()
    cur.executemany(
        """
        INSERT INTO products (source, keyword, category, name, price, mall, link, image_url)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        rows,
    )
    conn.commit()
    count = cur.rowcount
    conn.close()
    return count

def insert_keyword_cache(rows):
    if not rows:
        return 0
    conn = get_conn()
    cur = conn.cursor()
    cur.executemany(
        "INSERT INTO keyword_cache (source, period, keyword, score) VALUES (?, ?, ?, ?)",
        rows,
    )
    conn.commit()
    count = cur.rowcount
    conn.close()
    return count

def get_recent_products(limit=100, source=None):
    conn = get_conn()
    cur = conn.cursor()
    if source:
        cur.execute(
            """SELECT id, source, keyword, category, name, price, mall, link, image_url, collected_at
               FROM products WHERE source = ? ORDER BY id DESC LIMIT ?""",
            (source, limit),
        )
    else:
        cur.execute(
            """SELECT id, source, keyword, category, name, price, mall, link, image_url, collected_at
               FROM products ORDER BY id DESC LIMIT ?""",
            (limit,),
        )
    rows = cur.fetchall()
    conn.close()
    return rows

def get_recent_keywords(limit=100, source=None, period=None):
    conn = get_conn()
    cur = conn.cursor()
    q = "SELECT id, source, period, keyword, score, collected_at FROM keyword_cache WHERE 1=1"
    params = []
    if source:
        q += " AND source = ?"
        params.append(source)
    if period:
        q += " AND period = ?"
        params.append(period)
    q += " ORDER BY score DESC, id DESC LIMIT ?"
    params.append(limit)
    cur.execute(q, tuple(params))
    rows = cur.fetchall()
    conn.close()
    return rows

def get_names_for_insight(limit=150):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT name FROM products WHERE name IS NOT NULL AND TRIM(name) != '' ORDER BY id DESC LIMIT ?", (limit,))
    rows = [r[0] for r in cur.fetchall()]
    conn.close()
    return rows

def get_summary_stats():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM products")
    total = cur.fetchone()[0]
    cur.execute("SELECT source, COUNT(*) FROM products GROUP BY source ORDER BY COUNT(*) DESC")
    by_source = cur.fetchall()
    cur.execute("""
        SELECT category, COUNT(*)
        FROM products
        WHERE category IS NOT NULL AND TRIM(category) != ''
        GROUP BY category
        ORDER BY COUNT(*) DESC
        LIMIT 100
    """)
    by_category = cur.fetchall()
    cur.execute("SELECT mall, COUNT(*) FROM products GROUP BY mall ORDER BY COUNT(*) DESC LIMIT 100")
    by_mall = cur.fetchall()
    conn.close()
    return {"total": total, "by_source": by_source, "by_category": by_category, "by_mall": by_mall}

def log_event(source, status, message):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO logs (source, status, message) VALUES (?, ?, ?)", (source, status, message))
    conn.commit()
    conn.close()

def get_db_path_text():
    return str(DB_PATH)
