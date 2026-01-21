import sqlite3
import datetime

DB = 'db.sqlite3'
TABLE = 'ai_interviewsession'

conn = sqlite3.connect(DB)
c = conn.cursor()
now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

c.execute(f"INSERT INTO {TABLE} (user_id, interview_type, created_at) VALUES (?, ?, ?)", (None, 'web', now))
conn.commit()
print('inserted id:', c.lastrowid)
conn.close()
