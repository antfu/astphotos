
from os.path     import exists, join
from core.loader import load
from core.copyer import copy_images
from config      import configs as cfg


def load_and_save(src_path, out_path, use_cache=True):
	data = load(src_path, use_cache)
	data.save(join(src_path,'_cache.json'))

	copy_images(data, join(out_path, cfg.img_dir))

	data.remove_keys_startswith('_')
	data.save(join(out_path,cfg.sturct_filename),'var full_data= ')
