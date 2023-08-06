import os
from flask import Flask, render_template, request, session, redirect, url_for
from flask_socketio import SocketIO, emit, join_room, leave_room
from werkzeug.utils import secure_filename
import MySQLdb

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app)

mysql = MySQLdb.connect(host='localhost', user='root', password='', db='chat_app', autocommit=True)

@app.route('/')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('index.html', username=session['username'])

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.cursor()
        cursor.execute('SELECT id, username FROM users WHERE username = %s AND password = %s', (username, password))
        user = cursor.fetchone()
        cursor.close()
        if user:
            session['user_id'] = user[0]
            session['username'] = user[1]
            return redirect(url_for('index'))
        else:
            return render_template('login.html', message='Invalid credentials. Please try again.')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.cursor()
        cursor.execute('INSERT INTO users (username, password) VALUES (%s, %s)', (username, password))
        cursor.close()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    return redirect(url_for('login'))

@socketio.on('join')
def on_join(data):
    if 'username' not in session:
        return
    user_id = session['user_id']
    username = session['username']
    room = data['room']
    join_room(room)
    emit('system_message', f'{username} has joined the room.', room=room)

@socketio.on('leave')
def on_leave(data):
    if 'username' not in session:
        return
    user_id = session['user_id']
    username = session['username']
    room = data['room']
    leave_room(room)
    emit('system_message', f'{username} has left the room.', room=room)

@socketio.on('message')
def handle_message(data):
    if 'username' not in session:
        return
    user_id = session['user_id']
    username = session['username']
    room = data['room']
    message = data['message']
    emit('message', {'username': username, 'message': message}, room=room)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)