import re
import os
import logging
from flask import Flask, render_template, request, redirect, url_for, session, make_response
from flask_bcrypt import Bcrypt
from flask_mysqldb import MySQL
import MySQLdb.cursors
from google.cloud import speech_v1p1beta1 as speech
import mysql.connector
from flask import jsonify
import database  # import the database module
import MySQLdb
# import wave
# import io
# from pickle import FALSE
from flask_cors import CORS



app = Flask(__name__)
app.secret_key = 'your secret key'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_DB'] = 'mydatabase'

mysql = MySQL(app)

bcrypt = Bcrypt(app)


#The beggining of the section that communicates with the Google Speech To text API.---------------------BEGIN----
# Define the path to the Google Cloud credentials and set environment variable
key_path = 'C:/Users/keish/OneDrive/Desktop/mykey.json'
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = key_path


@app.route('/speech_to_text', methods=['POST', 'GET'])
def process_audio():
    # Get the audio data from the request
    blob = request.data
    
    # Get the user id from the session
    users_id = session['id']

    # if not blob:
    #     return jsonify({'error': 'Audio data not provided in the request.'}), 400

    # Create a client instance for the Speech-to-Text API
    client = speech.SpeechClient()

    # Set the audio configuration
    # blob = request.get_data(cache=False)
    audio = speech.RecognitionAudio(content=blob)

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.MP3,
        sample_rate_hertz=48000,
        language_code='en-US',
        # model ="default",
        audio_channel_count=1,
        enable_word_time_offsets=True,
        enable_automatic_punctuation=True,
        enable_speaker_diarization=True,
        use_enhanced=True,
        diarization_speaker_count=1,
        speech_contexts=[
            speech.SpeechContext(
                phrases=["bought", "sold", "capital", "GHS", "banana", "salt", "bathing soap", "flour"
                         "soap", "canned fish", "spaghetti", "Peppe", "cooking oil", "tampico",
                         "kalipoo", "cereas", "cornflakes", "magarine", "royco", "chocolate biscuits",
                         "ice cream", "sanitary pads", "Detol", "noodles", "popcorn", "powdered milk",
                         "fresh milk", "fanta", "Bigoo", "sprite", "skirts", "trousers", "top", "jeans", "t-shirts"
                         "chocolate milk", "Nescafe coffee", "fruit Telli", "jollof soup", "red source", "fish", "Don Simon"

                         ],
                boost=30
            ),
            speech.SpeechContext(
                phrases=["cedis", "2", "sugar"],
                boost=40
            ),

            speech.SpeechContext(
                phrases=["bought item", "quantity", "amount",
                         "sold item", "3 cedis", "10 cedis"],
                boost=20
            ),

            speech.SpeechContext(
                phrases=["Sold banana 10 cedis", "Bought bananas 100 cedis", "Capital 2000 cedis", "Sold chocolate biscuits 4 cedis", "Sold fresh milk 30 cedis", "Sold tampico 6 cedis",
                         "Bought popcorn 100 cedis", "Sold cooking oil 50 cedis", " Bought sprite 4 cedis", "Sold sanitary pads 12 cedis"],
                boost=20
            ),
        ]
    )

    #     speech_contexts = [
    #         {
    #         "phrases": ["bought", "sold", "capital", "cedis"]
    #         "boost": 5},
    #                        {"phrases": ["bought sugar GHS3", "sold 12 bananas GHS10"],}

    #     ]

    # )

    # Use the Speech-to-Text API to transcribe the audio
    response = client.recognize(config=config, audio=audio)

    # Extract the transcription and confidence level from the response
    transcription = response.results[0].alternatives[0].transcript
    confidence = response.results[0].alternatives[0].confidence
    
    
    textlist = transcription
    print(users_id)
    print(confidence)
    
    # Store the transcription in the database
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    print(cursor)
    cursor.execute("INSERT INTO voice_transcripts (transcription, users_id, confidence_level) VALUES (%s, %s, %s)", (textlist, users_id, confidence))
    mysql.connection.commit()
    
    
    # return results as json
    return textlist
    # return jsonify({'transcription': transcription})
#The beggining of the section that communicates with the Google Speech To text API.------------------END---




#Rendering Templates
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/transcripts')
def transcripts():
    return render_template('transcripts.html')


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
    app.run(debug=True)