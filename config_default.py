#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Default configurations.
'''

configs = dict(
    # The static files(css/js) path,
    # you can change them into CDNs
    # for example (using CDNjs.com):
    #static_files_path = dict(
    #    jquery_js = 'https://cdnjs.cloudflare.com/ajax/libs/jquery/3.1.0/jquery.min.js',
    #    vue_js = 'https://cdnjs.cloudflare.com/ajax/libs/vue/1.0.26/vue.min.js',
    #    material_icons = 'https://fonts.googleapis.com/icon?family=Material+Icons'
    #),
    static_files_path = dict(
        favicon = '/static/favicon.ico',
        jquery_js = '/static/jquery-3.1.0.min.js',
        vue_js = '/static/vue.min.js',
        material_icons = '/static/material-icons.css'
    ),

    # The lanuages display in webpage
    # for example (Chinese):
    #lanuages = dict(
    #    photographer = '拍摄者',
    #    location = '地点',
    #    albums = '相册',
    #    photos = '张照片',
    #    comments = '条留言'
    #)
    lanuages = dict(
        photographer = 'photographer',
        location = 'location',
        albums = 'albums',
        photos = ' photos',
        comments = ' comments'
    ),

    src_dir = 'src',
    out_dir = 'out',

    static_dir = 'static',
    img_dir = 'img',
    sturct_filename = 'struct.json',
    src_file_type = 'jpg',

    lazy_copy = True,
    photo_resize = True,
    photo_resize_horizontal_max_size = (3000,0),
    photo_resize_vertical_max_size = (0,3000),
    photo_resize_keep_exif = False,

    # If there is not title infomation in JSON file or EXIF tags,
    # use the file name as the title of the photo
    use_filename_as_default_title = True,

    # The order of gallery photos,
    # the value can be one of ['filename','title','time','shuffle','custom']
    # for 'custom' option: you should set 'index' value in photo's json file
    photo_orderby = 'filename',

    # False:  Ascending
    # True: Descending
    photo_order_descending = False,

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
    display_info = True,

    # Gallery photos display mode
    # 0 for horizontal mode
    # 1 for vertical mode
    gallery_mode = 0,
)
