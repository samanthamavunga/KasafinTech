from flask import Flask, render_template, request, redirect, url_for, session, make_response
from flask_bcrypt import Bcrypt
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import database  # import the database module

app = Flask(__name__)
app.secret_key = 'your secret key'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_DB'] = 'mydatabase'

mysql = MySQL(app)

bcrypt = Bcrypt(app)

# create a table for storing voice transcripts if it does not exist already
def create_voice_transcripts_table():
    with app.app_context():
        conn = MySQLdb.connect(host="localhost", user="root",  db="mydatabase")
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS voice_transcripts (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                transcript TEXT NOT NULL,
                date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        conn.commit()
        cursor.close()
        conn.close()

# function to store voice transcripts in the database
def store_voice_transcript(user_id, transcript):
    with app.app_context():
        cursor = mysql.connection.cursor()
        cursor.execute('INSERT INTO voice_transcripts (user_id, transcript) VALUES (%s, %s)', (user_id, transcript))
        mysql.connection.commit()
        cursor.close()

@app.route('/store-voice-data', methods=['POST'])
def store_voice_data():
    # get the user ID from the session
    user_id = session.get('user_id')

    # get the voice transcript data from the request
    voice_transcript = request.form.get('voice_transcript')

    # store the voice transcript data in the database using the store_voice_transcript function
    store_voice_transcript(user_id, voice_transcript)

    # create a success response
    response = make_response({'status': 'success'})
    response.headers['Content-Type'] = 'application/json'
    return response




@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE username = % s', (username, ))
        account = cursor.fetchone()
        if account and bcrypt.check_password_hash(account['password'], password):
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            msg = 'Logged in successfully !'
            return redirect(url_for('record'))
        else:
            msg = 'Incorrect username / password !'
    return render_template('login.html', msg=msg)

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
        account = cursor.fetchone()
        if account:
            msg = 'Account with this email already exists!'
            return render_template('register.html', msg=msg)
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]{3,20}$', username):
            msg = 'Username must contain only characters and numbers and be between 3 and 20 characters long!'
        elif not re.match(r'[A-Za-z0-9@#$%^&+=]{8,}', password):
            msg = 'Password must be at least 8 characters long and contain at least one special character, one uppercase letter, one lowercase letter and one digit!'
        else:
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
            cursor.execute('INSERT INTO users VALUES (NULL, %s, %s, %s)', (username, email, hashed_password,))
            mysql.connection.commit()
            msg = 'You have successfully registered!'
            return redirect(url_for('login'))
    elif request.method == 'POST':
        msg = 'Please fill out the form!'
    return render_template('register.html', msg=msg)


@app.route('/recordingpage')
def recordingpage():
    return render_template('recordingpage.html')


@app.route('/record')
def record():
    if 'loggedin' in session:
        return render_template('record.html', username=session['username'])
    return redirect(url_for('login'))


@app.route('/dashboard')
def dashboard():
    # Check if user is logged in
    if 'loggedin' in session:
        # Retrieve user's name from session
        username = session['username']
        msg = request.args.get('msg')
        return render_template('dashboard.html', username=username,msg=msg)
    else:
        return redirect(url_for('login'))


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
    if 'loggedin' in session:
        if request.method == 'POST':
            # handle form submission
            username = request.form['name']
            email = request.form['email']
            password = request.form['password']
            new_password = request.form['new_password']
            confirm_password = request.form['confirm_password']
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM users WHERE id = %s', (session['id'],))
            account = cursor.fetchone()
            if account and bcrypt.check_password_hash(account['password'], password):
                if new_password == confirm_password:
                    hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')
                    cursor.execute('UPDATE users SET username = %s, email = %s, password = %s WHERE id = %s', (username, email, hashed_password, session['id'],))
                    mysql.connection.commit()
                    msg = 'Your profile has been updated!'
                    return redirect(url_for('dashboard'), msg=msg)
                else:
                    msg = 'New password and confirm password do not match!'
            else:
                msg = 'Incorrect password!'
            return render_template('dashboard.html', user=account, msg=msg)
        else:
            # load form with user data
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM users WHERE id = %s', (session['id'],))
            account = cursor.fetchone()
            return render_template('dashboard.html', user=account)
    else:
        return redirect(url_for('login'))



    
if __name__ == '__main__':
    
    app.run(port = 5000)
    create_voice_transcripts_table()
    app.run(debug=True)

