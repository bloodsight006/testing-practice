import sqlite3
import os

DB_FILE = os.path.join(os.path.dirname(__file__), 'hospital.db')

conn = sqlite3.connect(DB_FILE)
c = conn.cursor()

# Insert Doctor John if not exists
c.execute("SELECT COUNT(*) FROM users WHERE username='drjohn'")
if c.fetchone()[0] == 0:
    c.execute("INSERT INTO users (username, password, role, name, specialization) VALUES ('drjohn', 'doc123', 'doctor', 'Dr. John', 'Neurology')")
    print("Added Doctor John (drjohn / doc123) to database.")
else:
    print("Doctor John already exists in database.")

conn.commit()
conn.close()
