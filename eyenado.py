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
import cStringIO
import tornado.web
import tornado.escape
import tornado.ioloop
import tornado.options
import tornado.template

CONFIG_PATH = "etc/"
CONFIG_FILE = CONFIG_PATH + "server.conf"
SNAPSHOTS_PATH = "snapshots/"

# web server application and handlers
class CoreHandler(tornado.web.RequestHandler):
    def render_string(self, template_name, **kwargs):
        kwargs['cameras'] = self.application.cameras
        return super(CoreHandler, self).render_string(template_name, **kwargs)

    def error_page(self, error_msg):
        self.render("error.tpl", error_msg=error_msg)
        
class BaseHandler(CoreHandler):
    """ BaseHandler is the base class for all request handlers
    except the special config handler. It will redirect to /config/
    if there is no camera configuration.
    """
    def prepare(self, * args, ** kwargs):
        if len(self.application.cameras) < 1:
            self.redirect("/config/")

class ConfigHandler(CoreHandler):
    def get(self):
        # TODO: Add support for advanced options like authentication
        self.render("config.tpl")

    def post(self):
        # TODO: Add support for advanced options like authentication
        # TODO: Check camera host is a valid camera when added
        do = self.get_argument("do", None)
        name = self.get_argument("camera.name", None)
        host = self.get_argument("camera.host", None)
        user = self.get_argument("camera.user", None)
        password = self.get_argument("camera.password", None)
        if do == "add":
            if not name:
                self.error_page("You did not give your camera a name")
                return
            if not name.isalnum():
                self.error_page("Camera names must be alphanumeric")
                return
            if not host:
                self.error_page("You did not specify a host for your camera. Host is usually the ipaddress of your camera.")
                return
            if "cameras" in self.application.config:
                self.application.config["cameras"].append({"name": name, "host": host, "user": user, "password": password})
            else:
                self.application.config["cameras"] = [{"name": name, "host": host}]
        if do == "delete":
            for camera in self.application.config["cameras"]:
                if camera["name"] == name:
                    self.application.config["cameras"].remove(camera)
                    print self.application.config
        write_config()
            
        self.redirect("/config/")

class MainHandler(BaseHandler):
    def get(self):
        self.render("main.tpl")

class GetImage(CoreHandler):
    def get(self, cam):
        print cam
        if not cam:
            raise tornado.web.HTTPError(404)
        for camera in self.application.cameras:
            if camera.name == cam:
               img_data = cStringIO.StringIO()
               camera.images[0].save(img_data, format="JPEG")
               img_data.seek(0)
               content = img_data.getvalue()
               self.write(content)
               self.set_header('Content-Type', 'image/jpg')
               self.flush()
               self.finish()
               return
        raise tornado.web.HTTPError(404)

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            ("/", MainHandler),
            ("/config/?", ConfigHandler),
            ("/getimage/(.*?)/?", GetImage),
        ]
        settings = dict(
            cookie_secret = "40daa7fd545251e59e6ded007abd4f7b7b9762f8",
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            xsrf_cookies=True,
            debug=True,
        )
        if not os.path.exists(CONFIG_PATH):
            os.makedirs(CONFIG_PATH)
        if not os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'w') as config_f:
                config_f.write(tornado.escape.json_encode({}))
        if not os.path.exists(SNAPSHOTS_PATH):
            os.makedirs(SNAPSHOTS_PATH)

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
    application.cameras = []
    with open(CONFIG_FILE, 'r') as config_f:
        config_json = config_f.read()
        application.config = tornado.escape.json_decode(config_json)
    if "cameras" in application.config:
        for camera in application.config["cameras"]:
            c = detect.Camera(ioloop, **camera)
            c.loop = tornado.ioloop.PeriodicCallback(c.monitor, c.pull_speed, ioloop)
            c.loop.start()
            application.cameras.append(c)

def write_config(blank=False):
    with open(CONFIG_FILE, 'w') as config_f:
        config_f.write(tornado.escape.json_encode(application.config))
    config_f.close()
    load_config()

ioloop = tornado.ioloop.IOLoop.instance()

if __name__ == "__main__":
    load_config()
    application.listen(8888)
    ioloop.start()

