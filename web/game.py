from flask_discord import requires_authorization
from core.web import app, discord, socket
from flask import abort, render_template, request
from flask_socketio import ConnectionRefusedError, emit, join_room, leave_room

sessions = {}
rooms = {}

@app.route('/<string:room>')
@requires_authorization
def room_route(room):
    if not room.isalnum():
        abort(404) #invalid room name
    return render_template('index.html', room=room)


@socket.event
def connect():
    if not discord.authorized:
        print('rejected!')
        raise ConnectionRefusedError('You must log in to proceed.')
    
    sessions[request.sid] = {
        'rooms': []
    }
        
    return True

@socket.event
def join(room):
    if room in sessions[request.sid]['rooms']:
        return False
    
    join_room(room)
    sessions[request.sid]['rooms'].append(room)
    emit('message', f'{discord.fetch_user().name} joined {room}!', to=room)

@socket.event
def leave(room):
    if room not in sessions[request.sid]['rooms']:
        return False
    
    leave_room(room)
    sessions[request.sid]['rooms'].remove(room)
    emit('message', f'{discord.fetch_user().name} left {room}!', to=room)

@socket.event
def disconnect():
    for room in sessions[request.sid]['rooms']:
        leave(room)
    del sessions[request.sid]
