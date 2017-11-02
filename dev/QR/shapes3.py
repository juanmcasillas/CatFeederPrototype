#!/usr/bin/env python

import sys
import os.path
import argparse
from videotools import *
from check_pi import *

import imutils
from PIL import  Image
import zbar
import numpy
from numpy.core.defchararray import center

class Shape:
        def __init__(self, center, type):
            self.center = center
            self.distance = 0.0
            self.type = type
            
        def Distance(self, point):
            self.distance = cv2.norm(self.center, point.center)
            
        def __str__(self):
            s = "Type: %s Center: (%d,%d) Distance: %3.2f" % (self.type, self.center[0], self.center[1], self.distance)
            return s
         

class ShapeDetector:
    def __init__(self):
        pass
 
    def detect(self, c):
        # initialize the shape name and approximate the contour
        shape = "unidentified"
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.07 * peri, True)
        
        # if the shape is a triangle, it will have 3 vertices
        if len(approx) == 3:
            shape = "triangle"
 
        # if the shape has 4 vertices, it is either a square or
        # a rectangle
        elif len(approx) == 4:
            # compute the bounding box of the contour and use the
            # bounding box to compute the aspect ratio
            (x, y, w, h) = cv2.boundingRect(approx)
            ar = w / float(h)
 
            # a square will have an aspect ratio that is approximately
            # equal to one, otherwise, the shape is a rectangle
            shape = "square" if ar >= 0.95 and ar <= 1.05 else "rectangle"
            shape = "rectangle"
 
        # if the shape is a pentagon, it will have 5 vertices
        elif len(approx) == 5:
            shape = "pentagon"
 
        # otherwise, we assume the shape is a circle
        else:
            shape = "circle"
 
        # return the name of the shape
        #return shape
        return "%s %3.2f" % (shape,cv2.contourArea(c))

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

    # calculated with hsvselect (change light, change this)
    greenLower = numpy.array([26, 33, 14],numpy.uint8) # BGR
    greenUpper = numpy.array([87, 219, 108],numpy.uint8)  # BGR
    #greenLower = (29, 86, 6)
    #greenUpper = (64, 255, 255)
    #greenLower = numpy.array([33, 31, 100],numpy.uint8) # BGR
    #greenUpper = numpy.array([81, 247, 219],numpy.uint8)  # BGR
    greenLower = numpy.array([37, 43, 39],numpy.uint8) # BGR
    greenUpper = numpy.array([91, 255, 255],numpy.uint8) # BGR


    while True:
        result,img = camHandler.read(videoport=True)
        if not result:
            break

        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        hsv = cv2.GaussianBlur(hsv, (17, 17), 0)
        
        mask = cv2.inRange(hsv, greenLower, greenUpper)
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)
        
        #output = cv2.bitwise_and(img, img, mask = mask) # to remove (debug)
        #gray = cv2.cvtColor(output, cv2.COLOR_BGR2GRAY) # to remove (debug)

        #thresh = cv2.threshold(gray, 60, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C)[1]
    
        # find contours in the thresholded image and initialize the
        # shape detector
        cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        cnts = cnts[0] if imutils.is_cv2() else cnts[1]
        sd = ShapeDetector()

        # loop over the contours
        
 
        
        lshapes = []
        
        for c in cnts:
            # compute the center of the contour, then detect the name of the
            
            # shape using only the contour
            
            if cv2.contourArea(c) < 150.0:
                continue
            M = cv2.moments(c)
            cX = 0
            cY = 0
            if M["m00"] != 0: cX = int((M["m10"] / M["m00"]) * 1)
            if M["m00"] != 0: cY = int((M["m01"] / M["m00"]) * 1)
            shape = sd.detect(c)

            
            # multiply the contour (x, y)-coordinates by the resize ratio,
            # then draw the contours and the name of the shape on the image
            c = c.astype("float")
            #c *= ratio
            c = c.astype("int")
            cv2.drawContours(img, [c], -1, (0, 255, 0), 2)
            cv2.putText(img, shape, (cX, cY), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
         
            if len(lshapes) == 0:
                lshapes.append( Shape( (cX, cY), shape ))
            else:
                s = Shape( (cX,cY), shape )
                s.Distance( lshapes[-1] )
                lshapes.append(s)
         
        # analyze data
    
        triangles = 0
        rectangles = 0
        squares = 0
        circles = 0
        pentagons = 0
        
        SHAPES_NEEDED = 4
        
        if len(lshapes) >= SHAPES_NEEDED:
            
            distance= 0.0
            for j in range(len(lshapes)):
                i = lshapes[j]
                print i
                if i.type == 'circle': circles += 1
                if i.type == 'triangle': triangles += 1
                if i.type == 'square': squares += 1
                if i.type == 'rectangle': rectangles += 1
                if i.type == 'pentagon': pentagons += 1
            
                distance += i.distance
                
            distance = distance / (len(lshapes)-1)
            print "DistanceAvg: %3.2f" % distance
            # get 
            
        
            if triangles >= SHAPES_NEEDED: print "%d triangles: Firulais" % SHAPES_NEEDED
            if rectangles >=SHAPES_NEEDED: print "%d rectangles: Neko" % SHAPES_NEEDED
            if circles >= SHAPES_NEEDED: print "%d circles: Eli"% SHAPES_NEEDED
            if squares >= SHAPES_NEEDED: print "%d squares: --"% SHAPES_NEEDED
            if pentagons >= SHAPES_NEEDED: print "%d pentagon: --"% SHAPES_NEEDED
        
        cv2.imshow("Image", img)
        if not WaitForKeyToExit():
            break

 

    #if args.verbose: 
        #ocv2_img = cv2.cvtColor(numpy.array(pil),cv2.COLOR_RGB2BGR)
        #ocv2_img = cv2.cvtColor(numpy.array(pil),cv2.COLOR_GRAY2BGR)
        #cv2.imshow('im',ocv2_img)
        
    cv2.destroyAllWindows()
    
