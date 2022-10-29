from core.data import Player, Room
from core.web import app, discord
from flask import render_template
from flask_discord import requires_authorization

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/pineappleselena')
@requires_authorization
def pineappleselena():
    player = Player(discord.fetch_user().id)
    player.set_test(player.get_test() + 1)
    return player.to_json() + '\n\n' + str(Room('pineappleselena').get_test())