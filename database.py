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
                UNIQUE(client_id, word)
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

@dataclass
class QuizSession:
    words: list
    index: int = 0
    correct_count: int = 0

active_quizzes: dict[int, QuizSession] = {}
