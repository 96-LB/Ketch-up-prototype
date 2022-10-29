import os
from base64 import b64encode
from flask import Flask
from flask_discord import DiscordOAuth2Session
from importlib import import_module
from threading import Thread

#sets up a flask application
app = Flask('Ketchup')
app.url_map.strict_slashes = False
app.config['SERVER_NAME'] = os.getenv('SERVER_NAME', 'localhost:5000')
app.config['SECRET_KEY'] = b64encode(os.getenv('SECRET_KEY').encode('utf-8'))
app.jinja_env.filters['debug'] = lambda x: print(x) or ''
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = 'true' #suppresses reverse-proxy http errors - proxy should already force https

# use http if running locally
if app.config['SERVER_NAME'] == 'localhost:5000':
    app.config['PREFERRED_URL_SCHEME'] = 'http'
    app.config['DISCORD_REDIRECT_URI'] = f'http://{app.config["SERVER_NAME"]}/callback'
else:
    app.config['PREFERRED_URL_SCHEME'] = 'https'
    app.config['DISCORD_REDIRECT_URI'] = f'https://{app.config["SERVER_NAME"]}/callback'

#loads in discord environment variables
for key in ['CLIENT_ID', 'CLIENT_SECRET']:
    key = 'DISCORD_' + key
    app.config[key] = os.environ[key]

#start a discord oauth application
discord = DiscordOAuth2Session(app)
app.jinja_env.globals['discord'] = discord

def jinja_env(f):
    #adds a function to the jinja environment
    app.jinja_env.globals[f.__name__] = f
    return f

#loads each module in the web folder
for file in os.listdir('web'):
    if file.endswith('.py'):
        import_module('web.' + file[:-3])

def run():
    #runs the webserver in a separate thread
    thread = Thread(target=lambda: app.run('0.0.0.0'))
    thread.start()
