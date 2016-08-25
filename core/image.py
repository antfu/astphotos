# -*- coding: utf-8 -*-

import exifread
import datetime
import random
import codecs
from   PIL           import Image # PIL using Pillow (PIL fork)
from   utils.parser  import infodict

def color_average(im, sample = 100):
    r,g,b = (0,0,0)
    w = im.size[0] - 1
    h = im.size[1] - 1
    for _ in range(sample):
        tr, tg, tb = im.getpixel((random.randint(0,w),random.randint(0,h)))
        r += tr
        g += tg
        b += tb
    return (int(r/sample),int(g/sample),int(b/sample))

def photo_info(im, average_sample = 100):
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
    return result

def image_resize(img, horizontal_size = None, vertical_size = None):
    if horizontal_size == None and vertical_size == None:
        horizontal_size = (2000,0)
    if vertical_size == None and horizontal_size != None:
        vertical_size = (horizontal_size[1],horizontal_size[0])
    if horizontal_size == None and vertical_size != None:
        horizontal_size = (vertical_size[1],vertical_size[0])

    size = img.size
    # deceide the photo is vertical or horizontal and choose the target size
    if size[0] >= size[1]:
        t_size = horizontal_size
    else:
        t_size = vertical_size
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

def get_tags(img_path,details=False):
    # Open image file for reading (binary mode)
    with codecs.open(img_path, 'rb') as f:
        # Return Exif tags
        tags = exifread.process_file(f, details=details)
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
