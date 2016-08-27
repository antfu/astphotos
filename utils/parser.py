
import os
import hashlib
import htmlmin
import codecs
from utils.file         import read_json, save_json, read_if_exists
from markdown           import markdown
from jinja2             import FileSystemLoader
from jinja2.environment import Environment

class infodict(dict):
    def __setattr__(self,key,value):
        self[key]=value

    def __getattr__(self,key):
        return self.get(key,None)

    def __delattr__(self,key):
        if key in self.keys():
            del(self[key])

    def update_json(self,jsonpath):
        if os.path.exists(jsonpath):
            self.update(read_json(jsonpath))

    def remove_keys_startswith(self, starts='_'):
        for k,v in self.items():
            if k.startswith(starts):
                del(self[k])
            elif isinstance(v,infodict):
                v.remove_keys_startswith(starts)

    def save(self, path, prefix=None):
        save_json(path, self, prefix)

def template_render(dst,cfg,**kwargs):
    j2_env = Environment(loader=FileSystemLoader(cfg.src_dir))
    s = j2_env.get_template(cfg.themes_dir+'/'+cfg.theme+'/index.html').render(cfg=cfg,**kwargs)
    if cfg.minify:
        s = htmlmin.minify(s, remove_comments=False, remove_empty_space=True)

    # save file
    with codecs.open(dst, 'w', 'utf-8') as f:
        f.write(s)

def marked(path):
    raw = read_if_exists(path)
    if raw:
        return markdown(raw)
    return None

def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def md5_text(text):
    hash_md5 = hashlib.md5()
    hash_md5.update(str(text).encode())
    return hash_md5.hexdigest()
