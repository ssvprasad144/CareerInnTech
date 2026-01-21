import sqlite3
conn = sqlite3.connect('db.sqlite3')
c = conn.cursor()
c.execute("SELECT name FROM sqlite_master WHERE type='table'")
rows = c.fetchall()
print('tables:')
for r in rows:
    print('-', r[0])
conn.close()
