from flask_discord import requires_authorization
from flask import abort, render_template, request
from flask_socketio import ConnectionRefusedError, emit
from functools import wraps
from core.web import app, discord, socket
from core.data import Player, Room
from .rooms import requires_login


@socket.event
@requires_login
def damage(room):
    if Room(room).on_break():
        return
    
    damage_player(room, Player(discord.fetch_user().id))
    for player in Room(room).get_players():
        damage_player(room, player)
        
def damage_player(room, player):
    damage = Room(room).get_damage()
    if player.get_hp() > 0:
            player.damage(damage)
            emit('message', f'{player.get_user().name} takes {damage} damage!', to=room)
            if player.get_hp() <= 0:
                emit('message', f'{player.get_user().name} has been defeated!', to=room)



@socket.event
@requires_login
def attack(room):
    if not Room(room).on_break():
        return
    
    damage = Player(discord.fetch_user().id).get_damage()
    Room(room).damage(damage)
    emit('message', f'{discord.fetch_user().name} attacks for {damage} damage!', to=room)


@socket.event
@requires_login
def heal(room):
    if not Room(room).on_break():
        return
    
    Player(discord.fetch_user().id).damage(-10)
    emit('message', f'{discord.fetch_user().name} heals 10 HP!', to=room)
