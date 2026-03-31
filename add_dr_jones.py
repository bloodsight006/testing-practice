import sqlite3
import os

DB_FILE = os.path.join(os.path.dirname(__file__), 'hospital.db')

conn = sqlite3.connect(DB_FILE)
c = conn.cursor()

# Insert Doctor Jones if not exists
c.execute("SELECT COUNT(*) FROM users WHERE username='drjones'")
if c.fetchone()[0] == 0:
    c.execute("INSERT INTO users (username, password, role, name, specialization) VALUES ('drjones', 'doc123', 'doctor', 'Dr. Jones', 'Orthopedics')")
    print("Added Doctor Jones (drjones / doc123) to database.")
else:
    print("Doctor Jones already exists in database.")

conn.commit()
conn.close()
