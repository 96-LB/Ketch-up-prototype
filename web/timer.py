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
            return
        return func(room, *args, **kwargs)
    return wrapper


# start a thread to ping the client
def start_timer(room, minutes, rest=False):
    Room(room).start_timer(minutes, rest)
    


def timer_loop(room):
    while True:
        socket.sleep(1)
        socket.emit('timer', Room(room).get_remaining_time(), to=room)
        if Room(room).get_remaining_time() <= 0:
            socket.emit('message', 'timer finished', to=room)
            break


@socket.event
@requires_leader
def start_timer(room):
    if Room(room).get_remaining_time() > 0:
        return
    
    Room(room).start_timer(25 / 100) # TODO: increase time
    socket.start_background_task(timer_loop, room)
    emit('message', 'It\'s time to Ketch up on your work~!', to=room)