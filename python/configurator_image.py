#!/usr/bin/env python
###############################################################################
#
# configurator.py
# Creates the OpenCV parameter configuration using a openCV GUI
#
#
###############################################################################



import sys
import os.path
import argparse
from videotools import *
from check_pi import *

import imutils
from PIL import  Image

import numpy

def nothing(x):
    pass
# Creating a window for later use

import detector

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-c:w", "--camera_width", help="Capture Width", action="store", type=int, default=800)
    parser.add_argument("-c:h", "--camera_height", help="Capture Height", action="store", type=int, default=608)
    parser.add_argument("-c:f", "--camera_fps", help="Frames per second", action="store", type=int, default=30)
    parser.add_argument("-c:r", "--camera_rotation", help="Camera Rotation", action="store", type=int, default=0)
    parser.add_argument("-s", "--stored", help="Use Stored Config", action="store_true", default=True)
        
    args = parser.parse_args()

    cv2.namedWindow('image')
    cv2.namedWindow('controls')
 
        
    # create trackbars for color change, configuration, and so on
    cv2.createTrackbar('HMin','controls',0,180,nothing) # Hue is from 0-179 for Opencv
    cv2.createTrackbar('SMin','controls',0,255,nothing)
    cv2.createTrackbar('VMin','controls',0,255,nothing)
    cv2.createTrackbar('HMax','controls',0,180,nothing)
    cv2.createTrackbar('SMax','controls',0,255,nothing)
    cv2.createTrackbar('VMax','controls',0,255,nothing)
    cv2.createTrackbar('ShowMask','controls',0,1,nothing)
    # create trackbars for showmask, gaussian blur, and so on.

    
    # Initialize to check if HSV min/max value changes
    hMin = sMin = vMin = hMax = sMax = vMax = 0
    phMin = psMin = pvMin = phMax = psMax = pvMax = 0
    ShowMask = 0

    if args.stored:
        # previous config
        #https://stackoverflow.com/questions/31590499/opencv-android-green-color-detection
        #hsvMin = numpy.array([40, 99, 26],numpy.uint8) # BGR
        #hsvMax = numpy.array([94, 255, 255],numpy.uint8) # BGR
        hsvMin = numpy.array([37, 43, 39],numpy.uint8) # BGR
        hsvMax = numpy.array([91, 255, 255],numpy.uint8) # BGR

    
 

        # previous config

        
        cv2.setTrackbarPos('HMin', 'controls', hsvMin[0])
        cv2.setTrackbarPos('SMin', 'controls', hsvMin[1])
        cv2.setTrackbarPos('VMin', 'controls', hsvMin[2])
        
        cv2.setTrackbarPos('HMax', 'controls', hsvMax[0])
        cv2.setTrackbarPos('SMax', 'controls', hsvMax[1])
        cv2.setTrackbarPos('VMax', 'controls', hsvMax[2])
        
        


        
    else:
        # Set default value for MAX HSV trackbars.
        cv2.setTrackbarPos('HMax', 'controls', 255)
        cv2.setTrackbarPos('SMax', 'controls', 255)
        cv2.setTrackbarPos('VMax', 'controls', 255)
     

    img = cv2.imread('framedump-TEST/frame_00000000.png')
    while True:
        
        
        # get current positions of all trackbars
        
        
        
        hMin = cv2.getTrackbarPos('HMin','controls')
        sMin = cv2.getTrackbarPos('SMin','controls')
        vMin = cv2.getTrackbarPos('VMin','controls')
    
        hMax = cv2.getTrackbarPos('HMax','controls')
        sMax = cv2.getTrackbarPos('SMax','controls')
        vMax = cv2.getTrackbarPos('VMax','controls')
        
        ShowMask = cv2.getTrackbarPos('ShowMask','controls')

      
     
        # Set minimum and max HSV values to display
        lower = numpy.array([hMin, sMin, vMin])
        upper = numpy.array([hMax, sMax, vMax])
    
        # sharpen

    
    
        # Create HSV Image and threshold into a range.
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, lower, upper)
        output = cv2.bitwise_and(img,img, mask= mask)
        
        print "#"
        print "# configuration begins"
        print "hsvMin = np.array([%d, %d, %d],np.uint8) # HSV" % (hMin,sMin,vMin)
        print "hsvMax = np.array([%d, %d, %d],np.uint8) # HSV" % (hMax,sMax,vMax)
        print "# "    
       
        # Display output image
        
        if ShowMask == 0:
            cv2.imshow('image',output)
        else:
            cv2.imshow('image',mask)
    
        # Wait longer to prevent freeze for videos.
        if cv2.waitKey(33) & 0xFF == ord('q'):
            break
  
cv2.destroyAllWindows()












