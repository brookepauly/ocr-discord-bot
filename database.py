import sqlite3

def init_db():
    conn = sqlite3.connect('vocab.db') # connection
    c = conn.cursor() # cursor
    c.execute("""CREATE TABLE IF NOT EXISTS vocab (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id integer,
                meaning text,
                word text,
                reading text,
                date_added TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(client_id, word)
                )""")

    conn.commit()
    conn.close() # close database

init_db()
