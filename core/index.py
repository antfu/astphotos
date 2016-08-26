
from os.path    import exists, join
from loader     import load
from copyer     import copy_all

def generate(src_path, out_path, use_cache=True):
	data = load(src_path, use_cache)
	data.save(join(src_path,'_cache.json'))

	copy_all(data, out_path)

	data.remove_keys_startswith('_')
	data.save(join(out_path,cfg.sturct_filename,'var full_data= '))