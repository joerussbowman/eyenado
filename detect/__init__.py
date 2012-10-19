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

""" Implents the interface with Foscam cameras and clones
using the cgi commands available on the camera interfaces.

Tested with an Agasio A603W Camera
"""

import os
import sys
import time
import Image
import base64
import urllib
import urllib2
import logging
import datetime
import cStringIO
import ImageChops
import numpy
import tornado.httpclient
import tornado.gen

class Camera:
    def __init__(self, ioloop, name, host, user="admin", password="", cam_type="foscam", threshold=1200, pull_speed=500):
        """ Camera is the primary interface to the camera.

        ioloop:     The ioloop this application is running in, used for
                    scheduling
        name:       Camera name
        host:       hostname or ip address of the server, do not include 
                    http://, ie: 192.168.1.10
        user:       the user name to connect to the server as
        password:   the password for the user
        cam_type:   string to identify the camera type, currenly only foscam
                    is supported
        threshold:  the amount of acceptable entropy between images to detect
                    motion. 1200 worked for a camera behind a window with
                    a screen. You may need to adjust this based on camera
                    location.
        pull_speed: how fast, in miliseconds to pull images from the camera. 

        Each camera will have it's own http client, authentication credentials
        are sent via a base64 Authorize header. Currently ssl connections are
        not supported.
        """
        self.name = name
        self.host = host
        self.ioloop = ioloop
        self.user = user
        self.password = password
        self.cam_type = cam_type
        self.threshold = threshold
        self.pull_speed = pull_speed

        self.current_image = None
        base64string = base64.encodestring('%s:%s' % (self.user, self.password)).replace('\n', '')
        self.http_client = tornado.httpclient.AsyncHTTPClient()
        self.url = "http://%s/snapshot.cgi" % self.host
        self.headers = {"Authorization": "Basic %s" % base64string}
        self.request = tornado.httpclient.HTTPRequest(url=self.url, headers=self.headers)

        self.images = []
        self.errors = 0

    @tornado.gen.engine
    def get_image(self, current=False, callback=None):
        """ TODO: Abstract this more for other camera vendors.

        For foscam cameras this will connect to the camera snapshot 
        cgi. There is a videostream cgi that uses server push, but 
        by pulling snapshots it's easier to manage image processing
        time and also there's no need to deal with monitoring the
        connection to the server to make sure it's still alive.

        Returns the image as a raw cString in order to pass to
        PIL. This should be enough abstraction that other camera
        models can be handled in the future.
        """
        while len(self.images) > 1:
            self.images.pop(0)
        response = yield tornado.gen.Task(self.http_client.fetch, self.request)
        if not response.error:
            img_data = cStringIO.StringIO(response.body)
            self.images.append(Image.open(img_data))
        else:
            self.errors += 1

        callback()
    
    @tornado.gen.engine
    def monitor(self):
        while len(self.images) < 2 and self.errors < 3:
            yield tornado.gen.Task(self.get_image)
        if self.errors < 3:
            entropy = Images().do_comparison(self.images)
            self.images.pop(0)
            print entropy
            if entropy > self.threshold:
                print "over threshold "

class Images:
    def do_comparison(self, images):
        diffs = ImageChops.difference(images[0], images[1])
        return self.get_entropy(diffs)

    def get_entropy(self, image):
        w,h = image.size
        a = numpy.array(image.convert('RGB')).reshape((w*h,3))
        h,e = numpy.histogramdd(a, bins=(16,)*3, range=((0,256),)*3)
        prob = h/numpy.sum(h)
        return -numpy.sum(numpy.log2(prob[prob>0]))

