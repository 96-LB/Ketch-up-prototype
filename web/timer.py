from flask_discord import requires_authorization
from flask import abort, render_template, request
from flask_socketio import ConnectionRefusedError, emit
from functools import wraps
from core.web import app, discord, socket
from core.data import Player, Room
from .rooms import SESSIONS, requires_login

def requires_leader(func):
    @wraps(func)
    @requires_login
    def wrapper(room, *args, **kwargs):
        if Player(discord.fetch_user().id) != Room(room).get_leader():
            print('♥') # just so it's not TOO silent
            return None
        return func(room, *args, **kwargs)
    return wrapper



@socket.event
@requires_leader
def start_timer(room):
    emit('message', 'It\'s time to Ketch up on your work~!', to=room)