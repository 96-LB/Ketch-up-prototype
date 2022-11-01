from core.data import Player
from core.web import app, discord

@app.route('/')
def index():
    output = 'hi'
    if discord.authorized:
        player = Player(discord.fetch_user().id)
        output += f', {discord.fetch_user().name}'
        output += '<br>'
        output += f'you have {player.get_exp()} exp and {player.get_hp()}/{100} hp'
        output += '<br>'
        output += '<a href="/logout">logout</a>'
    else:
        output += '<br>'
        output += '<a href="/login">login</a>'
    return output
