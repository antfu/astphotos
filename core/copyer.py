
from os         import mkdir
from os.path    import exists, join
from shutil     import copy2


def copy_all(data, dst_path):
    mkdir_if_not(dst_path)
    for album in data.albums:
        album_out_path = join(dst_path, album._src_folder_name)
    	copy_albums(album, album_out_path)

def copy_albums(data, dst_path)
    mkdir_if_not(dst_path)
    for photo in data.photos:
    	photo._out_name = photo.md5 + '.' + photo._ext
    	photo._out_path = join(dst_path, photo._out_name)
    	photo.path = join('static', album._src_folder_name, photo._out_name).replace('\\','/')
    	copy2(photo._src_path, photo._out_path)

def mkdir_if_not(dst_path):
    if not exists(dst_path):
        mkdir(dst_path)