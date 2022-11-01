import json, os
from abc import ABC, abstractmethod
from functools import wraps
from time import time

for path in ['data', 'data/players', 'data/rooms']:
    if not os.path.exists(path):
        os.mkdir(path)

# override the default json encoder to encode our JSONData objects
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, JSONData):
            return obj.to_dict()
        return json.JSONEncoder.default(self, obj)
json.JSONEncoder.default = CustomJSONEncoder.default

class Dummy():
    def __getattr__(self, attr):
        return ''



def update(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        func(self, *args, **kwargs)
        self.update()
    return wrapper


class JSONData(ABC):
    
    _instances = {}
    
    @staticmethod
    def load(file):
        if os.path.exists(file):
            with open(file, 'r') as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    return {}
        else:
            return {}
    
    def __new__(cls, file):
        name = f'{cls}::{file}'
        if name  not in cls._instances:
            obj = super().__new__(cls)
            cls._instances[name] = obj
            return obj
        else:
            return cls._instances[name]
    
    @abstractmethod
    def __init__(self, file):
        if getattr(self, '__inited__', False):
            return
        self.__inited__ = True
        self._file = file
        self._data = self.load(file)
    
    @abstractmethod
    def to_dict(self):
        ...
    
    def update(self):
        with open(self._file, 'w') as f:
            f.write(json.dumps(self))


class Player(JSONData):
    
    def __init__(self, player):
        super().__init__(f'data/players/{player}.json')
        self._id = str(player)
        self._data.setdefault('user', Dummy())
        self._data.setdefault('hp', 100)
        self._data.setdefault('max_hp', 100)
        self._data.setdefault('exp', 0)
        self._data.setdefault('damage', 25)
    
    def get_id(self):
        return self._id
    
    def get_user(self):
        return self._data['user']
    
    def set_user(self, user):
        self._data['user'] = user
    
    @update
    def damage(self, amount):
        self._data['hp'] -= amount
        self._data['hp'] = min(max(self._data['hp'], 0), self._data['max_hp'])
    
    def get_damage(self):
        return self._data['damage']
    
    def get_hp(self):
        return self._data['hp']
    
    def get_exp(self):
        return self._data['exp']
    
    @update
    def add_exp(self, amount):
        self._data['exp'] += amount
    
    def to_dict(self):
        return {
            'id': self.get_id(),
            'name': self._data['user'].name,
            'hp': self._data['hp'],
            'max_hp': self._data['max_hp'],
            'exp': self._data['exp'],
            'damage': self._data['damage']
        }



class Room(JSONData):
    
    def __init__(self, room):
        super().__init__( f'data/rooms/{room}.json')
        self._data.setdefault('players', [])
        self._data.setdefault('timer', 0)
        self._data.setdefault('rest', True)
        self._data.setdefault('hp', 0)
        self._data.setdefault('max_hp', 0)
        self._data.setdefault('damage', 0)
        self._data.setdefault('attackers', []) # list of players who have attacked this turn
        self._data.setdefault('healers', []) # list of players who have healed this turn
        self._data.setdefault('running', False) # is the game running or not
    
    def add_player(self, player):
        self._data['players'].append(Player(player))
    
    def remove_player(self, player):
        self._data['players'].remove(Player(player))
    
    def get_players(self):
        return list(self._data['players'])
    
    def get_leader(self):
        return (self._data['players'] or [None])[0]
    
    @update
    def add_attacker(self, player):
        self._data['attackers'].append(Player(player))
    
    @update
    def add_healer(self, player):
        self._data['healers'].append(Player(player))
    
    def has_attacked(self, player):
        return player in self._data['attackers']
    
    def has_healed(self, player):
        return player in self._data['healers']
    
    @update
    def clear_turn(self):
        self._data['attackers'] = []
        self._data['healers'] = []
    
    @update
    def start_timer(self, minutes, rest=False):
        self._data['timer'] = int(time() + minutes) # TODO: make this not 60x faster than it should be
        self._data['rest'] = rest
        self._data['running'] = True
    
    def get_remaining_time(self):
        return max(0, self._data['timer'] - int(time()))
    
    def on_break(self):
        return self._data['rest']
        
    @update
    def damage(self, amount):
        self._data['hp'] -= amount
        self._data['hp'] = min(max(self._data['hp'], 0), self._data['max_hp'])
    
    def get_damage(self):
        return self._data['damage']
    
    def get_hp(self):
        return self._data['hp']
    
    @update
    def summon_boss(self, hp, damage):
        self._data['hp'] = hp
        self._data['max_hp'] = hp
        self._data['damage'] = damage
    
    
    @update
    def reset(self):
        self._data['hp'] = 0
        self._data['max_hp'] = 0
        self._data['damage'] = 0
        self._data['timer'] = 0
        self._data['rest'] = True
        self._data['attackers'] = []
        self._data['healers'] = []
        self._data['running'] = False
    
    def is_running(self):
        return self._data['running']
    
    def to_dict(self):
        return {
            'timer': self._data['timer'],
            'rest': self._data['rest'],
            'hp': self._data['hp'],
            'max_hp': self._data['max_hp'],
            'damage': self._data['damage'],
            'attackers': [player.get_id() for player in self._data['attackers']],
            'healers': [player.get_id() for player in self._data['healers']],
        }