#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
import glob
import codecs
import random
import datetime
import shutil
import jinja2
import htmlmin
from   termcolor import colored, cprint
from   jinja2    import FileSystemLoader
from   jinja2.environment import Environment
from   PIL       import Image # PIL using Pillow (PIL fork)
from   config    import configs as cfg

from utils.parser    import infodict, marked, md5
from utils.minifier  import can_minify, auto_minify
from utils.file      import *
from utils.color     import hex_to_rgb, rgb_to_hex
from core.image      import *

from core.index      import load_and_save

if os.name == 'nt':
    os.system("@chcp 65001")

# Shorthand alias
def log(*args,color=None,back=None,attrs=None,**kws):
    cprint(' '.join([str(x) for x in args]),color,back,attrs=attrs,**kws)
    #print(*[remove_unicode(str(x)) for x in args],**kws)
pjoin = os.path.join
Photo_Sort_Methods = {
    'filename': lambda photos: sorted(photos,key=lambda x: (x.path or '')),
    'title'   : lambda photos: sorted(photos,key=lambda x: (x.title or '')),
    'time'    : lambda photos: sorted(photos,key=lambda x: (x.datetime or '')),
    'shuffle' : lambda photos: random.sample(photos, len(photos)),
    'custom'  : lambda photos: sorted(photos,key=lambda x: (x.index or -1))
}
Photo_Title_Splite_Placeholders = [
    'title',
    'des',
    'photographer',
    'location'
]

if not os.path.exists(cfg.out_dir):
    os.mkdir(cfg.out_dir)

def gen():
    log('*** Generator Start ***', color='cyan')

    log('- Copying static files...', color='cyan')
    copy_static()
    log('- Copying completed', color='cyan')

    log('- Generating Structure tree...', color='cyan')
    generate_and_save(True)
    #struct_tree = generate_struct_tree()
    log('- Generating completed', color='cyan')

    #json_path = pjoin(cfg.out_dir,cfg.static_dir,cfg.sturct_filename)
    #log('- Saving struct json file...', color='cyan')
    #save_json(json_path ,struct_tree,'var full_data = ')
    #log('- Saving completed', color='cyan')

    log('- Rendering template file...', color='cyan')
    render_index()
    log('- Rendering completed', color='cyan')

    log('*** Task Completed ***', color='cyan')


def copy_static():
    if not os.path.exists(cfg.src_dir):
        os.mkdir(cfg.src_dir)
    copydir(pjoin(cfg.src_dir,cfg.static_dir),pjoin(cfg.out_dir,cfg.static_dir),cfg.minify)
    copydir(pjoin(cfg.src_dir,cfg.themes_dir,cfg.theme,cfg.static_dir),pjoin(cfg.out_dir,cfg.static_dir),cfg.minify)

def render_index():
    cfg.gentime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    index_path = pjoin(cfg.out_dir,'index.html')
    render(index_path,cfg=cfg)

def generate_and_save(old=False):
    if old:
        struct_tree = generate_struct_tree()
        json_path = pjoin(cfg.out_dir,cfg.static_dir,cfg.sturct_filename)
        save_json(json_path ,struct_tree,'var full_data = ')
    else:
        load_and_save(cfg.img_dir, pjoin(cfg.out_dir,cfg.static_dir))


def generate_struct_tree():
    time_start = datetime.datetime.now()

    img_src_dir = cfg.img_dir
    img_out_dir = os.path.join(cfg.out_dir,cfg.static_dir,cfg.img_dir)

    if not os.path.exists(os.path.join(cfg.out_dir,cfg.static_dir)):
        os.mkdir(os.path.join(cfg.out_dir,cfg.static_dir))
    if not os.path.exists(img_out_dir):
        os.mkdir(img_out_dir)

    src_file_type = cfg.src_file_type

    root = infodict()
    root.update_json(os.path.join(img_src_dir,'_site.json'))
    root.about = marked(os.path.join(img_src_dir,'about.md'))
    root.albums = []

    log()
    album_id = 0
    for album_name in os.listdir(img_src_dir):
        album_path = pjoin(img_src_dir,album_name)
        album_out_path = pjoin(img_out_dir,album_name)
        album_href_path = pjoin(cfg.static_dir,cfg.img_dir,album_name).replace('\\','/')

        # Skip if it's not a dir
        if not os.path.isdir(album_path):
            continue

        if not os.path.exists(album_out_path):
            os.mkdir(album_out_path)

        album = infodict(
            id = album_id,
            name = album_name,
            photographer = root.default_photographer,
            cover = cfg.default_cover_filename+'.'+src_file_type,
            gallery_mode = cfg.gallery_mode,

            href_path = album_href_path,
            display_info = cfg.display_info,
            use_filename_as_default_title = cfg.use_filename_as_default_title,
            photo_orderby = cfg.photo_orderby,
            photo_order_descending = cfg.photo_order_descending
        )
        album.update_json(pjoin(album_path,'_album.json'))

        log('  ', end='')
        log('  ', album.name, '  ', color='grey', back='on_yellow')

        album.photos = []
        photo_id = 0

        # Search for photos
        for photo_path in glob.glob(pjoin(album_path,'*.'+src_file_type)):
            photo_filename = os.path.basename(photo_path)
            photo_filename_without_ext = clear_ext(photo_filename)
            photo_md5 =  md5(photo_path)
            # Generate output filename
            if cfg.rename_photo_by_md5:
                photo_out_filename = photo_md5 + '.' + src_file_type
            else:
                photo_out_filename = photo_filename
            photo_out_path = pjoin(album_out_path,photo_out_filename)
            #photo_href_path = photo_out_filename
            photo_href_path = pjoin(cfg.static_dir,cfg.img_dir,album_name,photo_out_filename).replace('\\','/')

            photo_instance = Image.open(photo_path)

            photo = infodict(id = photo_id, md5 = photo_md5)
            # Update basic photo infos
            photo.update(photo_info(photo_instance))
            # Calc average color
            if cfg.calc_image_average_color:
                photo.color = rgb_to_hex(color_average(photo_instance, cfg.calc_image_samples))
            # Update info from the same-name json file if it exists
            photo.update_json(change_ext(photo_path,'json'))
            # Update info from the image's EXIF tags
            if cfg.extract_exif:
                photo.update(get_exif(photo_path))

            photo.path = photo_href_path
            # Use filename as title, But not the filename startswith '_'
            if not photo.title and album.use_filename_as_default_title and not photo_filename.startswith(cfg.filename_title_ignore_start):
                photo.title = photo_filename_without_ext
            # If title contains '$', separate into
            # title & des & photographer & location
            if photo.title and cfg.photo_title_spliter in photo.title:
                temp = photo.title.split(cfg.photo_title_spliter)
                for i in range(len(temp)):
                    photo[Photo_Title_Splite_Placeholders[i]] = temp[i]
            # Get index from title
            if photo.title and cfg.photo_title_index_spliter in photo.title:
                temp = photo.title.split(cfg.photo_title_index_spliter)
                if photo.index == None:
                    photo.index = float(temp[0])
                photo.title = temp[1]

            # Set default photographer
            #  if not photo.photographer and album.photographer:
            #      photo.photographer = album.photographer

            # Get photographer link by searching album and root configures
            #  if album.photographer_links and isinstance(album.photographer_links,dict) \
            #   and photo.photographer in album.photographer_links.keys():
            #     photo.photographer_link = album.photographer_links[photo.photographer]
            #  if root.photographer_links and isinstance(root.photographer_links,dict) \
            #   and photo.photographer in root.photographer_links.keys():
            #     photo.photographer_link = root.photographer_links[photo.photographer]
            # if configed not to display exposure and aperture, delete them

            if not cfg.exif_exposure:
                del(photo.aperture)
                del(photo.exposure)

            log('  ' + (photo.title or photo_filename_without_ext) + '  ', color='cyan', end='')

            # Lazy copy
            if cfg.lazy_copy and os.path.exists(photo_out_path):
                log('Skip', end='')
            # Resize and Save
            elif cfg.photo_resize:
                log('Resizing', end='')
                rim = image_resize(photo_instance, cfg.photo_resize_horizontal_max_size, cfg.photo_resize_vertical_max_size)
                rim.save(photo_out_path)
            # Just copy
            else:
                log('Copying', end='')
                shutil.copy2(photo_path,photo_out_path)

            # Check wather it's cover
            if (album.cover and album.cover.lower() == photo_filename.lower()):
                album.cover = photo_href_path
                album.color = photo.color

            log()
            album.photos.append(photo)
            photo_id += 1

        # delete the images which been deleted in source folder
        #if cfg.delete_nonsrc_images:
        #    srcs = photo_names
        #    outs = [os.path.basename(x).lower() for x in glob.glob(pjoin(album_out_path,'*.'+src_file_type))]
        #    for o in outs:
        #        if not o in srcs:
        #            log('  [!]Removing', o, color='red')
        #            os.remove(pjoin(album_out_path,o))

        if album.photos:
            if not album.cover:
                # Random choice a photo as cover
                choiced_cover = (random.choice(album.photos))
                album.cover = choiced_cover.path
                album.color = choiced_cover.color
            # Photo orderby (can be override in album json file)
            if album.photo_orderby:
                log('  [', album.photo_orderby, ']', color='green')
                if album.photo_orderby in Photo_Sort_Methods.keys():
                    album.photos = Photo_Sort_Methods[album.photo_orderby](album.photos)
                else:
                    log('  !Warning: invaild photo_orderby', album.photo_orderby, color="on_red")
            # Descending
            if album.photo_order_descending:
                album.photos = album.photos[::-1]
            album.amount = len(album.photos)
            log('  Amount:', album.amount, color='green')
            log()

            root.albums.append(album)
            album_id += 1

    time_end = datetime.datetime.now()
    time_spent = time_end - time_start
    log(' {} albums, {} photos, {}s cost '.format(len(root.albums),sum([len(a.photos) for a in root.albums]),time_spent.seconds),color='white',back='on_magenta')
    log()
    return root

def copydir(src,dst,minify=False):
    if not os.path.exists(dst):
        os.mkdir(dst)
    for itemname in os.listdir(src):
        src_path = pjoin(src,itemname)
        if os.path.isfile(src_path):
            dst_path = os.path.join(dst,itemname)
            # if the files modify time is the same, do not copy
            if not os.path.exists(dst_path) or os.path.getmtime(src_path) != os.path.getmtime(dst_path):
                if minify and not '.min.' in itemname and can_minify(src_path):
                    # minify
                    log('  Minifing ',itemname, color='yellow')
                    auto_minify(src_path,dst_path)
                    shutil.copystat(src_path,dst_path)
                else:
                    log('  Copying ',itemname)
                    # use 'copy2' to keep file metadate
                    shutil.copy2(src_path,dst_path)
        else:
            # isdir
            copydir(src_path, pjoin(dst,itemname), minify)

def render(dst,**kwargs):
    j2_env = Environment(loader=FileSystemLoader(cfg.src_dir))
    s = j2_env.get_template(cfg.themes_dir+'/'+cfg.theme+'/index.html').render(**kwargs)
    if cfg.minify:
        s = htmlmin.minify(s, remove_comments=False, remove_empty_space=True)

    # save file
    with codecs.open(dst, 'w', 'utf-8') as f:
        f.write(s)

# === Utils === #


def remove_unicode(string):
    return ''.join([i if ord(i) < 128 else '?' for i in string])
    #return string.encode('ascii','ignore').decode('utf-8')

def clear_complied():
    path = cfg.out_dir
    if input('Deleting ' + path + ', are you sure? [y/n]') == 'y':
        clear_directory(path)

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
