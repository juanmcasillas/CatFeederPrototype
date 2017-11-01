import cv2
import argparse
import numpy as np
import matplotlib
matplotlib.use('Agg')

from matplotlib import pyplot as plt
import glob
from numpy import nan
import math
import os
import time

# raspy conf
import sys
import logging
import config
from check_pi import *

from kmeantools import *

class Detector:
    def __init__(self):
        self.db = {}
        self.status = {}
        self.dbdir = DB_DIR

    def Info(self):
        for i in self.db.keys():
            item = self.db[i]
            print "-- %s --- " % (i)
            print "Histogram"
            print item.hist
        
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
      
        return
    
    def Identify(self, video, verbose=False,videoport=True):
        
        if video == None:
            if IsRaspberry():
                from cameratools import PiCameraHandler
                cap = PiCameraHandler(resolution=(config.camera.width,config.camera.height), 
                                                  framerate=config.camera.fps, 
                                                  rotation=config.camera.rotation,videoport=videoport)
                logging.info("Detector: Using Raspberry Camera")
            else:
      
                cap= cv2.VideoCapture(0)
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.camera.width)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.camera.height)
                cap.set(cv2.CAP_PROP_FPS, config.camera.fps)
                
                if not cap.isOpened():
                    logging.info("Detector: error: Can't open video capture cam. Bailing out")
                    sys.exit(1)
                    
                logging.info("Detector: Using Generic Webcam")
        else:
            # open video file
            cap = cv2.VideoCapture("%s" % video)

        frame_counter = 0
        element = O()
    
        # to the configuration
        img = O()

        
        hist_3d =   np.array([ np.zeros([bins.Ac]), np.zeros([bins.Bc]), np.zeros([bins.Cc]) ])
        hist_3d_c = np.array([ np.zeros([bins.A]), np.zeros([bins.B]), np.zeros([bins.C]) ]) # clipped hist.
    
        #scores
    
        while True:
            result,img.bgr = cap.read()
            if not result:
                break
         
        
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
                
                
            
            #
            # check percent
            #
           
            
            if verbose:
                print "-" * 80
                #print "diff: ", row_max
           
                
            for item in self.status.keys():
                value, frames, maxval = self.status[item]
                p = (value * 100.0) / frame_counter
                self.status[item][2] = max([self.status[item][2], p])
                if verbose:
                    print "%s->%.3f %% (%d frames, %d) max: %3.f%%" % (item, p, frame_counter, value, self.status[item][2])
                # useful for videos, but with cam, better count hits
                # if p > PERCENT_MATCH and frames > FRAMES_MATCH:
                if frames > FRAMES_MATCH:
                    #print "MATCH %s->%.3f %% (%d frames, %d) max: %3.f%%" % (item, p, frame_counter, value, self.status[item][2])
                    return item,p
                
            
            #if not verbose and frame_counter % 30 == 0:
            #    print "frame: ", frame_counter
            if FRAME_LIMIT and frame_counter > FRAME_LIMIT:
                break
            
            
    
        #
        # END LOOP.
        # if we are near the max ... we are the max.
        #
      
        key,value = max(self.status.items(), key=lambda k: k[1])
        
        max_val = value[2]
        if max_val + PERCENT_MATCH_THRESHOLD >= PERCENT_MATCH:
            "threshold matched, returning %s [%.3f%%]" % (key, max_val)
            return key, max_val
        
        return None,0.0
    
    



if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help="Show data", action="store_true")
    parser.add_argument('input', nargs='*')
    args = parser.parse_args()    
        
    detector = Detector()
    
    for item in [ 'firulais','neko', 'eli' ]:
        detector.Load("%s" % item)
    
    detector.Init()
   
    if len(args.input) > 0:
        # process video files
        for video in args.input:
            start_time = time.time()
            result, percent = detector.Identify(video, args.verbose)
            end_time = time.time()-start_time
            print "%s is %s %.3f %% [%.3f seconds]" % (video, result, percent, end_time)
    else:
        # from webcam
        start_time = time.time()
        result, percent = detector.Identify(None, args.verbose)
        end_time = time.time()-start_time
        print "%s is %s %.3f %% [%.3f seconds]" % ("-webcam-", result, percent, end_time)
  
    
