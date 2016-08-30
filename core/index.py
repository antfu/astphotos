
from os.path     import exists, join
from core.loader import load
from core.copyer import copy_images
from utils.file  import mkdir_if_not
from config      import configs as cfg


def load_and_save(src_path, out_path=None, use_cache=True):
    mkdir_if_not(out_path)

    data = load(src_path, use_cache)
    data.save(join(src_path,'_cache.json'))

    copy_images(data, join(out_path, cfg.img_dir))

    data.remove_keys_startswith('_')
    data.save(join(out_path,cfg.sturct_filename),'var full_data= ')
