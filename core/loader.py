from os           import listdir
from os.path      import join, basename, getmtime, exists, isdir
from random       import sample
from utils.parser import infodict, marked
from utils.color  import rgb_to_hex
from utils.file   import change_ext
from core.image   import photo_info, get_exif
from config       import configs as cfg

Photo_Sort_Methods = {
    'filename': lambda photos: sorted(photos,key=lambda x: (x._src_path or '')),
    'title'   : lambda photos: sorted(photos,key=lambda x: (x.title or '')),
    'time'    : lambda photos: sorted(photos,key=lambda x: (x.datetime or '')),
    'shuffle' : lambda photos: sample(photos, len(photos)),
    'custom'  : lambda photos: sorted(photos,key=lambda x: (x.index or -1))
}

def load(dir_path, use_cache=True):
    cached = None
    if use_cache:
        cached = infodict()
        cached.update_json(join(dir_path,'_cache.json'))

    root = infodict()
    root.update_json(join(dir_path,'_site.json'))
    root.about = marked(join(dir_path,'about.md'))
    root.albums = []

    for album_name in listdir(dir_path):
        album_path = join(dir_path,album_name)
        if not isdir(album_path):
            continue
        album_cache = None
        if cached:
            for a in cached.albums:
                if a._src_path == album_path:
                    album_cache = a
                    break
        root.albums.append(load_album(album_path),root_cache)

    return root

def load_album(album_path, cached=None):
    album = infodict()

    album.name = basename(album_path)
    album.photographer = root.default_photographer
    album.cover = cfg.default_cover_filename+'.'+cfg.src_file_type
    album.gallery_mode = cfg.gallery_mode

    album._src_folder_name = basename(album_path)
    album._src_path = album_path
    album._display_info = cfg.display_info
    album._orderby = cfg.photo_orderby
    album._order_desc = cfg.photo_order_descending

    album.update_json(pjoin(album_path,'_album.json'))
    album.photos = []

    for photo_path in listdir(album_path):
        if isdir(join(album_path,photo_path)) or not album_path.lower().endswith(cfg.src_file_type):
            continue

        photo_cache = None
        if cached:
            for c in cached.photos:
                if c._src_path == photo_path:
                    photo_cache = c
                    break
        album.photos.append(load_photo(photo_path),photo_cache)

    if not album.cover:
        # Random choice a photo as cover
        choiced_cover = (random.choice(album.photos))
        album.cover = choiced_cover.path
        album.color = choiced_cover.color
    # Photo orderby (can be override in album json file)
    if album._orderby:
        if album._orderby in Photo_Sort_Methods.keys():
            album.photos = Photo_Sort_Methods[album._orderby](album.photos)
    # Descending
    if album._order_desc:
        album.photos = album.photos[::-1]
    album.amount = len(album.photos)

    return album

def load_photo(photo_path, cached=None):
    filename = basename(photo_path)

    photo = infodict()

    photo._src_path = photo_path
    photo._modify_time = getmtime(photo._src_path)
    meta_path = change_ext(photo_path,'json')
    if exists(meta_path):
        photo._meta_path = meta_path
        photo._meta_modify_time = getmtime(photo._meta_path)

    if cached and cached._modify_time == photo._modify_time \
              and cached._meta_modify_time == photo._meta_modify_time:
        return cached

    photo.md5 = md5(photo_path)
    phoot._ext = filename.split('.')[-1]
    
    photo_instance = Image.open(photo_path)

    # Update basic photo infos
    photo.update(photo_info(photo_instance))
    # Calc average color
    photo.color = rgb_to_hex(color_average(photo_instance, cfg.calc_image_samples))
    # Update info from the same-name json file if it exists
    photo.update_json()
    # Update info from the image's EXIF tags
    if cfg.extract_exif:
        photo.update(get_exif(photo_path))

    photo.path = photo_href_path
    # Use filename as title, But not the filename startswith '_'
    if not photo.title and not filename.startswith(cfg.filename_title_ignore_start):
        photo.title = filename.split('.')[:-1]
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

    return photo
