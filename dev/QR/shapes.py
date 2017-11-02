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


class ShapeDetector:
    def __init__(self):
        pass
 
    def detect(self, c):
        # initialize the shape name and approximate the contour
        shape = "unidentified"
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.04 * peri, True)
        
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
 
        # if the shape is a pentagon, it will have 5 vertices
        elif len(approx) == 5:
            shape = ""
 
        # otherwise, we assume the shape is a circle
        else:
            shape = ""
 
        # return the name of the shape
        return shape

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


    while True:
        result,img = camHandler.read()
        if not result:
            break

        if not WaitForKeyToExit():
            break

       
        resized = imutils.resize(img, width=300)
        ratio = img.shape[0] / float(resized.shape[0])
         
        # convert the resized image to grayscale, blur it slightly,
        # and threshold it
        gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
        
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        thresh = cv2.threshold(blurred, 60, 255, cv2.THRESH_BINARY)[1]
         
        # find contours in the thresholded image and initialize the
        # shape detector
        cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        cnts = cnts[0] if imutils.is_cv2() else cnts[1]
        sd = ShapeDetector()

        # loop over the contours
        for c in cnts:
            # compute the center of the contour, then detect the name of the
            # shape using only the contour
            M = cv2.moments(c)
            cX = 0
            cY = 0
            if M["m00"] != 0: cX = int((M["m10"] / M["m00"]) * ratio)
            if M["m00"] != 0: cY = int((M["m01"] / M["m00"]) * ratio)
            shape = sd.detect(c)
         
            # multiply the contour (x, y)-coordinates by the resize ratio,
            # then draw the contours and the name of the shape on the image
            c = c.astype("float")
            c *= ratio
            c = c.astype("int")
            cv2.drawContours(img, [c], -1, (0, 255, 0), 2)
            cv2.putText(img, shape, (cX, cY), cv2.FONT_HERSHEY_SIMPLEX,
                0.5, (255, 255, 255), 2)
         
            # show the output image
        cv2.imshow("Image", img)
        #cv2.waitKey(0)

 

    #if args.verbose: 
        #ocv2_img = cv2.cvtColor(numpy.array(pil),cv2.COLOR_RGB2BGR)
        #ocv2_img = cv2.cvtColor(numpy.array(pil),cv2.COLOR_GRAY2BGR)
        #cv2.imshow('im',ocv2_img)
        
    cv2.destroyAllWindows()
    
