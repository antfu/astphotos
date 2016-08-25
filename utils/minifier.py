import codecs
import csscompressor
import jsmin
import htmlmin

def js_minify(src,dst):
    with codecs.open(src, 'r', 'utf-8') as src_file:
        minified = jsmin.jsmin(src_file.read())
        with codecs.open(dst, 'w', 'utf-8') as dst_file:
            dst_file.write(minified)

def css_minify(src,dst):
    with codecs.open(src, 'r', 'utf-8') as src_file:
        minified = csscompressor.compress(src_file.read())
        with codecs.open(dst, 'w', 'utf-8') as dst_file:
            dst_file.write(minified)
            
def html_minify(src,dst):
    with codecs.open(src, 'r', 'utf-8') as src_file:
        minified = htmlmin.minify(src_file.read(), remove_comments=True, remove_empty_space=True)
        with codecs.open(dst, 'w', 'utf-8') as dst_file:
            dst_file.write(minified)

minifiers = {
    'js'   : js_minify,
    'css'  : css_minify,
    'html' : html_minify
}

def can_minify(src):
	ext = src.split('.')[-1]
	return ext in minifiers.keys()

def auto_minify(src,dst):
	ext = src.split('.')[-1]
	if not can_minify(src):
		raise Exception('Minify for {} is not supported.'.format(ext))
	minifiers[ext](src,dst)