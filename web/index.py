from core.data import Player, Room
from core.web import app, discord
from flask import render_template
from flask_discord import requires_authorization

@app.route('/')
def index():
    return 'hi'
