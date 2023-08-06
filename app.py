#import packages

from flask import Flask, render_template, request, session, redirect, url_for
from flask_socketio import SocketIO, emit, join_room, leave_room

#create app & secure key

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app)

#connect template our app

@app.route('/')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('index.html', username=session['username'])

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['username'] = request.form['username']
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@socketio.on('join')
def on_join(data):
    if 'username' not in session:
        return
    username = session['username']
    room = data['room']
    join_room(room)
    emit('system_message', f'{username} has joined the room.', room=room)

@socketio.on('leave')
def on_leave(data):
    if 'username' not in session:
        return
    username = session['username']
    room = data['room']
    leave_room(room)
    emit('system_message', f'{username} has left the room.', room=room)

@socketio.on('message')
def handle_message(data):
    if 'username' not in session:
        return
    username = session['username']
    room = data['room']
    message = data['message']
    emit('message', {'username': username, 'message': message}, room=room)

#add host and port
if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)