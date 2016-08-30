
from os.path import exists
from codecs  import open
from json    import dumps, loads

class JsonEditor:
    def __init__(self, path, data=None):
        self.path = path
        if data == None:
            if exists(self.path):
                with open(self.path, 'r', 'utf-8') as f:
                    data = loads(f.read())
            else:
                data = {}
        self.data = data

    def __getitem__(self, key):
        return self.data.get(key, None)

    def __setitem__(self, key, value):
        self.data[key] = value
        self.save()

    def __delitem__(self, key):
        if key in self.data.keys():
            del(self.data[key])
            self.save()

    def save(self):
        with open(self.path, 'w', 'utf-8') as f:
            f.write(dumps(self.data))
