from core.web import app, discord, socket
from flask import request
from flask_socketio import ConnectionRefusedError, emit, join_room, leave_room

sessions = {}


@socket.event
def connect():
    if not discord.authorized:
        print('rejected!')
        raise ConnectionRefusedError('You must log in to proceed.')
    print(f'{discord.fetch_user().name} connected!')
    
    sessions[request.sid] = {
        'rooms': []
    }
    
    print(sessions)
    
    return True

@socket.event
def join(room):
    if room in sessions[request.sid]['rooms']:
        return False
    
    join_room(room)
    sessions[request.sid]['rooms'].append(room)
    print(f'{discord.fetch_user().name} joined {room}!')
    emit('message', f'{discord.fetch_user().name} joined {room}!', to=room)
    
    print(sessions)

@socket.event
def leave(room):
    if room not in sessions[request.sid]['rooms']:
        return False
    
    leave_room(room)
    sessions[request.sid]['rooms'].remove(room)
    print(f'{discord.fetch_user().name} left {room}!')
    emit('message', f'{discord.fetch_user().name} left {room}!', to=room)
    
    print(sessions)

@socket.event
def disconnect():
    for room in sessions[request.sid]['rooms']:
        leave(room)
    del sessions[request.sid]
    
    print(f'{discord.fetch_user().name} disconnected!')
    
    print(sessions)
