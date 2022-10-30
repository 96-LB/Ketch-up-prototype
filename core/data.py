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
                return json.load(f)
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
        self._data.setdefault('name', 'Unknown User')
    
    def get_id(self):
        return self._id
    
    def get_user(self):
        return self._data['user']
    
    def set_user(self, user):
        self._data['user'] = user
        
    def to_dict(self):
        return {
            'id': self.get_id(),
            'name': self._data['user'].name
        }



class Room(JSONData):
    
    def __init__(self, room):
        super().__init__( f'data/rooms/{room}.json')
        self._data.setdefault('players', [])
        self._data.setdefault('timer', 0)
        self._data.setdefault('rest', False)
    
    def add_player(self, player):
        self._data['players'].append(Player(player))
    
    def remove_player(self, player):
        self._data['players'].remove(Player(player))
    
    def get_players(self):
        return list(self._data['players'])
    
    def get_leader(self):
        return (self._data['players'] or [None])[0]
    
    @update
    def start_timer(self, minutes, rest=False):
        self._data['timer'] = int(time() + minutes * 60)
        self._data['rest'] = rest
    
    def get_remaining_time(self):
        return max(0, self._data['timer'] - int(time()))
    
    def on_break(self):
        return self._data['rest']
    
    def to_dict(self):
        return {
            'timer': self._data['timer'],
            'rest': self._data['rest']
        }