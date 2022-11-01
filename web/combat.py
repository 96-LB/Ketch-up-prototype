from flask_discord import requires_authorization
from flask import abort, render_template, request
from flask_socketio import ConnectionRefusedError, emit
from functools import wraps
from core.web import app, discord, socket
from core.data import Player, Room
from .rooms import requires_login



def requires_party_member(func):
    @wraps(func)
    @requires_login
    def wrapper(room, *args, **kwargs):
        if Player(discord.fetch_user().id) not in Room(room).get_players():
            print('♦') # just so it's not TOO silent
            return
        return func(room, *args, **kwargs)
    return wrapper


@socket.event
@requires_party_member
def damage(room):
    if (
        Room(room).on_break()
        or Player(discord.fetch_user().id).get_hp() <= 0
    ):
        return
    
    damage_player(room, Player(discord.fetch_user().id))
    for player in Room(room).get_players():
        damage_player(room, player)

def damage_player(room, player):
    damage = Room(room).get_damage()
    if player.get_hp() > 0:
            player.damage(damage)
            emit('message', f'Procrabination attacks {player.get_user().name} for {damage} damage!', to=room)
            if player.get_hp() <= 0:
                emit('message', f'{player.get_user().name} has been knocked down!', to=room)



@socket.event
@requires_party_member
def attack(room):
    if (
        not Room(room).on_break() or
        Room(room).has_attacked(Player(discord.fetch_user().id)) or
        not Room(room).is_running() or
        Player(discord.fetch_user().id).get_hp() <= 0
    ):
        return
    
    Room(room).add_attacker(discord.fetch_user().id)
    damage = Player(discord.fetch_user().id).get_damage()
    Room(room).damage(damage)
    emit('message', f'{discord.fetch_user().name} attacks Procrabination for {damage} damage!', to=room)
    
    if Room(room).get_hp() <= 0:
        emit('message', f'Procrabination has been defeated!', to=room)
        emit('victory', to=room)
        for player in Room(room).get_players():
            player.add_exp(1)
        Room(room).reset()


@socket.event
@requires_party_member
def heal(room):
    if (
        not Room(room).on_break() or
        Room(room).has_healed(Player(discord.fetch_user().id)) or
        not Room(room).is_running()
    ):
        return
    
    Room(room).add_healer(discord.fetch_user().id)
    Player(discord.fetch_user().id).damage(-10)
    if Player(discord.fetch_user().id).get_hp() == 10:
        emit('message', f'{discord.fetch_user().name} has gotten back up!', to=room)
    else:
        emit('message', f'{discord.fetch_user().name} heals 10 HP!', to=room)
