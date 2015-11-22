import sqlite3


conn = sqlite3.connect('tempdb.db')

cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS celltemp(
     id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
     time INTEGER,
     t1 REAL,
	 t2 REAL,
	 t3 REAL,
	 hum1 REAL
)
""")
conn.commit()

cursor.execute("""
INSERT INTO celltemp(time, t1, t2, t3, hum1) VALUES(CURRENT_TIMESTAMP, ?, ?, ?, ?)""", (1,2,3,4))
conn.commit()