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
        def __init__(self, center, shape, contour):
            self.center = center
            self.distance = 0.0
            self.shape = shape
            self.c = contour
            
        def Distance(self, point):
            self.distance = cv2.norm(self.center, point.center)
            
        def __str__(self):
            s = "Shape: %s Center: (%d,%d) Distance: %3.2f" % (self.shape, self.center[0], self.center[1], self.distance)
            return s
         

class ShapeDetector:
    def __init__(self, coef=0.04):
        self.coef = coef
 
    def detect(self, c):
        # initialize the shape name and approximate the contour
        shape = "unidentified"
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, self.coef * peri, True)
        
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
            #shape = "square" if ar >= 0.95 and ar <= 1.05 else "rectangle"
            shape = "rectangle"
 
        # if the shape is a pentagon, it will have 5 vertices
        #elif len(approx) == 5:
        #    shape = "pentagon"
 
        # otherwise, we assume the shape is a circle
        else:
            shape = "circle"
 
        # return the name of the shape
        return shape
        #return "%s %3.2f" % (shape,cv2.contourArea(c))

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

    
    #hsvMin = numpy.array([33, 31, 100],numpy.uint8) # BGR
    #hsvMax = numpy.array([81, 247, 219],numpy.uint8)  # BGR

    ## configuration options from CONFIGURATOR.py

    hsvMin = numpy.array([40, 99, 26],numpy.uint8) # BGR
    hsvMax = numpy.array([94, 255, 255],numpy.uint8) # BGR
    hsvMin = numpy.array([39, 42, 84],numpy.uint8) # BGR
    hsvMax = numpy.array([102, 175, 197],numpy.uint8) # BGR
    #latest
    hsvMin = numpy.array([44, 37, 99],numpy.uint8) # BGR
    hsvMax = numpy.array([90, 255, 255],numpy.uint8) # BGR
    
    Blur = 5
    Dilate = 0
    CountourArea = 100
    Coef = 0.04
    SHAPES_NEEDED = 4
    PERCENT_DISTANCE=50
    FILTER_BY_DISTANCE=False

    while True:
        result,img = camHandler.read()
	
        if not result:
            break
        img = cv2.bilateralFilter(img,13,75,75)
        
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, hsvMin, hsvMax)
        #kernel = numpy.ones((2,2),numpy.uint8)
        #mask = cv2.erode(mask, kernel, iterations=Erode)
        #mask = cv2.dilate(mask, kernel, iterations=Dilate)
        
        output = cv2.bitwise_and(img,img, mask= mask)
        
        #output = cv2.bitwise_and(img, img, mask = mask) # to remove (debug)
        #gray = cv2.cvtColor(output, cv2.COLOR_BGR2GRAY) # to remove (debug)

        #thresh = cv2.threshold(gray, 60, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C)[1]
    
        # find contours in the thresholded image and initialize the
        # shape detector
        cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        cnts = cnts[0] if imutils.is_cv2() else cnts[1]
        sd = ShapeDetector(Coef)

        # loop over the contours
        
        
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

    
            if len(lshapes) == 0:
                lshapes.append( Shape( (cX, cY), shape, c ))
            else:
                s = Shape( (cX,cY), shape, c )
                s.Distance( lshapes[-1] )
                lshapes.append(s)
         
        # analyze data

 
        cshapes = []
        rshapes = []
        
        distance_avg = 0.0
        distance_max = 0.0
        distance_min = 99999999999999.9
        distance_c = 0        
        
        
        if len(lshapes) >= SHAPES_NEEDED:
            
            #1 get SHAPES_NEEDED CONTIGOUS
            
            for j in range(len(lshapes)-1):
                goout = False
                cshapes.append(lshapes[j])
                for i in range(j+1,len(lshapes)):
                    if lshapes[j].shape == lshapes[i].shape:
                        cshapes.append(lshapes[i])
                        if len(cshapes) >= SHAPES_NEEDED:
                            goout = True
                            break
                    else:
                        cshapes = []
                        break
                if goout: 
                    break
                
        if len(cshapes) >= SHAPES_NEEDED:
            #print "contiguous shapes"
            
            if FILTER_BY_DISTANCE:
            
                for i in cshapes:
                    distance_avg += i.distance
                    if i.distance != 0.0: distance_c +=1
                    
        
                distance_avg = distance_avg / distance_c
                # filter in base at distance.
               
                delta_distance = ((distance_avg * PERCENT_DISTANCE) / 100.0) / 2.0
                #print("Distance Min: %3.2f, Max: %3.2f, Avg: %3.2f | %3.2f%%, delta: %3.2f" % (distance_min, distance_max, distance_avg, PERCENT_DISTANCE, delta_distance))
                
                # filter by distance
            
                for i in range(len(cshapes)):
                    s = cshapes[i]
                    
                    if  distance_avg - delta_distance <= s.distance <= distance_avg + delta_distance:
                        #print "%3.2f <= %3.2f <= %3.2f" % (distance_avg - delta_distance,s.distance,distance_avg + delta_distance)
                        rshapes.append(s)
            else:
                rshapes = cshapes

                        
        rshapes = rshapes[0:SHAPES_NEEDED]
        if len(rshapes) == SHAPES_NEEDED:   
            for i in rshapes:
                #print i
                cv2.drawContours(img, [i.c], -1, (0, 255, 0), 2)
                cv2.putText(img, i.shape, (i.center[0], i.center[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)    
                
                if rshapes[0].shape == "triangle": print "found Firulais"
                if rshapes[0].shape == "rectangle": print "found Neko"
                if rshapes[0].shape == "circle": print "found Eli"
        
            
 
        if args.verbose:
            cv2.imshow("Image", img)
            if not WaitForKeyToExit():
                break

 

    #if args.verbose: 
        #ocv2_img = cv2.cvtColor(numpy.array(pil),cv2.COLOR_RGB2BGR)
        #ocv2_img = cv2.cvtColor(numpy.array(pil),cv2.COLOR_GRAY2BGR)
        #cv2.imshow('im',ocv2_img)
        
    cv2.destroyAllWindows()
    
