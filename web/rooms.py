from flask_discord import requires_authorization
from flask import abort, render_template, request
from flask_socketio import ConnectionRefusedError, emit, join_room, leave_room
from functools import wraps
from core.web import app, discord, socket
from core.data import Player, Room

SESSIONS = {}

@app.route('/<string:room>')
@requires_authorization
def room_route(room):
    if not room.isalnum():
        abort(404) #invalid room name
    return render_template('index.html', room=room)

# silent failure to avoid exceptions
def requires_login(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not discord.authorized:
            print('♠') # just so it's not TOO silent
            return
        return func(*args, **kwargs)
    return wrapper

@socket.event
@requires_login
def connect():
    SESSIONS[request.sid] = {
        'rooms': []
    }
    user = discord.fetch_user()
    Player(user.id).set_user(user)
    
    return True

@socket.event
@requires_login
def join(room):
    if room in SESSIONS[request.sid]['rooms']:
        return
    
    join_room(room)
    SESSIONS[request.sid]['rooms'].append(room)
    Room(room).add_player(discord.fetch_user().id)
    
    
    emit('message', f'{discord.fetch_user().name} joined the party!', to=room)
    emit('user_join', Player(discord.fetch_user().id), to=room)
    
    return Room(room).get_players()

@socket.event
@requires_login
def leave(room):
    if room not in SESSIONS[request.sid]['rooms']:
        return False
    
    leave_room(room)
    
    SESSIONS[request.sid]['rooms'].remove(room)
    Room(room).remove_player(discord.fetch_user().id)
    
    
    emit('message', f'{discord.fetch_user().name} left the party!', to=room)
    emit('user_leave', Player(discord.fetch_user().id), to=room)

@socket.event
def disconnect():
    for room in SESSIONS[request.sid]['rooms']:
        leave(room)
    del SESSIONS[request.sid]
