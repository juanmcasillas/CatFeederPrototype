#!/usr/bin/env python

import sys
import os.path
import argparse
from videotools import *
from check_pi import *
import time

import imutils
from PIL import  Image
import numpy
from numpy.core.defchararray import center
import os
import os.path

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help="Show images", action="store_true", default=False)
    parser.add_argument("-c:w", "--camera_width", help="Capture Width", action="store", type=int, default=800)
    parser.add_argument("-c:h", "--camera_height", help="Capture Height", action="store", type=int, default=608)
    parser.add_argument("-c:f", "--camera_fps", help="Frames per second", action="store", type=int, default=30)
    parser.add_argument("-c:r", "--camera_rotation", help="Camera Rotation", action="store", type=int, default=180)
    parser.add_argument("-e", "--element", help="Camera Rotation", action="store")  
        
    args = parser.parse_args()

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

  
    if not os.path.exists(args.element):
        os.makedirs(args.element)
        
    counter = 0
    while counter < 50:
        result,img = camHandler.read()
        if not result:
            break
    
        img = img[0:608, 0:640] # ROI. Was rotated!!

        
        p = '%s/%07d.jpg' % (args.element,counter)
        cv2.imwrite(p, img)
        
        counter += 1
        print counter
        
         
                
   

    cv2.destroyAllWindows()
    
