#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-

import sys
import os
import json
import tornado.web
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.websocket
import gen

class index_handler(tornado.web.RequestHandler):
    def get(self):
        static = self.get_argument("static", None)
        photo  = self.get_argument("photo", None)
        _all   = self.get_argument("all", None)
        print(static != None,photo != None,_all != None)
        if _all != None or static != None:
            print('Copying static')
            gen.copy_static()
            gen.render_index()
        if _all != None or photo != None:
            print('Generating struct')
            gen.generate_and_save()
        self.render('index.html')

def run():
    print('Start')
    tornado.options.parse_command_line()
    app = tornado.web.Application(
        handlers=[
            (r'/?',index_handler)
        ],
        template_path='out/',
        static_path='out/static',
        debug=True
    )
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(80)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    run()
