#!/usr/bin/env python
import os
import sys
import time
import Image
import base64
import urllib
import urllib2
import datetime
import cStringIO
import ImageChops
import numpy as np

# globals
DEFAULT_DEVICE_WIDTH  = 640
DEFAULT_DEVICE_HEIGHT = 480
SAVE_PATH = "/home/misty/Dropbox/cam/pics"
THRESHOLD = 1200
DEBUG = False 
VERBOSE = True

cam = {
        "user": "admin",
        "passwd": "",
        "url": "http://192.168.1.10/snapshot.cgi",
        }

# This class is based of a class posted on stackoverflow at the following
# url: 
# http://stackoverflow.com/questions/5524179/how-to-detect-motion-between-two-pil-images-wxpython-webcam-integration-exampl
class Images:
    def __init__(self, request, image1=None):
        self.image1 = image1
        self.request = request
        if not image1:
            self.image1 = self.getImage()
        time.sleep(0.5)
        self.image2 = self.getImage()

    def DoComparison(self, image1=None, image2=None):
        if not image1: image1 = self.image1
        if not image2: image2 = self.image2
        diffs = ImageChops.difference(image1, image2)
        return {
            "entropy": self.ImageEntropy(diffs),
            "img": image2
            }

    def ImageEntropy(self, image):
        w,h = image.size
        a = np.array(image.convert('RGB')).reshape((w*h,3))
        h,e = np.histogramdd(a, bins=(16,)*3, range=((0,256),)*3)
        prob = h/np.sum(h)
        return -np.sum(np.log2(prob[prob>0]))

    def getImage(self):
        try:
            imgRequest = cStringIO.StringIO(urllib2.urlopen(self.request).read())
            return Image.open(imgRequest)
        except:
            time.sleep(1)
            self.getImage()

if __name__=="__main__":
    base64string = base64.encodestring('%s:%s' % (cam["user"], cam["passwd"])).replace('\n', '')
    request = urllib2.Request(cam["url"])
    request.add_header("Authorization", "Basic %s" % base64string)
    imgCheck = {"img": None, "entropy": 0.0}
    print "Starting..."
    while True:
        imgCheck = Images(request, imgCheck["img"]).DoComparison()
        if DEBUG:
            print imgCheck["entropy"]
        if imgCheck["entropy"] > THRESHOLD:
            now = datetime.datetime.now()
            savePath = "%s/%s/%s/%s" % (SAVE_PATH, now.year, now.month, now.day)
            fileName = "%s/%s.%s.%s.jpg" % (savePath, now.hour, now.minute, now.second)
            if not os.path.exists(savePath):
                os.makedirs(savePath)
            imgCheck["img"].save(fileName, "JPEG")
            if VERBOSE:
                print "Saved %s with entropy %s" % (fileName, imgCheck["entropy"])
    

