import hashlib, sqlite3
from datetime import datetime, timezone
from evidora.config import DB, UPLOADS

def conn():
    c = sqlite3.connect(DB); c.row_factory = sqlite3.Row
    c.execute("PRAGMA foreign_keys=ON")
    return c

def init_db():
    with conn() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS papers(
          id INTEGER PRIMARY KEY, filename TEXT NOT NULL, file_hash TEXT UNIQUE NOT NULL,
          title TEXT, authors TEXT, year INTEGER, abstract TEXT, page_count INTEGER,
          warnings TEXT DEFAULT '', stored_path TEXT, created_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS pages(
          id INTEGER PRIMARY KEY, paper_id INTEGER NOT NULL REFERENCES papers(id) ON DELETE CASCADE,
          page_number INTEGER NOT NULL, text TEXT NOT NULL, UNIQUE(paper_id,page_number));
        CREATE INDEX IF NOT EXISTS idx_pages_paper ON pages(paper_id);
        """)

def add_paper(filename, data, result):
    h = hashlib.sha256(data).hexdigest()
    with conn() as c:
        if c.execute("SELECT id FROM papers WHERE file_hash=?", (h,)).fetchone(): return False
        path = UPLOADS / f"{h}.pdf"; path.write_bytes(data)
        cur = c.execute("""INSERT INTO papers(filename,file_hash,title,authors,year,abstract,page_count,warnings,stored_path,created_at)
          VALUES(?,?,?,?,?,?,?,?,?,?)""",
          (filename,h,result["title"],result["authors"],result["year"],result["abstract"],result["page_count"],result["warnings"],str(path),datetime.now(timezone.utc).isoformat()))
        pid = cur.lastrowid
        c.executemany("INSERT INTO pages(paper_id,page_number,text) VALUES(?,?,?)",
                      [(pid,p["page_number"],p["text"]) for p in result["pages"]])
        return True

def papers():
    with conn() as c: rows = c.execute("SELECT * FROM papers ORDER BY created_at DESC").fetchall()
    return [dict(r) for r in rows]

def pages(pid):
    with conn() as c: rows = c.execute("SELECT page_number,text FROM pages WHERE paper_id=? ORDER BY page_number",(pid,)).fetchall()
    return [dict(r) for r in rows]

def remove_paper(pid):
    from pathlib import Path
    with conn() as c:
        row = c.execute("SELECT stored_path FROM papers WHERE id=?", (pid,)).fetchone()
        if row and row["stored_path"]: Path(row["stored_path"]).unlink(missing_ok=True)
        c.execute("DELETE FROM papers WHERE id=?", (pid,))
