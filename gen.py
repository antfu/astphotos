#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
import glob
import codecs
import random
import datetime
import configparser
import exifread
import shutil
import hashlib
import jinja2
from   termcolor import colored, cprint
from   jinja2    import FileSystemLoader
from   jinja2.environment import Environment
from   PIL       import Image # PIL using Pillow (PIL fork)
from   config    import configs as cfg

class infodict(dict):
    def update_json(self,jsonpath):
        if os.path.exists(jsonpath):
            self.update(open_json(jsonpath))

    def __setattr__(self,key,value):
        self[key]=value

    def __getattr__(self,key):
        return self.get(key,None)

    def __delattr__(self,key):
        if key in self.keys():
            del(self[key])

# Shorthand alias
def log(*args,color=None,back=None,attrs=None,**kws):
    cprint(' '.join([str(x) for x in args]),color,back,attrs=attrs,**kws)
    #print(*[remove_unicode(str(x)) for x in args],**kws)
pjoin = os.path.join

if not os.path.exists(cfg.out_dir):
    os.mkdir(cfg.out_dir)

def run():
    log('*** Generator Start ***', color='cyan')

    log('- Copying static files...', color='cyan')
    copy_static()
    log('- Copying completed', color='cyan')

    log('- Generating Structure tree...', color='cyan')
    struct_tree = generate_struct_tree()
    log('- Generating completed', color='cyan')

    json_path = pjoin(cfg.out_dir,cfg.static_dir,cfg.sturct_filename)
    log('- Saving struct json file...', color='cyan')
    save_json(json_path ,struct_tree,'var full_data = ')
    log('- Saving completed', color='cyan')

    log('- Rendering template file...', color='cyan')
    render_index()
    log('- Rendering completed', color='cyan')

    log('*** Task Completed ***', color='cyan')


def copy_static():
    copydir(pjoin(cfg.src_dir,cfg.static_dir),pjoin(cfg.out_dir,cfg.static_dir))
    copydir(pjoin(cfg.src_dir,cfg.themes_dir,cfg.theme,cfg.static_dir),pjoin(cfg.out_dir,cfg.static_dir))

def render_index():
    cfg.gentime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    render(pjoin(cfg.out_dir,'index.html'),cfg=cfg)

def generate_and_save():
    struct_tree = generate_struct_tree()
    json_path = pjoin(cfg.out_dir,cfg.static_dir,cfg.sturct_filename)
    save_json(json_path ,struct_tree,'var full_data = ')

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
    root.albums = []

    log()
    album_id = 0
    for album_name in os.listdir(img_src_dir):
        album_path = pjoin(img_src_dir,album_name)
        album_out_path = pjoin(img_out_dir,album_name)

        # Skip if it's not a dir
        if not os.path.isdir(album_path):
            continue

        if not os.path.exists(album_out_path):
            os.mkdir(album_out_path)

        album = infodict()
        album.id = album_id
        album.display_info = cfg.display_info
        album.gallery_mode = cfg.gallery_mode
        album.update_json(pjoin(album_path,'_album.json'))
        if not album.name:
            album.name = album_name
        if album.photographer == None and root.default_photographer:
            album.photographer = root.default_photographer

        log('  ', end='')
        log('  ', album.name, '  ', color='grey', back='on_yellow')

        album.photos = []
        photo_id = 0

        photo_names = []
        # Search for photos
        for photo_path in glob.glob(pjoin(album_path,'*.'+src_file_type)):
            photo_filename = os.path.basename(photo_path)

            # Generate output filename
            if cfg.rename_photo_by_md5:
                photo_out_filename = md5(photo_path) + '.' + src_file_type
            else:
                photo_out_filename = photo_filename
            photo_out_path = pjoin(album_out_path,photo_out_filename)
            photo_href_path = pjoin(cfg.static_dir,cfg.img_dir,album_name,photo_out_filename).replace('\\','/')

            photo_instance = Image.open(photo_path)

            photo = infodict()
            photo.id = photo_id
            # Update basic photo infos
            photo.update(get_photo_info(photo_instance))
            # Update info from the image's EXIF tags
            if cfg.extract_exif:
                photo.update(get_exif(photo_path))
            # Update info from the same-name json file if it exists
            photo.update_json(change_ext(photo_path,'json'))
            photo.path = photo_href_path
            # Use filename as title
            if (album.use_filename_as_default_title or cfg.use_filename_as_default_title) and not photo.title:
                name = clear_ext(photo_filename)
                # But not the filename startswith '_'
                if not name.startswith(cfg.filename_title_ignore_start):
                    photo.title = clear_ext(photo_filename)
            # If title contains '$', separate into
            # title & des & photographer & location
            if photo.title and cfg.photo_title_spliter in photo.title:
                temp = photo.title.split(cfg.photo_title_spliter)
                if len(temp) > 0:
                    photo.title = temp[0]
                if len(temp) > 1 and not photo.des:
                    photo.des = temp[1]
                if len(temp) > 2 and not photo.photographer:
                    photo.photographer = temp[2]
                if len(temp) > 3 and not photo.location:
                    photo.location = temp[3]
            # Get index from title
            if photo.title and cfg.photo_title_index_spliter in photo.title:
                temp = photo.title.split(cfg.photo_title_index_spliter)
                if photo.index == None:
                    photo.index = float(temp[0])
                photo.title = temp[1]
            # Set default photographer
            if not photo.photographer and album.photographer:
                photo.photographer = album.photographer
            # Get photographer link by searching album and root configures
            if album.photographer_links and isinstance(album.photographer_links,dict) \
             and photo.photographer in album.photographer_links.keys():
               photo.photographer_link = album.photographer_links[photo.photographer]
            if root.photographer_links and isinstance(root.photographer_links,dict) \
             and photo.photographer in root.photographer_links.keys():
               photo.photographer_link = root.photographer_links[photo.photographer]
            # if configed not to display exposure and aperture, delete them
            if not cfg.exif_exposure:
                del(photo.aperture)
                del(photo.exposure)

            log('  ' + (photo.title or clear_ext(photo_filename)) + '... ', end='')

            # Lazy copy
            if cfg.lazy_copy and os.path.exists(photo_out_path):
                log('Skip', end='')
            else:
                # Resize and Save
                if cfg.photo_resize:
                    log('Resizing', end='')
                    rim = im_resize(photo_instance)
                    rim.save(photo_out_path)
                # Just copy
                else:
                    log('Copying', end='')
                    shutil.copy(photo_path,photo_out_path)

            # Check wather it's cover
            if (album.cover and album.cover.lower() == photo_filename.lower()) \
              or (photo_filename.lower() == (cfg.default_cover_filename+'.'+src_file_type)):
                album.cover = photo_href_path
                album.color = photo.color

            log()
            album.photos.append(photo)
            photo_names.append(photo_out_filename.lower())
            photo_id += 1

        if cfg.delete_nonsrc_images:
            srcs = photo_names
            outs = [os.path.basename(x).lower() for x in glob.glob(pjoin(album_out_path,'*.'+src_file_type))]
            for o in outs:
                if not o in srcs:
                    log('  [!]Removing', o, color='red')
                    os.remove(pjoin(album_out_path,o))

        if album.photos:
            if not album.cover:
                # Random choice a photo as cover
                choiced_cover = (random.choice(album.photos))
                album.cover = choiced_cover.path
                album.color = choiced_cover.color
            # Photo orderby (can be override in album json file)
            photo_orderby = album.photo_orderby or cfg.photo_orderby
            photo_order_descending = album.photo_order_descending or cfg.photo_order_descending
            if photo_orderby:
                log('  [', photo_orderby, ']', color='green')
                if   photo_orderby == 'filename':
                    album.photos = sorted(album.photos,key=lambda x: (x.path or ''))
                elif photo_orderby == 'title':
                    album.photos = sorted(album.photos,key=lambda x: (x.title or ''))
                elif photo_orderby == 'time':
                    album.photos = sorted(album.photos,key=lambda x: (x.datetime or ''))
                elif photo_orderby == 'shuffle':
                    random.shuffle(album.photos)
                elif photo_orderby == 'custom':
                    album.photos = sorted(album.photos,key=lambda x: (x.index or -1))
                else:
                    log('  !Warning: invaild photo_orderby', photo_orderby, color="on_red")
            # Descending
            if photo_order_descending:
                album.photos = album.photos[::-1]
            album.amount = len(album.photos)
            root.albums.append(album)
            #log('  Cover :', os.path.basename(album.cover), color='green')
            log('  Amount:', album.amount, color='green')
            log()
            album_id += 1

    time_end = datetime.datetime.now()
    time_spent = time_end - time_start
    log(' {} albums, {} photos, {}s cost '.format(len(root.albums),sum([len(a.photos) for a in root.albums]),time_spent.seconds),color='white',back='on_magenta')
    log()
    return root

def codecs_open(filename,open_type,encode=None):
    return codecs.open(filename,open_type,encode)

def copydir(src,dst):
    if not os.path.exists(dst):
        os.mkdir(dst)
    for f in glob.glob(os.path.join(src,'*.*')):
        filename = os.path.basename(f)
        dst_path = os.path.join(dst,filename)
        # if the files modify time is the same, do not copy
        if not os.path.exists(dst_path) or os.path.getmtime(f) != os.path.getmtime(dst_path):
            log('  Copying',filename)
            # use 'copy2' to keep file metadate
            shutil.copy2(f,dst_path)

def render(dst,**kwargs):
    j2_env = Environment(loader=FileSystemLoader(cfg.src_dir))
    s = j2_env.get_template(cfg.themes_dir+'/'+cfg.theme+'/index.html').render(**kwargs)
    # save file
    f = codecs_open(dst,'w','utf-8')
    f.write(s)
    f.close()

def im_resize(img):
    size = img.size
    # deceide the photo is vertical or horizontal and choose the target size
    if size[0] >= size[1]:
        t_size = cfg.photo_resize_horizontal_max_size
    else:
        t_size = cfg.photo_resize_vertical_max_size
    # if there is no size limit
    if not t_size:
        return img
    if t_size[0] == 0 and t_size[1] == 0:
        return img
    # if the photo size is smaller than target size
    if t_size[0] > size[0] and t_size[1] > size[1]:
        return img

    # target width and height (keep the aspect ratio)
    t_width = size[0]
    t_height = size[1]
    if t_size[0] != 0 and t_width > t_size[0]:
        old_width = t_width
        t_width = t_size[0]
        t_height = t_height * t_width / old_width
    if t_size[1] != 0 and t_height > t_size[1]:
        old_height = t_height
        t_height = t_size[1]
        t_width = t_width * t_height / old_height

    # resize
    resized_img = img.resize((int(t_width),int(t_height)))
    return resized_img


# === Utils === #

def get_tags(img_path,details=False):
    # Open image file for reading (binary mode)
    f = codecs_open(img_path, 'rb')
    # Return Exif tags
    tags = exifread.process_file(f, details=details)
    f.close()
    return tags

def get_exif(img_path):
    result = infodict()
    tags = get_tags(img_path)

    # Aperture
    aperture = tags.get('EXIF FNumber',None)
    if aperture:
        aperture = aperture.printable
        if '/' in aperture:
            temp = aperture.split('/')
            aperture = str(float(temp[0]) / float(temp[1]))
        result.aperture = aperture + 'f'
    # Exposure Time
    exposure = tags.get('EXIF ExposureTime',None)
    if exposure:
        exposure = exposure.printable
        if not '/' in exposure:
            exposure += 's'
        result.exposure = exposure
    # Tooken DateTime
    dt = tags.get('EXIF DateTimeOriginal',None)
    if dt:
        result.datetime = datetime.datetime.strptime(dt.printable,'%Y:%m:%d %H:%M:%S').isoformat()

    title = tags.get('Image ImageDescription',None)
    if title:
        result.title = title.printable

    return result

def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def get_photo_info(im):
    result = infodict()
    # PIL, Get image size and color
    result.width = im.size[0]
    result.height = im.size[1]
    if result.width >= result.height:
        # Horizontal
        result.type = 0
    else:
        # Vertical
        result.type = 1

    # Calc average color
    if cfg.calc_image_average_color:
        result.color = rgb_to_hex(get_average_color(im))

    return result

def get_average_color(im, sample = 100):
    r,g,b = (0,0,0)
    w = im.size[0] - 1
    h = im.size[1] - 1
    for _ in range(sample):
        tr, tg, tb = im.getpixel((random.randint(0,w),random.randint(0,h)))
        r += tr
        g += tg
        b += tb
    return (int(r/sample),int(g/sample),int(b/sample))

def remove_unicode(string):
    return ''.join([i if ord(i) < 128 else '?' for i in string])
    #return string.encode('ascii','ignore').decode('utf-8')

def hex_to_rgb(value):
    value = value.lstrip('#')
    lv = len(value)
    return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))

def rgb_to_hex(rgb):
    return '#%02x%02x%02x' % rgb

def open_ini(filepath):
    ini_str = '[root]\n' + codecs_open(filepath,'r','utf-8').read()
    ini_fp = StringIO.StringIO(ini_str)
    config = ConfigParser.RawConfigParser()
    config.readfp(ini_fp)
    return config['root']

def open_json(filepath):
    f = codecs_open(filepath,'r','utf-8')
    s = f.read()
    f.close()
    return json.loads(s)

def save_json(filepath,obj,prefix):
    f = codecs_open(filepath, 'w', 'utf-8')
    t = json.dumps(obj)
    if prefix:
        t = prefix + t
    f.write(t)
    f.close()

def change_ext(filepath,ext):
    return '.'.join(filepath.split('.')[:-1]+[ext])

def clear_ext(filepath):
    return '.'.join(filepath.split('.')[:-1])


if __name__ == '__main__':
    #if input('Sure? [y/n]') == 'y':
    run()
