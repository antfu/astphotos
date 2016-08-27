import os
from termcolor          import colored, cprint

if os.name == 'nt':
    os.system("@chcp 65001")

def log(*args,color=None,back=None,attrs=None,**kws):
    cprint(' '.join([str(x) for x in args]),color,back,attrs=attrs,**kws)
    #print(*[remove_unicode(str(x)) for x in args],**kws)
