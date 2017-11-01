#!/usr/bin/env python
################################################################################
#
# Main Program
# Detector.py
# JuanM.Casillas@gmail.com
#
# Detects the cat, opens the door. And so on.
#
###############################################################################

import sys
import os.path
import argparse
from videotools import *
from check_pi import *

import imutils
from PIL import  Image
#import zbar
import numpy
from numpy.core.defchararray import center


import time
import db
import config
import logging

import shutil


import cv2
import argparse
import numpy as np
import math
import os


# raspy conf

from kmeantools import *



class DetectorBase:
    def __init__(self):
        pass
    
    def Setup(self, videoport=True):
        pass

    def Identify(self):
        pass
    
    
class DetectorMock(DetectorBase):
    """mock class for development"""
    
    def __init__(self):
        DetectorBase.__init__(self)

    
    def Identify(self):
        #p = db.PetService().LoadByName('firulais') # not allowed
        p = db.PetService().LoadByName('neko') # allowed
        time.sleep(5)
        return p
        
    def GetPhoto(self):
        
        fname = int(time.time())
        photo_path = db.PhotoPath(fname)
        dirpath = os.path.dirname(photo_path)

        if not os.path.exists(dirpath):
            os.makedirs(dirpath, 755)

        # harcode this image, but save one from the camera in the right place
        shutil.copy(config.test_image, photo_path)
        
        # save the photo to the last photo image
        shutil.copy(photo_path, config.last_image)
        logging.info("Photo taken into %s" % photo_path)
        return photo_path
        


class DetectorCV2(DetectorBase):
    
    def __init__(self):
        DetectorBase.__init__(self)
        self.camHandler = None
        self.db = {}
        self.status = {}
        self.dbdir = DB_DIR

    def Info(self):
        for i in self.db.keys():
            item = self.db[i]
            logging.info("-- %s --- " % (i))
            logging.info("Histogram")
            logging.info(item.hist)
        
    def Init(self):
        self.status = {}
        for i in self.db.keys():
            self.status[i] = [0.0, 0, 0.0]
        
    def Load(self, id):
        item = O()
        item.hist = np.load("%s/%s_hist.npy" % (self.dbdir, id))
        item.name = id
        self.db[id] = item
        item.maxvals = [ [], [], [] ]
        for i in range(0,3):
            item.maxvals[i] = np.argpartition(item.hist[i], -MAXIMUMS_SIZE)[-MAXIMUMS_SIZE:]  # maximum
      
    
    #def Identify(self):
    #    #p = db.PetService().LoadByName('firulais') # not allowed
    #    p = db.PetService().LoadByName('neko') # allowed
    #    time.sleep(5)
    #    return p
    
    def camHandler_read(self):
        result = True
        img = cv2.imread(config.test_image)
        return result, img
        
    def GetPhoto(self, imgdata=None):
        
        fname = int(time.time())
        photo_path = db.PhotoPath(fname)
        dirpath = os.path.dirname(photo_path)
        
        # harcode this image, but save one from the camera in the right place

        if imgdata == None:
            result,img = self.camHandler.read()
            if not result:
                None
        else:
            img = imgdata  # use passed one
        
        if not os.path.exists(dirpath):
            os.makedirs(dirpath)
        
        cv2.imwrite(photo_path, img)
        shutil.copy(photo_path, config.last_image)
        logging.info("Photo taken into %s" % photo_path)
        
        return photo_path
        
    def Identify_OLD(self):
        # green color
        #hsvMin = numpy.array([44, 37, 99],numpy.uint8) # BGR
        #hsvMax = numpy.array([90, 255, 255],numpy.uint8) # BGR
        
        # move to config
        
        hsvMin = numpy.array([37, 43, 39],numpy.uint8) # BGR
        hsvMax = numpy.array([91, 255, 255],numpy.uint8) # BGR
        
        CountourArea = 100
        Coef = 0.04
        SHAPES_NEEDED = 4
        IDENTIFY_TIMEOUT= 5 #seconds
        CONFIDENCE=80 # percent
        MIN_SAMPLES=2
        time_start = time.time()

        #cv2.namedWindow('image')
        
        stats = {}
        photo = None
        
        while True:
            
            time_delta = time.time() - time_start
            #logging.info("Detecting Pet. Elapsed time: %3.2f/%3.2f "% (time_delta, IDENTIFY_TIMEOUT))
            
            if time_delta > IDENTIFY_TIMEOUT:
                
                if not stats:
                    return None,None
                
                #pet = db.PetService().LoadByShape(rshapes[0].shape)
                samples = 0
                for i in stats.keys(): 
                    samples += stats[i]
                max_key = max(stats, key=stats.get)   
                max_value = stats[max_key]
                
                if samples != 0.0: 
                    percent = (max_value * 100.0) / samples
                else:
                    percent = 0
                    
                #print max_key, max_value, percent    
                logging.info("Detect Timeout Expired %d secs. Calculating %d samples, %s shape %d count, %3.2f%% percent" %  (IDENTIFY_TIMEOUT, samples, max_key, max_value, percent))
                
                if percent >= CONFIDENCE and max_value >= MIN_SAMPLES:
                    return db.PetService().LoadByShape(max_key),photo
                
                return None,None
   
                
            result,img = self.camHandler.read()
            if not result:
                logging.info("Can't get image from CV2. Bailing out")
                return None,None
            
            output = img
            img = cv2.bilateralFilter(img,13,75,75)
            
            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            mask = cv2.inRange(hsv, hsvMin, hsvMax)
            #output = cv2.bitwise_and(img,img, mask= mask)
            
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
                    
            rshapes = cshapes[0:SHAPES_NEEDED]
            if len(rshapes) == SHAPES_NEEDED:   
                #for i in rshapes:
                #    cv2.drawContours(output, [i.c], -1, (0, 255, 0), 2)
                #    cv2.putText(output, i.shape, (i.center[0], i.center[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)    
                
                    
                    
                    #if rshapes[0].shape == "triangle": print "found Firulais"
                    #if rshapes[0].shape == "rectangle": print "found Neko"
                    #if rshapes[0].shape == "circle": print "found Eli"
                #print pet
                if rshapes[0].shape not in stats.keys():
                    stats[rshapes[0].shape]  = 1
                    if photo == None:
                        photo = self.GetPhoto(img)
                else:
                    stats[rshapes[0].shape] += 1
                
            
            #cv2.imshow('image',output)
            #if cv2.waitKey(33) & 0xFF == ord('q'):
            #    break
            
        return None,None
    
    
    
    
    
    
    #
    #
    # new identification mechanism. This is the one that works
    #
    # WEBCAM ID IDENTIFICATOR.
    #
    
    def Identify(self, verbose=True):
        
        self.Init()
        time_start = time.time()
       
        
        photo = None
        
        frame_counter = 0
        element = O()
        
        # to the configuration
        img = O()
    
            
        hist_3d =   np.array([ np.zeros([bins.Ac]), np.zeros([bins.Bc]), np.zeros([bins.Cc]) ])
        hist_3d_c = np.array([ np.zeros([bins.A]), np.zeros([bins.B]), np.zeros([bins.C]) ]) # clipped hist.
    
        while True:
            
            time_delta = time.time() - time_start
            #logging.info("Detecting Pet. Elapsed time: %3.2f/%3.2f "% (time_delta, config.IDENTIFY_TIMEOUT))
            
            if time_delta > config.IDENTIFY_TIMEOUT:
                if verbose:
                    logging.info("-" * 80)
                    logging.info("diff: %s" % row_max)
                    
                for item in self.status.keys():
                    value, frames, maxval = self.status[item]
                    p = (value * 100.0) / frame_counter
                    self.status[item][2] = max([self.status[item][2], p])
                    if verbose:
                        logging.info("[TM] %s->%.3f %% (%d frames, %d) max: %3.f%%" % (item, p, frame_counter, value, self.status[item][2]))
                    # useful for videos, but with cam, better count hits
                    # if p > config.PERCENT_MATCH and frames > config.FRAMES_MATCH:
                    if frames > config.FRAMES_MATCH:
                        #print "MATCH %s->%.3f %% (%d frames, %d) max: %3.f%%" % (item, p, frame_counter, value, self.status[item][2])
                        logging.info("[TM] MATCH_TIMEOUT %s->%.3f %% (%d frames, %d) max: %3.f%%" % (item, p, frame_counter, value, self.status[item][2]))
                        return db.PetService().LoadByName(item),photo               
           
                return None,None
   
            # get things here
            
            result,img.bgr = self.camHandler.read()
            if not result:
                return None,None
         
            img.roi = get_roi(img.bgr)
            img.chroma = remove_chroma(img.roi)
            img.chroma = kmeans_resize(img.chroma, KMEANS_IMAGE_SZ)
            #img.chroma = cv2.cvtColor(img.chroma, cv2.COLOR_BGR2HSV)
            #img.bgr = cv2.cvtColor(img.chroma, cv2.COLOR_HSV2BGR)
            #img.lab = cv2.cvtColor(img.chroma, cv2.COLOR_BGR2LAB)
            img.lab = cv2.cvtColor(img.chroma, cv2.COLOR_HSV2BGR)
            
            #cv2.imwrite('framedump-TEST/raw_%08d.png' % frame_counter, img.roi)
            
            hist = O()
            hist.A = cv2.calcHist([img.lab],[0],None,[bins.Ac],[0,bins.sz.A])
            hist.B = cv2.calcHist([img.lab],[1],None,[bins.Bc],[0,bins.sz.B])
            hist.C = cv2.calcHist([img.lab],[2],None,[bins.Cc],[0,bins.sz.C])
    
            hist_3d[0] = hist.A.reshape((bins.Ac))
            hist_3d[1] = hist.B.reshape((bins.Bc))
            hist_3d[2] = hist.C.reshape((bins.Cc))
    
            # clipping     
            for i in range(3):
                tmp = hist_3d[i][bins.clipping::]
                hist_3d_c[i] = tmp[0:-bins.clipping:]
                
            # normalize
            hist_3d_c = hist_3d_c.astype("float")
            s_val = hist_3d_c.sum()
            if s_val:
                hist_3d_c /= s_val   
        
            maxvals = []
            for i in range(3):
                max_array = np.argpartition(hist_3d_c[i], -MAXIMUMS_SIZE)[-MAXIMUMS_SIZE:]  # maximum
                maxvals.append(max_array)
            
            ## use the database in order to get the things.
            
            row_max = {}
            for item in self.db.keys():
                
                master = self.db[item]
                difference_maxvals = np.array(master.maxvals) - np.array(maxvals)
                # all sum
                #diff_val = np.abs(difference_maxvals).sum()
                # per channel
                diff_val = np.abs(difference_maxvals).sum(axis=1)
                row_max[item] = diff_val
               
            frame_counter += 1
           
            #print row_max
            key,value = min(row_max.items(), key=lambda k: k[1].min())
            # all sum
            #if value < 100:
            # per channel:
            if (value < [ 33, 33, 33]).all(): 
                self.status[key][0] += 1
                self.status[key][1] += 1
                # get only one.
                if photo == None:
                    photo = self.GetPhoto(img.bgr)
      
            #
            # check percent
            #
            
            if verbose:
                logging.info("-" * 80)
                logging.info("* diff: %s" % row_max)
                
            for item in self.status.keys():
                value, frames, maxval = self.status[item]
                p = (value * 100.0) / frame_counter
                self.status[item][2] = max([self.status[item][2], p])
                if verbose:
                    logging.info("* %s->%.3f %% (%d frames, %d) max: %3.f%%" % (item, p, frame_counter, value, self.status[item][2]))
                # useful for videos, but with cam, better count hits
                # if p > config.PERCENT_MATCH and frames > config.FRAMES_MATCH:
                if frames > config.FRAMES_MATCH:
                    #print "MATCH %s->%.3f %% (%d frames, %d) max: %3.f%%" % (item, p, frame_counter, value, self.status[item][2])
                    logging.info("MATCH %s->%.3f %% (%d frames, %d) max: %3.f%%" % (item, p, frame_counter, value, self.status[item][2]))
                    return db.PetService().LoadByName(item),photo
                
            # removed by putting it here.
            #if not verbose and frame_counter % 30 == 0:
            #    print "frame: ", frame_counter
            # if FRAME_LIMIT and frame_counter > FRAME_LIMIT:
            #    break

        #
        # END LOOP.
        # if we are near the max ... we are the max.
        #
        return None,None
    
        
    def Setup(self, videoport=True):
        
        if IsRaspberry():
            from cameratools import PiCameraHandler
            self.camHandler = PiCameraHandler(resolution=(config.camera.width,config.camera.height), 
                                              framerate=config.camera.fps, 
                                              rotation=config.camera.rotation,videoport=videoport)
            logging.info("Detector: Using Raspberry Camera")
        else:
  

            self.camHandler = cv2.VideoCapture(0)
            self.camHandler.set(cv2.CAP_PROP_FRAME_WIDTH, config.camera.width)
            self.camHandler.set(cv2.CAP_PROP_FRAME_HEIGHT, config.camera.height)
            self.camHandler.set(cv2.CAP_PROP_FPS, config.camera.fps)
            
            if not self.camHandler.isOpened():
                logging.info("Detector: error: Can't open video capture cam. Starting Mockup")
                #sys.exit(1)
                
                self.camHandler = config.O()
                self.camHandler.read = self.camHandler_read
                
                
            logging.info("Detector: Using Generic Webcam")

        # move this to CONFIG.
        for item in config.CAT_DB_ITEMS:
            self.Load("%s" % item)
        self.Init()


#
# detector implementation
#
#Detector = DetectorMock
Detector = DetectorCV2
instance = None



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

