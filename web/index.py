from core.data import Player, Room
from core.web import app, discord
from flask import render_template
from flask_discord import requires_authorization

@app.route('/')
def index():
    output = 'hi'
    if discord.authorized:
        output += f', {discord.fetch_user().name}'
        output += '<br>'
        output += 'you have ' + str(Player(discord.fetch_user().id).get_exp()) + ' exp'
        output += '<br>'
        output += '<a href="/logout">logout</a>'
    else:
        output += '<br>'
        output += '<a href="/login">login</a>'
    return output
