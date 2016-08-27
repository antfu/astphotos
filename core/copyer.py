
from os         import mkdir
from os.path    import exists, join, basename
from shutil     import copy2
from config     import configs as cfg
from core.image import image_resize, Image
from random     import choice

def copy_images(data, dst_path):
    mkdir_if_not(dst_path)
    for album in data.albums:
        album_out_path = join(dst_path, album._src_folder_name)
        copy_albums(album, album_out_path)

def copy_albums(album_data, dst_path):
    mkdir_if_not(dst_path)
    for photo in album_data.photos:
        photo._out_name = photo.md5 + '.' + photo._ext
        photo._out_path = join(dst_path, photo._out_name)
        photo.path = join('static', 'img', album_data._src_folder_name, photo._out_name).replace('\\','/')
        resize_and_copy(photo._src_path, photo._out_path)

        if album_data.cover == basename(photo._src_path) \
        or album_data._cover == basename(photo._src_path):
            album_data.cover = photo.path
            album_data.color = photo.color

    if not album_data.cover:
        # Random choice a photo as cover
        choiced_cover = choice(album_data.photos)
        album_data.cover = choiced_cover.path
        album_data.color = choiced_cover.color


def mkdir_if_not(dst_path):
    if not exists(dst_path):
        mkdir(dst_path)

def resize_and_copy(src_path, dst_path):
    # Lazy copy
    if cfg.lazy_copy and exists(dst_path):
        return
    # Resize and Save
    elif cfg.photo_resize:
        rim = image_resize(Image.open(src_path), cfg.photo_resize_horizontal_max_size, cfg.photo_resize_vertical_max_size)
        rim.save(dst_path)
    # Just copy
    else:
        shutil.copy2(photo_path,dst_path)
