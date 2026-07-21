import sqlite3
from dataclasses import dataclass

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
                UNIQUE(client_id, word),
                correct_count integer,
                incorrect_count integer
                )""")

    c.execute("""CREATE TABLE IF NOT EXISTS review_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id INTEGER,
                word_id INTEGER,
                correct INTEGER,
                reviewed_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (word_id) REFERENCES vocab(id)
                )""")

    conn.commit()
    conn.close() # close database

init_db()

def add_vocab_word(client_id, vocab, reading, meaning):
    conn = sqlite3.connect('vocab.db')
    c = conn.cursor()

    c.execute(
        "INSERT OR IGNORE INTO vocab (client_id, vocab, reading, meaning) VALUES (?, ?, ?, ?)",
        (client_id, vocab, reading, meaning)
    )

    conn.commit()
    conn.close()

def all_words(client_id):
    conn = sqlite3.connect('vocab.db')
    c = conn.cursor()

    c.execute(
        "SELECT vocab, reading, meaning FROM vocab WHERE client_id = ?",
    (client_id,)
    )

    rows = c.fetchall()
    conn.commit()
    conn.close()

    return rows

def log_review(client_id, word_id, correct):
    conn = sqlite3.connect('vocab.db')
    c = conn.cursor()

    c.execute(
        "INSERT INTO review_log (client_id, word_id, correct) VALUES (?, ?, ?)",
        (client_id, word_id, int(correct))
    )

    conn.commit()
    conn.close()

def get_review_words(client_id, limit):
    conn = sqlite3.connect('vocab.db')
    c = conn.cursor()

    c.execute("""
        SELECT v.id, v.vocab, v.reading, v.meaning
        FROM vocab v
        LEFT JOIN review_log r ON v.id = r.word_id AND r.client_id = v.client_id
        WHERE v.client_id = ?
        GROUP BY v.id
        ORDER BY MAX(r.reviewed_at) ASC NULLS FIRST
        LIMIT ?
    """, (client_id, limit))

    rows = c.fetchall()
    conn.close()
    return [
        {"word_id": row[0], "vocab_name": row[1], "reading": row[2], "meaning": row[3]}
        for row in rows
    ]
