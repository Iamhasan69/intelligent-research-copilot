import json, sqlite3, time
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[2] / 'storage' / 'research.db'
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

def conn():
    c=sqlite3.connect(DB_PATH); c.row_factory=sqlite3.Row; return c

def init_db():
    with conn() as c:
        c.executescript('''
        CREATE TABLE IF NOT EXISTS researches(
          id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, query TEXT NOT NULL,
          provider TEXT, model TEXT, status TEXT, created_at REAL, updated_at REAL,
          report TEXT, dataset_json TEXT, graph_json TEXT
        );
        CREATE TABLE IF NOT EXISTS sources(
          id INTEGER PRIMARY KEY AUTOINCREMENT, research_id INTEGER, url TEXT, title TEXT,
          domain TEXT, snippet TEXT, content TEXT, source_type TEXT, fetched_at REAL,
          FOREIGN KEY(research_id) REFERENCES researches(id)
        );
        CREATE TABLE IF NOT EXISTS evidence(
          id INTEGER PRIMARY KEY AUTOINCREMENT, research_id INTEGER, source_id INTEGER,
          claim TEXT, quote TEXT, confidence REAL, FOREIGN KEY(research_id) REFERENCES researches(id)
        );
        CREATE TABLE IF NOT EXISTS events(
          id INTEGER PRIMARY KEY AUTOINCREMENT, research_id INTEGER, stage TEXT, message TEXT,
          detail TEXT, created_at REAL, FOREIGN KEY(research_id) REFERENCES researches(id)
        );
        CREATE TABLE IF NOT EXISTS settings(
          provider TEXT PRIMARY KEY, model TEXT, api_key TEXT, connected INTEGER DEFAULT 0, updated_at REAL
        );
        ''')

def create_research(query, provider, model):
    now=time.time(); title=query[:80]
    with conn() as c:
        cur=c.execute('INSERT INTO researches(title,query,provider,model,status,created_at,updated_at) VALUES(?,?,?,?,?,?,?)',(title,query,provider,model,'planning',now,now))
        return cur.lastrowid

def update_research(rid, **fields):
    fields['updated_at']=time.time(); keys=list(fields); vals=[fields[k] for k in keys]
    with conn() as c: c.execute(f"UPDATE researches SET {','.join(k+'=?' for k in keys)} WHERE id=?", vals+[rid])

def add_source(rid, **s):
    with conn() as c:
        cur=c.execute('INSERT INTO sources(research_id,url,title,domain,snippet,content,source_type,fetched_at) VALUES(?,?,?,?,?,?,?,?)',(rid,s.get('url'),s.get('title'),s.get('domain'),s.get('snippet',''),s.get('content',''),s.get('source_type','web'),time.time()))
        return cur.lastrowid

def add_event(rid, stage, message, detail=''):
    with conn() as c: c.execute('INSERT INTO events(research_id,stage,message,detail,created_at) VALUES(?,?,?,?,?)',(rid,stage,message,detail,time.time()))

def add_evidence(rid, source_id, claim, quote, confidence):
    with conn() as c: c.execute('INSERT INTO evidence(research_id,source_id,claim,quote,confidence) VALUES(?,?,?,?,?)',(rid,source_id,claim,quote,confidence))

def get_research(rid):
    with conn() as c:
        r=c.execute('SELECT * FROM researches WHERE id=?',(rid,)).fetchone()
        if not r:return None
        d=dict(r); d['dataset']=json.loads(d.pop('dataset_json') or '[]'); d['graph']=json.loads(d.pop('graph_json') or '{}')
        d['sources']=[dict(x) for x in c.execute('SELECT * FROM sources WHERE research_id=? ORDER BY id',(rid,))]
        d['evidence']=[dict(x) for x in c.execute('SELECT * FROM evidence WHERE research_id=? ORDER BY id',(rid,))]
        d['events']=[dict(x) for x in c.execute('SELECT * FROM events WHERE research_id=? ORDER BY id',(rid,))]
        return d

def list_researches():
    with conn() as c:return [dict(x) for x in c.execute('SELECT id,title,query,provider,model,status,created_at,updated_at FROM researches ORDER BY id DESC')]

def save_settings(provider, model, api_key, connected=0):
    with conn() as c:c.execute('INSERT INTO settings(provider,model,api_key,connected,updated_at) VALUES(?,?,?,?,?) ON CONFLICT(provider) DO UPDATE SET model=excluded.model,api_key=excluded.api_key,connected=excluded.connected,updated_at=excluded.updated_at',(provider,model,api_key,connected,time.time()))

def get_settings():
    with conn() as c:return [dict(x) for x in c.execute('SELECT provider,model,connected,updated_at FROM settings')]

def get_key(provider):
    import os
    env=os.getenv(provider.upper()+'_API_KEY')
    if env:return env
    with conn() as c:
        r=c.execute('SELECT api_key FROM settings WHERE provider=?',(provider,)).fetchone(); return r['api_key'] if r else None
