import sqlite3
from datetime import datetime

def init_db():
    conn = sqlite3.connect('cover_letters.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS cover_letters
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  job_title TEXT,
                  company TEXT,
                  skills TEXT,
                  background TEXT,
                  cover_letter TEXT,
                  created_at TIMESTAMP)''')
    conn.commit()
    conn.close()

def save_cover_letter(job_title, company, skills, cover_letter, background=''):
    conn = sqlite3.connect('cover_letters.db')
    c = conn.cursor()
    c.execute('INSERT INTO cover_letters (job_title, company, skills, background, cover_letter, created_at) VALUES (?, ?, ?, ?, ?, ?)',
              (job_title, company, skills, background, cover_letter, datetime.now()))
    conn.commit()
    conn.close()

def get_all_cover_letters():
    conn = sqlite3.connect('cover_letters.db')
    c = conn.cursor()
    c.execute('SELECT job_title, company, skills, background, cover_letter, created_at FROM cover_letters')
    letters = c.fetchall()
    conn.close()
    return letters