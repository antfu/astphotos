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

class index_handler(tornado.web.RequestHandler):
    def get(self):
        self.render('index.html')

def run():
    if not os.path.exists('logs'):
        os.makedirs('logs')
    args = sys.argv
    args.append("--log_file_prefix=logs/web.log")
    tornado.options.parse_command_line()
    app = tornado.web.Application(
        handlers=[
            (r'/?',index_handler)
        ],
        template_path='',
        static_path='static',
        debug=True
    )
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(80)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    run()
