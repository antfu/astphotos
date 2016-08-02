import os
import json
import glob
import codecs
import random
import datetime
import exifread
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
    src_dir = 'static/img',
    src_file_type = 'jpg',
    default_photographer = 'anthony.f',
    sturct_output_filename = 'struct.json',

    # If there is not title infomation in JSON file or EXIF tags,
    # use the file name as the title of the photo
    use_filename_as_default_title = False,

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
    calc_image_average_color = True,

    # Display the info in gallery view, such as title, desc, etc.
    # Can be overrided in "_album.json" and "[photo_name].json"
    display_info = True
)

log = print

def generate_struct_tree(save = True):
    src_dir = configs.src_dir
    src_file_type = configs.src_file_type

    log('Structure tree generator started at',src_dir)

    struct_tree = infodict()
    struct_tree.update_json(os.path.join(src_dir,'_site.json'))
    struct_tree.albums = []

    album_id = 0
    for album_path in os.listdir(src_dir):
        # Skip if it's not a dir
        if not os.path.isdir(os.path.join(src_dir,album_path)):
            continue

        album = infodict()
        album.id = album_id
        album.display_info = configs.display_info
        album.update_json(os.path.join(src_dir,album_path,'_album.json'))
        if not album.name:
            album.name = album_path
        if not album.photographer and configs.default_photographer:
            album.photographer = configs.default_photographer

        log('  Ablum:', album.name)

        album.photos = []
        photo_id = 0
        for photo_path in glob.glob(os.path.join(src_dir,album_path,'*.'+src_file_type)):
            log('    ', os.path.basename(photo_path))

            photo = infodict()
            photo.id = photo_id
            # Update info from the image's EXIF tags
            if configs.extract_exif:
                photo.update(get_exif(photo_path))
            # Update info from the same-name json file if it exists
            photo.update_json(change_ext(photo_path,'json'))
            photo.path = photo_path.replace('\\','/')
            if configs.use_filename_as_default_title and not photo.title:
                photo.title = clear_ext(os.path.basename(photo_path))
            if not photo.photographer and configs.default_photographer:
                photo.photographer = configs.default_photographer
            if not configs.exif_exposure:
                del(photo.aperture)
                del(photo.exposure)
            album.photos.append(photo)
            photo_id += 1

        if album.cover:
            album.cover = os.path.join(src_dir,album_path,album.cover).replace('\\','/')
            if album.photos:
                for p in album.photos:
                    if p.path == album.cover:
                        album.color = album.color
                        break

        if album.photos:
            if not album.cover:
                choiced_cover = (random.choice(album.photos))
                album.cover = choiced_cover.path
                album.color = choiced_cover.color
            album.amount = len(album.photos)
            struct_tree.albums.append(album)
            album_id += 1

    log()
    log('Generate finished')
    if save:
        json_path = os.path.join('static',configs.sturct_output_filename)
        log('Saving json file at', json_path)
        save_json(json_path ,struct_tree)

    log('=== Task finished ===')

# === Utils === #
def get_tags(img_path):
    # Open image file for reading (binary mode)
    f = open(img_path, 'rb')
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
        result.exposure = exposure.printable
    # Tooken DateTime
    dt = tags.get('EXIF DateTimeOriginal',None)
    if dt:
        result.datetime = datetime.datetime.strptime(dt.printable,'%Y:%m:%d %H:%M:%S').isoformat()

    # PIL, Get image size and color
    im = Image.open(img_path)
    result.width = im.size[0]
    result.height = im.size[1]

    # Calc average color
    if configs.calc_image_average_color:
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

def hex_to_rgb(value):
    value = value.lstrip('#')
    lv = len(value)
    return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))

def rgb_to_hex(rgb):
    return '#%02x%02x%02x' % rgb


def open_json(filepath):
    f = codecs.open(filepath,'r','utf-8')
    s = f.read()
    f.close()
    return json.loads(s)

def save_json(filepath,obj):
    f = codecs.open(filepath, 'w', 'utf-8')
    f.write(json.dumps(obj))
    f.close()

def change_ext(filepath,ext):
    return '.'.join(filepath.split('.')[:-1]+[ext])

def clear_ext(filepath):
    return '.'.join(filepath.split('.')[:-1])


if __name__ == '__main__':
    if input('Sure? [y/n]') == 'y':
        generate_struct_tree()
