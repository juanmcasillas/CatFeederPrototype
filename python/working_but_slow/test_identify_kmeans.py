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
        item.centers = np.load("%s/%s_centers.npy" % (self.dbdir, id))
        item.colors = PrepareMasterColors(item.centers)
        item.name = id
        self.db[id] = item
        
        return
        # NOT REACHED.
        # not load the overhaul cache. (too big to work fine)
        
        cache_fname = "%s/%s_cache.pickle" % (self.dbdir, id)
        if os.path.exists(cache_fname):
            DELTA_E_CACHE.LoadAndAppend(cache_fname)
    
    
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
            image = kmeans_resize(image, KMEANS_IMAGE_SZ)
            image_nobg = kmeans_remove_bg(image)
            
            # opencv2 k-means cluster.
            
            hist,centers = do_KMEANS(image_nobg, KCOLORS)
    
            frame_counter += 1
            
            element.hist = hist
            element.centers = centers
            element.name = video
            
            ## use the database in order to get the things.
            
            for item in self.db.keys():
                
                master = self.db[item]
                    
                #distance_master = kmeans_distance_master(element.hist, element.centers, master.hist, master.centers)
                distance_master = kmeans_distance_master(element.centers, master.colors, master.hist)
                
                local_matches = 0
          
                for i in range(len(distance_master)):
                    delta_e = distance_master[i][0]
                    if delta_e <= DELTA_E_RANGE:
                        local_matches += 1
 
                # this matches the minimum required number of colors to match.
                
                min_colors = int((len(master.colors) - NUM_IGNORE_COLORS) / 2.0)
                               
                if  local_matches >= min_colors:
                    self.status[item][0] += 1
                    self.status[item][1] += 1

     
            #
            # check percent
            #
            
            if verbose:
                print "-" * 80
            
            for item in self.status.keys():
                value, frames, maxval = self.status[item]
                p = (value * 100.0) / frame_counter
                self.status[item][2] = max([self.status[item][2], p])
                if verbose:
                    print "%s->%.3f %% (%d frames, %d) max: %3.f%%" % (item, p, frame_counter, value, self.status[item][2])
                if p > PERCENT_MATCH and frames > FRAMES_MATCH:
                    #print "MATCH %s->%.3f %% (%d frames, %d) max: %3.f%%" % (item, p, frame_counter, value, self.status[item][2])
                    return item,p
                
            
            
            if not verbose and frame_counter % 30 == 0:
                print "frame: ", frame_counter
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
    parser.add_argument("-v", "--verbose", help="run metrics", action="store_true")
    parser.add_argument('input', nargs='+')
    args = parser.parse_args()    
        
    detector = Detector()
    
    for item in [ 'firulais','neko', 'eli' ]:
        detector.Load("%s" % item)
    
    detector.Init()
   
    
    for video in args.input:
        start_time = time.time()
        result, percent = detector.Identify(video, args.verbose)
        end_time = time.time()-start_time
        print "%s is %s %.3f %% [%.3f seconds]" % (video, result, percent, end_time)
        
    print "Cache Stats Totals: %d, Hits: %d " % (DELTA_E_CACHE.asks, DELTA_E_CACHE.hits)
        