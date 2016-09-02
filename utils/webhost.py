#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-

import tornado.web
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.websocket
import astphoto


class index_handler(tornado.web.RequestHandler):
    def get(self):
        static = self.get_argument("static", None)
        photo = self.get_argument("photo", None)
        _all = self.get_argument("all", None)
        if _all is not None or static is not None:
            print('Copying static')
            astphoto.copy_static()
            astphoto.render_index()
        if _all is not None or photo is not None:
            print('astphotoerating struct')
            astphoto.astphotoerate_and_save()
        self.render('index.html')


def run():
    print('Start')
    tornado.options.parse_command_line()
    app = tornado.web.Application(
        handlers=[
            (r'/?', index_handler)
        ],
        template_path=astphoto.cfg.out_dir,
        static_path=astphoto.cfg.out_dir + '/' + astphoto.cfg.static_dir,
        debug=True
    )
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(80)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    run()
