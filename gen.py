#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import codecs
import datetime
import jinja2
import htmlmin

from os.path            import join
from config             import configs as cfg

from utils.parser       import template_render
from utils.output       import log
from utils.file         import copydir, mkdir_if_not
from core.index         import load_and_save

def gen():
    log('*** Generator Start ***', color='cyan')

    log('- Copying static files...', color='cyan')
    copy_static()
    log('- Copying completed', color='cyan')

    log('- Generating Structure tree...', color='cyan')
    generate_and_save()
    log('- Generating completed', color='cyan')

    log('- Rendering template file...', color='cyan')
    render_index()
    log('- Rendering completed', color='cyan')

    log('*** Task Completed ***', color='cyan')


def copy_static():
    mkdir_if_not(cfg.src_dir)
    copydir(join(cfg.src_dir,cfg.static_dir),join(cfg.out_dir,cfg.static_dir),cfg.minify)
    copydir(join(cfg.src_dir,cfg.themes_dir,cfg.theme,cfg.static_dir),join(cfg.out_dir,cfg.static_dir),cfg.minify)

def render_index():
    cfg.gentime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    index_path = join(cfg.out_dir,'index.html')
    template_render(index_path,cfg=cfg)

def generate_and_save():
    load_and_save(cfg.img_dir, join(cfg.out_dir,cfg.static_dir))

if __name__ == '__main__':
    import sys

    argv = sys.argv
    if len(argv) < 2 or argv[1] == 'gen':
        gen()
    elif argv[1] == 'clear':
        path = cfg.out_dir
        if input('Deleting "' + path + '", are you sure? [y/n]') == 'y':
            clear_directory(path)
    elif argv[1] == 'host':
        import utils.webhost
        utils.webhost.run()
    elif argv[1] == 'editor':
        import editor.editor
        editor.editor.run()
