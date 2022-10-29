import json, os
from abc import ABC, abstractmethod
from functools import wraps

for path in ['data', 'data/players', 'data/rooms']:
    if not os.path.exists(path):
        os.mkdir(path)

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
        if file not in cls._instances:
            obj = super().__new__(cls)
            cls._instances[file] = obj
            return obj
        else:
            return cls._instances[file]
    
    @abstractmethod
    def __init__(self, file):
        self._file = file
        self._data = self.load(file)
        
    @abstractmethod
    def to_json(self):
        return json.dumps(self.__dict__)
    
    def update(self):
        with open(self._file, 'w') as f:
            f.write(self.to_json())


class Player(JSONData):
    
    def __init__(self, player):
        super().__init__(f'data/players/{player}.json')
        self._id = str(player)
        self._data.setdefault('test', 0)
    
    def get_id(self):
        return self._id
    
    def get_test(self):
        return self._data['test']
    
    @update
    def set_test(self, value):
        self._data['test'] = value
    
    
    
    def to_json(self):
        return json.dumps({'test': self.get_test()})



class Room(JSONData):
    
    def __init__(self, room):
        super().__init__( f'data/rooms/{room}.json')
        self._data.setdefault('test2', 0)
        self._data.setdefault('players', [])
    
    def get_test(self):
        return self._data['test2']
    
    @update
    def set_test(self, value):
        self._data['test2'] = value
    
    def add_player(self, player):
        self._data['players'].append(player)
    
    def remove_player(self, player):
        self._data['players'].remove(player)
    
    def get_players(self):
        return list(self._data['players'])
    
    def to_json(self):
        return json.dumps({'test2': self.get_test()})