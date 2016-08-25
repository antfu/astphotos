
import os
from   utils.file   import read_json

class infodict(dict):
    def update_json(self,jsonpath):
        if os.path.exists(jsonpath):
            self.update(read_json(jsonpath))

    def __setattr__(self,key,value):
        self[key]=value

    def __getattr__(self,key):
        return self.get(key,None)

    def __delattr__(self,key):
        if key in self.keys():
            del(self[key])