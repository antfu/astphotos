#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-

import sys
import tornado.web
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.websocket

from   os.path          import join, isdir
from   gen              import cfg
from   core.loader      import load
from   json             import dumps, loads
from   core.edit        import JsonEditor
from   utils.file       import change_ext
from   codecs           import open

class index_handler(tornado.web.RequestHandler):
    def get(self):
        self.render('index.html')

class data_handler(tornado.web.RequestHandler):
    def get(self):
        self.set_header('Content-Type', 'application/json')
        self.write(dumps(load(cfg.img_dir, True)))

class api_handler(tornado.web.RequestHandler):
    def post(self, action):
        data = loads(self.request.body.decode('utf-8'))
        if action == 'json_update':
            if isdir(data['path']):
                path = join(data['path'],'_album.json')
            else:
                path = change_ext(data['path'],'json')
            _editor = JsonEditor(path)
            _editor[data['key']] = data['value']

class upload_handler(tornado.web.RequestHandler):
    def post(self):
        fileinfo = self.request.body
        fname = self.get_argument('filename', default=None)
        if not fname:
            self.finish('No filename')
            return

        with open(fname, 'wb') as f:
            f.write(self.request.body)
        self.finish(fname + ' is uploaded')

def run():
    print('Start')
    tornado.options.parse_command_line()
    app = tornado.web.Application(
        handlers=[
            (r'/?',index_handler),
            (r'/data',data_handler),
            (r'/img/(.*)', tornado.web.StaticFileHandler, {'path': cfg.img_dir}),
            (r'/api/(.*)',api_handler),
            (r'/upload',upload_handler),
        ],
        template_path=join('editor'),
        static_path=join('editor','static'),
        debug=True
    )
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(81)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    run()
