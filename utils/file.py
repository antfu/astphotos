# -*- coding: utf-8 -*-

import os
import codecs
import json
from os              import listdir, mkdir
from os.path         import join, getmtime, exists, isfile
from shutil          import rmtree, copy2, copystat
from utils.minifier  import can_minify, auto_minify
from utils.output    import log

def read_json(filepath):
    with codecs.open(filepath, 'r', 'utf-8') as f:
        return json.loads(f.read())

def save_json(filepath,obj,prefix=''):
    prefix = prefix or ''
    with codecs.open(filepath, 'w', 'utf-8') as f:
        f.write(prefix + json.dumps(obj))

def read_if_exists(path):
    if os.path.exists(path):
        with codecs.open(path,'r','utf-8') as f:
            return f.read()
    return None

def mkdir_if_not(dst_path):
    if not exists(dst_path):
        mkdir(dst_path)

def clear_directory(path):
    rmtree(path)

def copydir(src,dst,minify=False):
    if not exists(dst):
        mkdir(dst)
    for itemname in listdir(src):
        src_path = join(src,itemname)
        if isfile(src_path):
            dst_path = join(dst,itemname)
            # if the files modify time is the same, do not copy
            if not exists(dst_path) or getmtime(src_path) != getmtime(dst_path):
                if minify and not '.min.' in itemname and can_minify(src_path):
                    # minify
                    log('  Minifing ',itemname, color='yellow')
                    auto_minify(src_path,dst_path)
                    copystat(src_path,dst_path)
                else:
                    log('  Copying ',itemname)
                    # use 'copy2' to keep file metadate
                    copy2(src_path,dst_path)
        else:
            # isdir
            copydir(src_path, join(dst,itemname), minify)


def change_ext(filepath,ext):
    return '.'.join(filepath.split('.')[:-1]+[ext])

def clear_ext(filepath):
    return '.'.join(filepath.split('.')[:-1])

def get_ext(filepath):
    return filepath.split('.')[-1]
