import pytesseract
from PIL import Image
from flask import Flask, request, render_template, redirect, url_for, session, Response, flash, jsonify
import re
import io 
import requests
import base64
import sqlite3
import csv

app = Flask(__name__)
app.secret_key = "super secret key"
def connect():
    conn = sqlite3.connect('hub.db')
    conn.row_factory = sqlite3.Row
    return conn 

conn = connect()
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    password TEXT NOT NULL
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS student (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            section TEXT NOT NULL,
            course TEXT NOT NULL,
            year_graduated INTEGER,
            awards TEXT
            image BLOB
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS employee (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    position TEXT,
    salary REAL
)
''')

conn.commit()
conn.close()

@app.route('/')
def home():
    return render_template("index.html", title="Reader")


@app.route('/scanner', methods=['POST', 'GET'])
def scanner():
    if request.method == 'POST':
        value = request.form.get("text")
        txtdata = value.split('data:image/jpeg;base64,')[-1].strip()
        test = Image.open(io.BytesIO(base64.b64decode(txtdata)))
        test.save('test1.jpeg')
        scanned_text = pytesseract.image_to_string(Image.open(r'C:\Users\Luis\Desktop\luis\test1.jpeg'))
        if scanned_text == '':
            return render_template("index.html", value='py error')
        else:
            name = scanned_text.strip()
            cursor = connect()
            check = cursor.execute('SELECT * FROM student WHERE name LIKE ?', ('%' + name + '%',)).fetchone()
        
            
            if check == None:
                return render_template("index.html", value=check, val=name)
            else:
                session['data'] = {
                "name": check['name'],
                "year": check['year'],
                "motto": check['motto'],
                "awards": check['awards'],
        }
    return redirect(url_for('result'))
@app.route('/result')
def result():
    if "data" in session:
        data = session['data']
        return render_template(
            "result.html",
            name=data['name'],
            year=data['year'],
            motto=data['motto'],
            awards=data['awards'],
        )
    else:
        return "Wrong request method."  
@app.route('/dash')
def dashboard():
    if 'user_id' in session:
        return render_template('dashboard.html', username=session['username'])
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = connect()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()

        if user and password:
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if not username or not password or not confirm_password:
            flash('Please fill out all fields')
            return redirect(url_for('register'))

        if password != confirm_password:
            flash('Passwords do not match')
            return redirect(url_for('register'))

        try:
            conn = connect()
            conn.execute('INSERT INTO users (username, password) VALUES (?, ?)',
                         (username, password))
            conn.commit()
            conn.close()
            flash('Registration successful, please log in.')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username already exists')
            return redirect(url_for('register'))

    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/student', methods=['GET' , 'POST'])
def student():
    if request.method == 'POST':
        if 'file' in request.files:
            file = request.files['file']
            if file and file.filename.endswith('.csv'):
                file_stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
                reader = csv.DictReader(file_stream)
                conn = connect()
                for row in reader:
                    conn.execute('''
                        INSERT INTO student (name, section, course, year_graduated, awards)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (row['name'], row['section'], row['course'], row['year_graduated'], row['awards']))
                conn.commit()
                conn.close()
                return redirect(url_for('student'))
        else:
            name = request.form['name']
            section = request.form['section']
            course = request.form['course']
            year_graduated = request.form['year_graduated']
            awards = request.form['awards']
            
            conn = connect()
            conn.execute('''
                INSERT INTO student (name, section, course, year_graduated, awards)
                VALUES (?, ?, ?, ?, ?)
            ''', (name, section, course, year_graduated, awards))
            conn.commit()
            conn.close()
            return redirect(url_for('student'))
    6
    conn = connect()
    students = conn.execute('SELECT * FROM student').fetchall()
    conn.close()
    return render_template('student.html', students=students)


if __name__ == '__main__':
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    app.run(host="0.0.0.0", port=5000, debug=True)
    app.run(ssl_context='adhoc')
