#!/usr/bin/env python

import sys
import os.path
import argparse
from videotools import *
from check_pi import *

from PIL import  Image
import zbar
import numpy

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help="Show images", action="store_true", default=False)
    parser.add_argument("-c:w", "--camera_width", help="Capture Width", action="store", type=int, default=800)
    parser.add_argument("-c:h", "--camera_height", help="Capture Height", action="store", type=int, default=608)
    parser.add_argument("-c:f", "--camera_fps", help="Frames per second", action="store", type=int, default=30)
    parser.add_argument("-c:r", "--camera_rotation", help="Camera Rotation", action="store", type=int, default=0)
        
    args = parser.parse_args()

    pos_frame = 0

    if IsRaspberry():
        from cameratools import *
        camHandler = PiCameraHandler(resolution=(args.camera_width,args.camera_height), framerate=args.camera_fps, rotation=args.camera_rotation)
        print "Using Raspberry Camera"
    else:
        camHandler = cv2.VideoCapture(0)
        camHandler.set(cv2.CAP_PROP_FRAME_WIDTH, args.camera_width)
        camHandler.set(cv2.CAP_PROP_FRAME_HEIGHT, args.camera_height)
        camHandler.set(cv2.CAP_PROP_FPS, args.camera_fps)
        
        print "Using Generic Webcam"


    scanner = zbar.ImageScanner()
    scanner.parse_config('enable')
  

    while True:
        result,img = camHandler.read(videoport=True)
        if not result:
            break

        if not WaitForKeyToExit():
            break

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY, dstCn=0)
        pil = Image.fromarray(gray)
        print pil.format
        width, height = pil.size
        raw = pil.tostring()

	zimage = zbar.Image(width,height,'Y800',raw) # Y800, GREY
        scanner.scan(zimage)

        for symbol in zimage:
            print 'decoded', symbol.type, 'symbol', '"%s"' % symbol.data
	    tl = 9999
            bl = 9999
            tr = 0
            br = 0
            for l in symbol.location:
                if l[0] < tl: tl = l[0]
                if l[1] < bl: bl = l[1]
                if l[0] > tr: tr = l[0]
                if l[1] > br: br = l[1]
            print tl,bl,tr,br
            cv2.rectangle(gray,(tl,bl),(tr,br),2)


        del(zimage)

	if args.verbose: 
	    #ocv2_img = cv2.cvtColor(numpy.array(pil),cv2.COLOR_RGB2BGR)
	    ocv2_img = cv2.cvtColor(numpy.array(pil),cv2.COLOR_GRAY2BGR)
            cv2.imshow('im',ocv2_img)
        
    cv2.destroyAllWindows()
    
