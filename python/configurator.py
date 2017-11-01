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

    cv2.namedWindow('image')
    cv2.namedWindow('controls')
 
        
    # create trackbars for color change, configuration, and so on
    cv2.createTrackbar('HMin','controls',0,180,nothing) # Hue is from 0-179 for Opencv
    cv2.createTrackbar('SMin','controls',0,255,nothing)
    cv2.createTrackbar('VMin','controls',0,255,nothing)
    cv2.createTrackbar('HMax','controls',0,180,nothing)
    cv2.createTrackbar('SMax','controls',0,255,nothing)
    cv2.createTrackbar('VMax','controls',0,255,nothing)
    
    # create trackbars for showmask, gaussian blur, and so on.
    cv2.createTrackbar('ShowMask','controls',0,1,nothing)
    cv2.createTrackbar('CountourArea','controls',0,3000,nothing)
    cv2.createTrackbar('Coef','controls',0,100,nothing)
    
    # Initialize to check if HSV min/max value changes
    hMin = sMin = vMin = hMax = sMax = vMax = 0
    phMin = psMin = pvMin = phMax = psMax = pvMax = 0
    ShowMask = 0
    CountourArea = 0
    Coef = 0
  

    if args.stored:
        # previous config
        #https://stackoverflow.com/questions/31590499/opencv-android-green-color-detection
        #hsvMin = numpy.array([40, 99, 26],numpy.uint8) # BGR
        #hsvMax = numpy.array([94, 255, 255],numpy.uint8) # BGR
        hsvMin = numpy.array([37, 43, 39],numpy.uint8) # BGR
        hsvMax = numpy.array([91, 255, 255],numpy.uint8) # BGR

    
        CountourArea = 100
        Coef = 0.04

        # previous config

        
        cv2.setTrackbarPos('HMin', 'controls', hsvMin[0])
        cv2.setTrackbarPos('SMin', 'controls', hsvMin[1])
        cv2.setTrackbarPos('VMin', 'controls', hsvMin[2])
        
        cv2.setTrackbarPos('HMax', 'controls', hsvMax[0])
        cv2.setTrackbarPos('SMax', 'controls', hsvMax[1])
        cv2.setTrackbarPos('VMax', 'controls', hsvMax[2])
        
        
    
        cv2.setTrackbarPos('CountourArea', 'controls', CountourArea)
        cv2.setTrackbarPos('Coef', 'controls', int(Coef * 100.0))

        
    else:
        # Set default value for MAX HSV trackbars.
        cv2.setTrackbarPos('HMax', 'controls', 255)
        cv2.setTrackbarPos('SMax', 'controls', 255)
        cv2.setTrackbarPos('VMax', 'controls', 255)
        cv2.setTrackbarPos('CountourArea', 'controls', 300)
     

    
    while True:
        result,img = camHandler.read()
        if not result:
            break
    
        output = img
    
        # get current positions of all trackbars
        
        
        
        hMin = cv2.getTrackbarPos('HMin','controls')
        sMin = cv2.getTrackbarPos('SMin','controls')
        vMin = cv2.getTrackbarPos('VMin','controls')
    
        hMax = cv2.getTrackbarPos('HMax','controls')
        sMax = cv2.getTrackbarPos('SMax','controls')
        vMax = cv2.getTrackbarPos('VMax','controls')
        
        ShowMask = cv2.getTrackbarPos('ShowMask','controls')
        if cv2.getTrackbarPos('Blur','controls') % 2 == 1:
            Blur = cv2.getTrackbarPos('Blur','controls')
        

      
        
        CountourArea = cv2.getTrackbarPos('CountourArea','controls')
        Coef = cv2.getTrackbarPos('Coef','controls') / 100.0
     
        # Set minimum and max HSV values to display
        lower = numpy.array([hMin, sMin, vMin])
        upper = numpy.array([hMax, sMax, vMax])
    
        # sharpen

        img = cv2.bilateralFilter(img,13,75,75)
    
        # Create HSV Image and threshold into a range.
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        

        
        mask = cv2.inRange(hsv, lower, upper)

        output = cv2.bitwise_and(img,img, mask= mask)
        
        
    
    
        cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        cnts = cnts[0] if imutils.is_cv2() else cnts[1]
        sd = detector.ShapeDetector(Coef)
    
        lshapes = []
        
        for c in cnts:
            # compute the center of the contour, then detect the name of the
            
            # shape using only the contour
            
            if cv2.contourArea(c) < CountourArea:
                continue
            M = cv2.moments(c)
            cX = 0
            cY = 0
            if M["m00"] != 0: cX = int((M["m10"] / M["m00"]) * 1)
            if M["m00"] != 0: cY = int((M["m01"] / M["m00"]) * 1)
            shape = sd.detect(c)
            
            cv2.drawContours(output, [c], -1, (0, 255, 0), 1)
            cv2.putText(output, shape, (cX, cY), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)    
    
    
        # Print if there is a change in HSV value
        #if( (phMin != hMin) | (psMin != sMin) | (pvMin != vMin) | (phMax != hMax) | (psMax != sMax) | (pvMax != vMax) ):
        #    print("(hMin = %d , sMin = %d, vMin = %d), (hMax = %d , sMax = %d, vMax = %d)" % (hMin , sMin , vMin, hMax, sMax , vMax))
        #    phMin = hMin
        #    psMin = sMin
        #    pvMin = vMin
        #    phMax = hMax
        #    psMax = sMax
        #    pvMax = vMax
        print "#"
        print "# configuration begins"
        print "hsvMin = numpy.array([%d, %d, %d],numpy.uint8) # BGR" % (hMin,sMin,vMin)
        print "hsvMax = numpy.array([%d, %d, %d],numpy.uint8) # BGR" % (hMax,sMax,vMax)
        print "CountourArea = %d" % CountourArea
        print "Coef = %3.2f" % Coef
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












