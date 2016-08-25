# -*- coding: utf-8 -*-

import os
import codecs
import json
import shutil

def read_json(filepath):
    with codecs.open(filepath, 'r', 'utf-8') as f:
        return json.loads(f.read())

def save_json(filepath,obj,prefix=''):
    with codecs.open(filepath, 'w', 'utf-8') as f:
        f.write(prefix + json.dumps(obj))

def read_if_exists(path):
    if os.path.exists(path):
        with codecs.open(path,'r','utf-8') as f:
            return f.read()
    return None

def clear_directory(path):
    shutil.rmtree(path)



def change_ext(filepath,ext):
    return '.'.join(filepath.split('.')[:-1]+[ext])

def clear_ext(filepath):
    return '.'.join(filepath.split('.')[:-1])

def get_ext(filepath):
    return filepath.split('.')[-1]
