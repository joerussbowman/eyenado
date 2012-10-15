#!/usr/bin/env python
#
# Copyright 2012 Joseph Bowman
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import os
import detect
import tornado.web
import tornado.escape
import tornado.ioloop
import tornado.options
import tornado.template


# web server application and handlers
class CoreHandler(tornado.web.RequestHandler):
    def render_string(self, template_name, **kwargs):
        kwargs['cameras'] = self.application.cameras
        return super(CoreHandler, self).render_string(template_name, **kwargs)
        
class BaseHandler(tornado.web.RequestHandler):
    """ BaseHandler is the base class for all request handlers
    except the special config handler. It will redirect to /config/
    if there is no camera configuration.
    """
    def prepare(self, * args, ** kwargs):
        if not "cameras" in globals() or len(cameras) < 1:
            self.redirect("/config/")

class ConfigHandler(CoreHandler):
    def get(self):
        self.render("config.tpl")

class MainHandler(BaseHandler):
    def get(self):
        self.render("main.tpl")

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            ("/", MainHandler),
            ("/config/?", ConfigHandler),
        ]
        settings = dict(
            cookie_secret = "40daa7fd545251e59e6ded007abd4f7b7b9762f8",
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            xsrf_cookies=True,
            debug=True,
        )
        self.config_file = "etc/server.conf"
        self.cameras = []
        tornado.web.Application.__init__(self, handlers, ** settings)

application = Application()
# ioloop set up and configuration management
def load_config():
    # stop cameras
    for camera in application.cameras:
        if hasattr(camera, "loop"):
            camera.loop.stop()
    # reset camera list
    cameras = []
    with open(application.config_file, 'r') as config_f:
        config_json = config_f.read()
    application.config = tornado.escape.json_decode(config_json)
    for camera in application.config["cameras"]:
        c = detect.Camera(ioloop, **camera)
        c.loop = tornado.ioloop.PeriodicCallback(c.monitor, c.pull_speed, ioloop)
        c.loop.start()
        application.cameras.append(c)

def write_config(blank=False):
    pass

ioloop = tornado.ioloop.IOLoop.instance()

#cameras = [
#        detect.Camera("outdoor1", "192.168.1.10", ioloop),
#        ]
# fire it up!
if __name__ == "__main__":
    load_config()
    application.listen(8888)
    ioloop.start()

