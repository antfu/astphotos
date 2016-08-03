import os
import sys
import json
import glob
import codecs
import random
import datetime
import exifread
import shutil
import jinja2
from   PIL import Image # PIL using Pillow (PIL fork)

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


configs = infodict(
    src_dir = 'src',
    out_dir = 'out',

    static_dir = 'static',
    img_dir = 'img',
    sturct_filename = 'struct.json',
    src_file_type = 'jpg',

    use_out = False,
    lazy_copy = True,
    photo_resize = True,
    photo_resize_horizontal_max_size = (3000,0),
    photo_resize_vertical_max_size = (0,3000),

    default_photographer = 'anthony.f',

    # If there is not title infomation in JSON file or EXIF tags,
    # use the file name as the title of the photo
    use_filename_as_default_title = True,

    # TODO
    # The order of gallery photos,
    # the value can be one of ['name','date','shuffle']
    photo_orderby = 'name',

    # TODO
    # True:  Ascending
    # False: Descending
    photo_order_ascending = True,

    # Extract the photo infomation from the EXIF tags
    # Such as Aperture, ExposureTime, TookenDateTime, etc.
    # For title and desc you should modify the "ImageDescription",
    # in format [title|desc]
    extract_exif = True,

    # Display exposure and aperture info
    exif_exposure = True,

    # TODO
    # Extract the photo's location info from EXIF
    # (default: False)
    exif_location = False,

    # TODO
    # Extract the photo's title and desc from XPTags (Windows only)
    # In Windows, you can simpliy edit it in the photo file's Properties
    exif_windows_xptags = False,

    # Read and calc the average color of the photo,
    # this feature can bring a better user-experience in website,
    # but may cost more time while generating structure tree
    # (default: True)
    calc_image_average_color = False,

    # Display the info in gallery view, such as title, desc, etc.
    # Can be overrided in "_album.json" and "[photo_name].json"
    display_info = True
)

# Shorthand alias
log = print
pjoin = os.path.join
cfg = configs

def run():
    log('*** Generator Start ***')

    log('- Copying static files...')
    copy_static()
    log('- Copying completed')

    log('- Generating Structure tree...')
    struct_tree = generate_struct_tree()
    log('- Generating completed')

    json_path = pjoin(cfg.out_dir,cfg.static_dir,cfg.sturct_filename)
    log('- Saving struct json file...')
    save_json(json_path ,struct_tree)
    log('- Saving completed')

    log('- Rendering template file...')
    render_index()
    log('- Rendering completed')

    log('*** Task Completed ***')


def copy_static():
    copydir(pjoin(cfg.src_dir,cfg.static_dir),pjoin(cfg.out_dir,cfg.static_dir))

def render_index():
    render(pjoin(cfg.src_dir,'index.html'),pjoin(cfg.out_dir,'index.html'))

def generate_and_save():
    struct_tree = generate_struct_tree()
    json_path = pjoin(cfg.out_dir,cfg.static_dir,cfg.sturct_filename)
    save_json(json_path ,struct_tree)

def generate_struct_tree():
    img_src_dir = os.path.join(cfg.src_dir,cfg.img_dir)
    img_out_dir = os.path.join(cfg.out_dir,cfg.static_dir,cfg.img_dir)

    if not os.path.exists(os.path.join(cfg.out_dir,cfg.static_dir)):
        os.mkdir(os.path.join(cfg.out_dir,cfg.static_dir))
    if not os.path.exists(img_out_dir):
        os.mkdir(img_out_dir)

    src_file_type = cfg.src_file_type

    struct_tree = infodict()
    struct_tree.update_json(os.path.join(img_src_dir,'_site.json'))
    struct_tree.albums = []

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
        album.update_json(pjoin(album_path,'_album.json'))
        if not album.name:
            album.name = album_name
        if not album.photographer and cfg.default_photographer:
            album.photographer = cfg.default_photographer

        log('  Ablum:', remove_unicode(album.name))

        album.photos = []
        photo_id = 0
        for photo_path in glob.glob(pjoin(album_path,'*.'+src_file_type)):
            photo_filename = os.path.basename(photo_path)
            photo_out_path = pjoin(album_out_path,photo_filename)
            photo_href_path = pjoin(cfg.static_dir,cfg.img_dir,album_name,photo_filename)

            log('    ', remove_unicode(photo_filename), end='')

            photo = infodict()
            photo.id = photo_id
            # Update info from the image's EXIF tags
            if cfg.extract_exif:
                photo.update(get_exif(photo_path))
            # Update info from the same-name json file if it exists
            photo.update_json(change_ext(photo_path,'json'))
            photo.path = photo_href_path.replace('\\','/')
            if cfg.use_filename_as_default_title and not photo.title:
                name = clear_ext(os.path.basename(photo_path))
                if not name.startswith('_'):
                    photo.title = clear_ext(os.path.basename(photo_path))
            if not photo.photographer and cfg.default_photographer:
                photo.photographer = cfg.default_photographer
            if not cfg.exif_exposure:
                del(photo.aperture)
                del(photo.exposure)

            # Lazy copy
            if cfg.lazy_copy and os.path.exists(photo_out_path):
                log('  [Skip]', end='')
            else:
                # Resize and Save
                if cfg.photo_resize:
                    log('  [Resizing]', end='')
                    im = Image.open(photo_path)
                    rim = im_resize(im)
                    rim.save(photo_out_path)
                    im.close()
                # Just copy
                else:
                    log('  [Copying]', end='')
                    shutil.copy(photo_path,photo_out_path)

            log()
            album.photos.append(photo)
            photo_id += 1

        log('  ' + '-' * 20)
        album.cover = album.cover or ('_cover.'+src_file_type)
        if not os.path.exists(pjoin(album_out_path,album.cover)):
            del(album.cover)
            log('  !Warning: cover [',album.cover,'] not exist.')

        if album.cover:
            album.cover = pjoin(cfg.static_dir,cfg.img_dir,album_name,album.cover).replace('\\','/')
            # Take the color of cover if need
            if cfg.calc_image_average_color and album.photos:
                for p in album.photos:
                    if p.path == album.cover:
                        album.color = album.color
                        break

        if album.photos:
            if not album.cover:
                # Random choice a photo as cover
                choiced_cover = (random.choice(album.photos))
                album.cover = choiced_cover.path
                album.color = choiced_cover.color
            album.amount = len(album.photos)
            struct_tree.albums.append(album)
            log('  Cover :',os.path.basename(album.cover))
            log('  Amount:',album.amount)
            log()
            album_id += 1

    return struct_tree

def codecs_open(filename,open_type,encode=None):
    return codecs.open(
        filename.encode(sys.getfilesystemencoding()),
        open_type,
        encode)

def copydir(src,dst):
    if not os.path.exists(dst):
        os.mkdir(dst)
    for f in glob.glob(os.path.join(src,'*.*')):
        filename = os.path.basename(f)
        dst_path = os.path.join(dst,filename)
        # if the files modify time is the same, do not copy
        if os.path.getmtime(f) != os.path.getmtime(dst_path):
            log('  Copying',filename)
            # use 'copy2' to keep file metadate
            shutil.copy2(f,dst_path)

def render(src,dst,**kwargs):
    # open file
    f = codecs_open(src,'r','utf-8')
    s = f.read()
    f.close()
    # render html file using jinja2
    j = jinja2.Template(s)
    s = j.render(**kwargs)
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

def get_tags(img_path):
    # Open image file for reading (binary mode)
    f = codecs_open(img_path, 'rb')
    # Return Exif tags
    tags = exifread.process_file(f, details=False)
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

    # PIL, Get image size and color
    im = Image.open(img_path)
    result.width = im.size[0]
    result.height = im.size[1]

    # Calc average color
    if cfg.calc_image_average_color:
        resize_width = 10
        resize_height = 10
        s_im = im.resize((resize_width,resize_height))
        r,g,b = (0,0,0)
        for x in range(resize_width):
            for y in range(resize_height):
                tr,tg,tb = s_im.getpixel((x,y))
                r += tr
                g += tg
                b += tb
        r /= resize_width * resize_height
        g /= resize_width * resize_height
        b /= resize_width * resize_height
        result.color = rgb_to_hex((int(r),int(g),int(b))).upper()

    im.close()

    title = tags.get('Image ImageDescription',None)
    if title:
        title = title.printable
        if '|' in title:
            temp = t.split('|')
            result.title = temp[0]
            result.des = temSp[1]
        else:
            result.title = title

    return result

def remove_unicode(string):
    return string.encode('ascii','ignore').decode('utf-8')

def hex_to_rgb(value):
    value = value.lstrip('#')
    lv = len(value)
    return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))

def rgb_to_hex(rgb):
    return '#%02x%02x%02x' % rgb


def open_json(filepath):
    f = codecs_open(filepath,'r','utf-8')
    s = f.read()
    f.close()
    return json.loads(s)

def save_json(filepath,obj):
    f = codecs_open(filepath, 'w', 'utf-8')
    f.write(json.dumps(obj))
    f.close()

def change_ext(filepath,ext):
    return '.'.join(filepath.split('.')[:-1]+[ext])

def clear_ext(filepath):
    return '.'.join(filepath.split('.')[:-1])


if __name__ == '__main__':
    #if input('Sure? [y/n]') == 'y':
    run()
