#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-

import sys
import tornado.web
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.websocket

from   os.path     import join
from   gen         import cfg
from   core.loader import load
from   json        import dumps, loads

class index_handler(tornado.web.RequestHandler):
    def get(self):
        self.render('index.html')

class data_handler(tornado.web.RequestHandler):
    def get(self):
        self.set_header('Content-Type', 'application/json')
        self.write(dumps(load(cfg.img_dir, True)))


def run():
    print('Start')
    tornado.options.parse_command_line()
    app = tornado.web.Application(
        handlers=[
            (r'/?',index_handler),
            (r'/data',data_handler)
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
