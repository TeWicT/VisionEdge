import os, sqlite3, hashlib

DB_PATH = "data/users.db"
DEFAULT_ADMIN = {"username": "admin", "password": "admin123"}

def hash_password(p): return hashlib.sha256(p.encode()).hexdigest()

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH); cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS users (
                     id INTEGER PRIMARY KEY, username TEXT UNIQUE,
                     password TEXT, is_admin INTEGER DEFAULT 0)""")
    conn.commit()
    cur.execute("SELECT COUNT(*) FROM users WHERE is_admin=1")
    if cur.fetchone()[0]==0:
        cur.execute("INSERT OR IGNORE INTO users (username,password,is_admin) VALUES (?,?,1)",
                    (DEFAULT_ADMIN["username"], hash_password(DEFAULT_ADMIN["password"])))
        conn.commit()
    conn.close()

def verify_user(username, password):
    conn = sqlite3.connect(DB_PATH); cur = conn.cursor()
    cur.execute("SELECT id, username, is_admin FROM users WHERE username=? AND password=?",
                (username, hash_password(password)))
    row = cur.fetchone(); conn.close()
    return {"id":row[0],"username":row[1],"is_admin":bool(row[2])} if row else None
