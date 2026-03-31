import os
import sqlite3
from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'super_secret_key_for_hospital'
DB_FILE = 'hospital.db'

def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE,
                    password TEXT,
                    role TEXT,
                    name TEXT,
                    specialization TEXT
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS appointments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    patient_id INTEGER,
                    doctor_id INTEGER,
                    app_date TEXT,
                    app_time TEXT,
                    medical_history TEXT,
                    status TEXT,
                    fee INTEGER,
                    FOREIGN KEY(patient_id) REFERENCES users(id),
                    FOREIGN KEY(doctor_id) REFERENCES users(id)
                )''')
    c.execute("SELECT COUNT(*) FROM users")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO users (username, password, role, name) VALUES ('admin', 'admin123', 'admin', 'System Admin')")
        c.execute("INSERT INTO users (username, password, role, name, specialization) VALUES ('drsmith', 'doc123', 'doctor', 'Dr. Smith', 'Cardiology')")
        c.execute("INSERT INTO users (username, password, role, name, specialization) VALUES ('drjohn', 'doc123', 'doctor', 'Dr. John', 'Neurology')")
        c.execute("INSERT INTO users (username, password, role, name, specialization) VALUES ('drjones', 'doc123', 'doctor', 'Dr. Jones', 'Neurology')")
        c.execute("INSERT INTO users (username, password, role, name) VALUES ('patient1', 'pat123', 'patient', 'John Doe')")
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    if 'user_id' in session:
        if session['role'] == 'admin': return redirect(url_for('admin_dash'))
        if session['role'] == 'doctor': return redirect(url_for('doctor_dash'))
        if session['role'] == 'patient': return redirect(url_for('patient_dash'))
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password)).fetchone()
        conn.close()
        
        if user:
            session['user_id'] = user['id']
            session['role'] = user['role']
            session['name'] = user['name']
            return redirect(url_for('index'))
        return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        name = request.form.get('name')
        
        conn = get_db()
        try:
            conn.execute("INSERT INTO users (username, password, role, name) VALUES (?, ?, 'patient', ?)", (username, password, name))
            conn.commit()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            return render_template('register.html', error="Username already exists")
        finally:
            conn.close()
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/patient', methods=['GET', 'POST'])
def patient_dash():
    if session.get('role') != 'patient': return redirect(url_for('index'))
    conn = get_db()
    
    if request.method == 'POST':
        doctor_id = request.form.get('doctor_id')
        date = request.form.get('date')
        time = request.form.get('time')
        history = request.form.get('history')
        fee = int(request.form.get('fee', 0))
        
        # S1: Start booking
        # S2: Check patient login (already passed via session)
        
        # S3: Check Doc Availability
        conflict = conn.execute("SELECT id FROM appointments WHERE doctor_id=? AND app_date=? AND app_time=?", (doctor_id, date, time)).fetchone()
        if conflict:
            return render_template('patient.html', error="Doctor unavailable at this time.", **locals())
        
        # S5: Payment Valid
        if fee < 50:
            return render_template('patient.html', error="Minimum Booking fee is $50", **locals())
            
        conn.execute("INSERT INTO appointments (patient_id, doctor_id, app_date, app_time, medical_history, status, fee) VALUES (?, ?, ?, ?, ?, 'booked', ?)", 
                     (session['user_id'], doctor_id, date, time, history, fee))
        conn.commit()
        return redirect(url_for('patient_dash'))

    doctors = conn.execute("SELECT id, name, specialization FROM users WHERE role='doctor'").fetchall()
    history_recs = conn.execute("SELECT a.*, u.name as doc_name FROM appointments a JOIN users u ON a.doctor_id = u.id WHERE patient_id=? ORDER BY app_date DESC", (session['user_id'],)).fetchall()
    conn.close()
    return render_template('patient.html', doctors=doctors, history=history_recs, name=session['name'])

@app.route('/doctor')
def doctor_dash():
    if session.get('role') != 'doctor': return redirect(url_for('index'))
    conn = get_db()
    appointments = conn.execute("SELECT a.*, u.name as pat_name FROM appointments a JOIN users u ON a.patient_id = u.id WHERE doctor_id=? ORDER BY app_date ASC", (session['user_id'],)).fetchall()
    conn.close()
    return render_template('doctor.html', appointments=appointments, name=session['name'])

@app.route('/admin')
def admin_dash():
    if session.get('role') != 'admin': return redirect(url_for('index'))
    conn = get_db()
    appointments = conn.execute('''SELECT a.*, p.name as pat_name, d.name as doc_name 
                                   FROM appointments a 
                                   JOIN users p ON a.patient_id = p.id 
                                   JOIN users d ON a.doctor_id = d.id
                                   ORDER BY app_date DESC''').fetchall()
    stats = conn.execute("SELECT SUM(fee) as total_fees, COUNT(*) as appt_count FROM appointments").fetchone()
    conn.close()
    return render_template('admin.html', appointments=appointments, stats=stats)

# API FOR GRAPH MATRIX TESTING
@app.route('/api/book_test', methods=['POST'])
def api_book_test():
    data = request.json
    pat_id = data.get('patient_id')
    doc_id = data.get('doctor_id')
    date = data.get('date')
    time = data.get('time')
    history = data.get('history')
    fee = data.get('fee', 0)
    
    # Path tracking (1 -> 10)
    path = [1] # Node 1: Start
    
    # Node 2: Validate Patient Logged In / ID exists
    if not pat_id:
        path.extend([2, 10]) # Edge 1->2 (Not logged in) -> Edge 2->10 (Error End)
        return jsonify({"status": "error", "message": "Not logged in", "path": path}), 401
    
    path.append(3) # Edge 1->3 (Logged in)

    conn = get_db()
    # Node 3: Check Doctor Availability
    conflict = conn.execute("SELECT id FROM appointments WHERE doctor_id=? AND app_date=? AND app_time=?", (doc_id, date, time)).fetchone()
    if conflict:
        conn.close()
        path.extend([4, 10]) # Edge 3->4 (Doc unavailable) -> Edge 4->10 (Error End)
        return jsonify({"status": "error", "message": "Doctor unavailable", "path": path}), 400
    
    path.append(5) # Edge 3->5 (Doc available, form sent)
    
    # Node 5: Validate Request Form & Process Payment
    if not history or fee < 50:
        conn.close()
        path.extend([6, 10]) # Edge 5->6 (Form invalid/Payment fail) -> Edge 6->10 (Error End)
        return jsonify({"status": "error", "message": "Invalid details or insufficient fee (Min $50)", "path": path}), 400
        
    path.append(7) # Edge 5->7 (Form valid, Payment Success)
    
    # Node 8: Save Appointment Booking to DB
    path.append(8) # Edge 7->8 (Saving)
    conn.execute("INSERT INTO appointments (patient_id, doctor_id, app_date, app_time, medical_history, status, fee) VALUES (?, ?, ?, ?, ?, 'booked', ?)", 
                 (pat_id, doc_id, date, time, history, fee))
    conn.commit()
    conn.close()
    
    # Node 9: Notification/Confirmation
    path.append(9) # Edge 8->9 (Confirm)
    path.append(10) # Edge 9->10 (End)
    
    return jsonify({"status": "success", "message": "Appointment Confirmed", "path": path}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)
