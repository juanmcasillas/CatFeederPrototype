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


from kmeantools import *



class Detector:
    def __init__(self):
        self.db = {}
        self.status = {}
        self.dbdir = 'videos'

    def Info(self):
        for i in self.db.keys():
            item = self.db[i]
            print "-- %s --- " % (i)
            print "Histogram"
            print item.hist
        
    def Init(self):
        self.status = {}
        for i in self.db.keys():
            self.status[i] = [0.0, 0]
                
        
    def Load(self, id):
        item = O()
        item.hist = np.load("%s/%s_hist.npy" % (self.dbdir, id))
        item.centers = np.load("%s/%s_centers.npy" % (self.dbdir, id))
        item.name = id
        self.db[id] = item
    
    
    def Identify(self, video, verbose=False):
        
    
        cap = cv2.VideoCapture("%s" % video)

        frame_counter = 0
        element = O()
    
        #scores
    
        while True:
            result,img = cap.read()
            if not result:
                break
            
            image = get_roi(img)
            image = remove_chroma(image)
            image = kmeans_resize(image, 100)
            image_nobg = kmeans_remove_bg(image)
            
            
            # opencv2 k-means cluster.
            
            hist,labels,centers = do_KMEANS(image_nobg, KCOLORS)
    
            frame_counter += 1
            
            element.hist = hist
            element.centers = centers
            element.name = video
            
            ## use the database in order to get the things.
            
            for item in self.db.keys():
                
                master = self.db[item]
                    
                distance_master = kmeans_distance_master(element.hist, element.centers, master.hist, master.centers)
          
                local_matches = 0
          
                for i in range(len(distance_master)):
                    delta_e, col_i, col_j, j, percent = distance_master[i]
                    if delta_e <= DELTA_E_RANGE:
                        local_matches += 1
 
                # this matches the minimum required number of colors to match.
                
                min_colors = int((len(master.centers) - NUM_IGNORE_COLORS) / 2.0)
                               
                if  local_matches >= min_colors:
                    self.status[item][0] += 1
                    self.status[item][1] += 1
                    
     
            #
            # check percent
            #
            
            if verbose:
                print "-" * 80
            for item in self.status.keys():
                value, frames = self.status[item]
                
                p = (value * 100.0) / frame_counter
                if verbose:
                    print "%s->%.3f %% (%d frames, %d)" % (item, p, frame_counter, value)
                if p > PERCENT_MATCH and frames > FRAMES_MATCH:
                    print "MATCH %s->%.3f %% (%d frames, %d)" % (item, p, frame_counter, value)
                    return item
                
            
            
            if not verbose and frame_counter % 30 == 0:
                print "frame: ", frame_counter
            if FRAME_LIMIT and frame_counter > FRAME_LIMIT:
                break
            
    
    
        #
        # END LOOP.
        
        return None


    
    
if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help="run metrics", action="store_true")
    parser.add_argument('input', nargs='+')
    args = parser.parse_args()    
        
    detector = Detector()
    
    for item in [ 'firulais','neko', 'eli' ]:
        detector.Load("%s" % item)
    
    detector.Init()
   
    
    for video in args.input:
        start_time = time.time()
        result = detector.Identify(video, args.verbose)
        end_time = time.time()-start_time
        print "%s is %s [%.3f seconds]" % (video, result, end_time)
        
        
        