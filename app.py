from flask import Flask, render_template, request, redirect, url_for, session, g
import sqlite3
import re
import bcrypt
from flask_login import current_user, login_required

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# create a connection to the SQLite database
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect('mydatabase.db')
    return db

# create a table for storing user data if it does not exist already
def create_user_table():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
# create a table for storing user data if it does not exist already
def create_products_table():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            
            price REAL NOT NULL
        )
    ''')
    conn.commit()
# create a table for storing voice transcripts if it does not exist already
def create_voice_transcripts_table():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS voice_transcripts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            transcript TEXT NOT NULL,
            date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    conn.commit()

# function to store voice transcripts in the database
def store_voice_transcript(user_id, transcript):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO voice_transcripts (user_id, transcript) VALUES (?, ?)', (user_id, transcript))
    conn.commit()

@app.route('/store-voice-data', methods=['POST'])
def store_voice_data():
    # get the user ID from the session
    user_id = session.get('user_id')

    # get the voice transcript data from the request
    voice_transcript = request.form.get('voice_transcript')

    # store the voice transcript data in the database
    store_voice_transcript(user_id, voice_transcript)

    # return a success response to the client
    return {'status': 'success'}

# function to hash passwords
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

# function to check if a password is valid
def check_password(password, hashed_password):
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password)

@app.before_request
def before_request():
    g.db = get_db()
    g.cursor = g.db.cursor()

@app.teardown_request
def teardown_request(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/')
def index():
    return render_template('index.html')
     

@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        # regular expressions to validate email and username format
        if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif check_email(email):
            msg = 'Email already exists!'
        elif not re.match(r'^[a-zA-Z0-9_-]{3,20}$', username):
            msg = 'Username must contain only characters and numbers and be between 3 and 20 characters long!'
        elif not check_password_strength(password):
            msg = 'Password must be at least 8 characters long and contain at least one uppercase letter, one lowercase letter, one digit, and one special character!'
        else:
            # hash password before storing it in the database
            hashed_password = hash_password(password)
            g.cursor.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)', (username, email, hashed_password))
            g.db.commit()
            msg = 'You have successfully registered!'
            return redirect('/login')
    elif request.method == 'POST':
        msg = 'Please fill out the form!'
    return render_template('register.html', msg=msg)

def check_email(email):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
    result = cursor.fetchone()
    if result is None:
        return False
    else:
        return True

def check_password_strength(password):
    if len(password) < 8:
        return False
    if not any(c.isupper() for c in password):
        return False
    if not any(c.islower() for c in password):
        return False
    if not any(c.isdigit() for c in password):
        return False
    if not any(c in '!@#$%^&*()_+-={}[]|\:;"<>,.?/~`' for c in password):
        return False
    return True

@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        g.cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = g.cursor.fetchone()
        if user and check_password(password, user[3]):
            session['loggedin'] = True
            session['id'] = user[0]
            session['username'] = user[1]
            session['username'] = username

            return redirect('/record')
        else:
            msg = 'Incorrect username/password!'
    return render_template('login.html', msg=msg)

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect('/login')


@app.route('/dashboard')
def dashboard():
    username = session.get('username')
    return render_template('dashboard.html', username=username)


@app.route('/record')
def record():
    return render_template('record.html')

@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/faqs')
def faqs():
    return render_template('faqs.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/revenue')
def revenue():
    if 'loggedin' in session:
        return render_template('revenue.html')
    else:
        return redirect('/login')


@app.route('/update_profile', methods=['GET', 'POST'])
def update_profile():
    msg = ''
    if request.method == 'POST' and 'name' in request.form and 'email' in request.form:
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        # Check if the user entered their current password correctly
        user_id = session['id']
        g.cursor.execute('SELECT password FROM users WHERE id=?', (user_id,))
        result = g.cursor.fetchone()
        if result and check_password(result['password'], password):
            # If the user entered their current password correctly, check if the new password is valid
            if new_password == confirm_password:
                hashed_password = generate_password_hash(new_password)
                g.cursor.execute('UPDATE users SET username=?, email=?, password=? WHERE id=?', (name, email, hashed_password, user_id))
                g.db.commit()
                msg = 'Profile updated successfully!'
                return redirect('/dashboard')
            else:
                msg = 'New password and confirm password must match'
        else:
            msg = 'Invalid password'

    return render_template('update_profile.html', msg=msg)


if __name__ == '__main__':
    create_user_table()
    create_products_table()
    create_voice_transcripts_table()
    app.run(debug=True)
