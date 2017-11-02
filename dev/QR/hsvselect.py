#!/usr/bin/env python

import sys
import os.path
import argparse
from videotools import *
from check_pi import *

import imutils
from PIL import  Image
import zbar
import numpy as np

def nothing(x):
    pass
# Creating a window for later use



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help="Show images", action="store_true", default=False)
    parser.add_argument("-c:w", "--camera_width", help="Capture Width", action="store", type=int, default=800)
    parser.add_argument("-c:h", "--camera_height", help="Capture Height", action="store", type=int, default=608)
    parser.add_argument("-c:f", "--camera_fps", help="Frames per second", action="store", type=int, default=30)
    parser.add_argument("-c:r", "--camera_rotation", help="Camera Rotation", action="store", type=int, default=0)
        
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

    greenLower = np.array([10, 50, 10],np.uint8) # BGR
    greenUpper = np.array([30, 151, 36],np.uint8)  # BGR
    #greenLower = (29, 86, 6)
    #greenUpper = (64, 255, 255)

    cv2.namedWindow('image')
    
    # create trackbars for color change
    cv2.createTrackbar('HMin','image',0,179,nothing) # Hue is from 0-179 for Opencv
    cv2.createTrackbar('SMin','image',0,255,nothing)
    cv2.createTrackbar('VMin','image',0,255,nothing)
    cv2.createTrackbar('HMax','image',0,179,nothing)
    cv2.createTrackbar('SMax','image',0,255,nothing)
    cv2.createTrackbar('VMax','image',0,255,nothing)
    
    # Set default value for MAX HSV trackbars.
    cv2.setTrackbarPos('HMax', 'image', 179)
    cv2.setTrackbarPos('SMax', 'image', 255)
    cv2.setTrackbarPos('VMax', 'image', 255)
    # Initialize to check if HSV min/max value changes
    hMin = sMin = vMin = hMax = sMax = vMax = 0
    phMin = psMin = pvMin = phMax = psMax = pvMax = 0

    
    while True:
        result,img = camHandler.read(videoport=True)
        if not result:
            break
    
        output = img
    
        # get current positions of all trackbars
        hMin = cv2.getTrackbarPos('HMin','image')
        sMin = cv2.getTrackbarPos('SMin','image')
        vMin = cv2.getTrackbarPos('VMin','image')
    
        hMax = cv2.getTrackbarPos('HMax','image')
        sMax = cv2.getTrackbarPos('SMax','image')
        vMax = cv2.getTrackbarPos('VMax','image')
    
        # Set minimum and max HSV values to display
        lower = np.array([hMin, sMin, vMin])
        upper = np.array([hMax, sMax, vMax])
    
        # Create HSV Image and threshold into a range.
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, lower, upper)
        output = cv2.bitwise_and(img,img, mask= mask)
    
        # Print if there is a change in HSV value
        if( (phMin != hMin) | (psMin != sMin) | (pvMin != vMin) | (phMax != hMax) | (psMax != sMax) | (pvMax != vMax) ):
            print("(hMin = %d , sMin = %d, vMin = %d), (hMax = %d , sMax = %d, vMax = %d)" % (hMin , sMin , vMin, hMax, sMax , vMax))
            phMin = hMin
            psMin = sMin
            pvMin = vMin
            phMax = hMax
            psMax = sMax
            pvMax = vMax
    
        # Display output image
        cv2.imshow('image',output)
    
        # Wait longer to prevent freeze for videos.
        if cv2.waitKey(33) & 0xFF == ord('q'):
            break
  
cv2.destroyAllWindows()












