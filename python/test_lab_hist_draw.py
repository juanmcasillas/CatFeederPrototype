import cv2
import argparse
import numpy as np
import matplotlib
#matplotlib.use('Agg')

from matplotlib import pyplot as plt
import glob
from numpy import nan
import math
import os


from kmeantools import *


def TEST_ELEMENTS(Master, Element,  CV_MODE, verbose=True, drawit=False):
    """
    Master: name of the master element to check against (e.g. videos/firulais)
    Element: Data to test (e.g. videos/firulais)
    """
    
    OPENCV_METHODS = {
                      "correlation": cv2.HISTCMP_CORREL,        # bigger better
                      "chi-squared": cv2.HISTCMP_CHISQR,
                      "intersection": cv2.HISTCMP_INTERSECT,    # bigger better
                      "bhattacharyya": cv2.HISTCMP_BHATTACHARYYA
        }  
    
    CV_MODE_TYPE = OPENCV_METHODS[CV_MODE]
    
    # load things
    MAXIMUM_SIZE = 2
    
    master = O()
    master.hist = np.load("%s_hist.npy" % Master)
    master.pngfile = "%s.png" % Master
    master.hist_img = cv2.imread(master.pngfile)
    master.hist_img = cv2.cvtColor(master.hist_img, cv2.COLOR_BGR2RGB)
    master.name = os.path.basename(Master)
    master.maxvals = [ [], [], [] ]
    for i in range(0,3):
        master.maxvals[i] = np.argpartition(master.hist[i], -MAXIMUM_SIZE)[-MAXIMUM_SIZE:]  # maximum
            
   
            
    
    cap = cv2.VideoCapture("%s.h264" % Element)

    frame_counter = 0
    
    element = O()
    element.name = os.path.basename(Element)
    
    #scores
    matched_frames = 0
    matched_avg = 0.0
    
    nonmatched_frames = 0
    nonmatched_avg = 0.0

    img = O()
    bins = O()
    bins.clipping = 10
    bins.A = 128 
    bins.B = 128 
    bins.C = 128 
    bins.Ac = 128 + (bins.clipping * 2)
    bins.Bc = 128 + (bins.clipping * 2)
    bins.Cc = 128 + (bins.clipping * 2)
    bins.sz = O()
    bins.sz.A = 255
    bins.sz.B = 255
    bins.sz.C = 255

    frame_counter = 0
    colors = []
    hist_3d =   np.array([ np.zeros([bins.Ac]), np.zeros([bins.Bc]), np.zeros([bins.Cc]) ])
    hist_3d_c = np.array([ np.zeros([bins.A]), np.zeros([bins.B]), np.zeros([bins.C]) ]) # clipped hist.

    master.testhist = O()
    master.testhist.A =  master.hist[0].astype(np.float32,casting='unsafe',copy=False)
    master.testhist.B =  master.hist[1].astype(np.float32,casting='unsafe',copy=False)
    master.testhist.C =  master.hist[2].astype(np.float32,casting='unsafe',copy=False)
        
    print Master, "vs", Element
    
    while True:
        result,img.bgr = cap.read()
        if not result:
            break

        
        img.roi = get_roi(img.bgr)
        img.chroma = remove_chroma(img.roi)
        #image = kmeans_resize(image, KMEANS_IMAGE_SZ)
        #image_nobg = kmeans_remove_bg(image)
        
        # get the image, convert to LAB and build the histogram. Then normalize it.
        
        img.lab = cv2.cvtColor(img.chroma, cv2.COLOR_BGR2LAB)
    
        hist = O()
        hist.A = cv2.calcHist([img.lab],[0],None,[bins.Ac],[0,bins.sz.A])
        hist.B = cv2.calcHist([img.lab],[1],None,[bins.Bc],[0,bins.sz.B])
        hist.C = cv2.calcHist([img.lab],[2],None,[bins.Cc],[0,bins.sz.C])

        hist_3d[0] = hist.A.reshape((bins.Ac))
        hist_3d[1] = hist.B.reshape((bins.Bc))
        hist_3d[2] = hist.C.reshape((bins.Cc))

        plt_labels = []
        plt_colors = []
        plt_data = []
        
        ##----------------------------------------------------------------------
        #
        # now plot things
        # 

        if True:
            for i in range(3):
                tmp = hist_3d[i][bins.clipping::]
                hist_3d_c[i] = tmp[0:-bins.clipping:]
                
        #normalize
        hist_3d_c = hist_3d_c.astype("float")
        hist_3d_c /= hist_3d_c.sum()  
    
        #element.testhist = O()
        #element.testhist.A =  hist_3d_c[0].astype(np.float32,casting='unsafe',copy=False)
        #element.testhist.B =  hist_3d_c[1].astype(np.float32,casting='unsafe',copy=False)
        #element.testhist.C =  hist_3d_c[2].astype(np.float32,casting='unsafe',copy=False)
        
        #distance = O()
       
        #distance.A = cv2.compareHist(master.testhist.A, element.testhist.A, CV_MODE_TYPE)
        #distance.B = cv2.compareHist(master.testhist.B, element.testhist.B, CV_MODE_TYPE)
        #distance.C = cv2.compareHist(master.testhist.C, element.testhist.C, CV_MODE_TYPE)
    
        #if 1 - distance.A < 0.3 and 1 - distance.B < 0.002 and 1 - distance.C < 0.02:
        #print frame_counter, distance.A, distance.B, distance.C
    
    
        maximums = []
    
        for i in range(3):
            max_array = np.argpartition(hist_3d_c[i], -MAXIMUM_SIZE)[-MAXIMUM_SIZE:]  # maximum
            maximums.append(max_array)
    
        difference = np.array(master.maxvals) - np.array(maximums)
        if False:
            print "-master-"
            print np.array(master.maxvals) 
            print "-local-"
            print np.array(maximums)
            print "-diference-"
            print difference
        print np.abs(difference).sum()
        
    
        # plot
    
        series = { 'A': ['r', 'Lab'], 'B': ['g','A'], 'C': ['b', 'B'] }
        l_handles = []
        
        f, plots = plt.subplots(3, sharex=True, sharey=True)
        plots[0].set_title('Histogram LAB')
        
      
        maximums = []
    
        for i,serie in enumerate(('A','B','C')):
    
            col = series[serie][0]
            tit = series[serie][1]
            
            ind = np.arange(len(hist_3d_c[i]))
            #h = plots[i].bar(ind, hist_3d_m[i], color="#cacaca", label=tit)
            plots[i].plot(hist_3d_c[i], color=col, label=tit, linewidth=1.2)
            
            max_array = np.argpartition(hist_3d_c[i], -MAXIMUM_SIZE)[-MAXIMUM_SIZE:]  # maximum
            maximums.append(max_array)
            
            for am in max_array:
                plots[i].axvline(am, color='#9E7a7a', linestyle='dashed', linewidth=1.0)
            
            plots[i].set_title(tit,loc='right',fontsize=10)
            plots[i].grid(True)
        
        
        f.subplots_adjust(hspace=0)
        plt.setp([a.get_xticklabels() for a in f.axes[:-1]], visible=False)
    
                     
        element.hist_img = Plot2Img(plt)
        plt.close('all')

        # stupid check
       
        
        

        #cv2.imshow('image', cv2.cvtColor(element.hist_img, cv2.COLOR_RGB2BGR))
        #if cv2.waitKey(33) & 0xFF==ord('q'):
        #    break
        
        img_output = ComposeImage(topleft=cv2.cvtColor(img.chroma, cv2.COLOR_HSV2BGR), 
                                  topright=cv2.cvtColor(element.hist_img, cv2.COLOR_RGB2BGR), 
                                  bottomleft=cv2.cvtColor(master.hist_img, cv2.COLOR_RGB2BGR),
                                  #bottomright=cv2.cvtColor(distance_master_img, cv2.COLOR_RGB2BGR)
                                  )

        
        dirpath = 'framedump-%s-%s' % (master.name,element.name)
        if not os.path.exists(dirpath):
            os.makedirs(dirpath)
        fname = '%s/frame_%08d.png' % (dirpath, frame_counter)
        ##cv2.imwrite(fname, img_output )
        plt.close('all')

        #if frame_counter % 30 == 0:
        #        print "frame: ", frame_counter
        if FRAME_LIMIT and frame_counter > FRAME_LIMIT:
            break
        
        frame_counter += 1
  

    #
    # END LOOP.

   





if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--element", help="Histogram", action="store")  
    parser.add_argument("-v", "--verbose", help="run metrics", action="store_true")
    parser.add_argument("-f", "--function", help="CV method function", action="store", default="bhattacharyya")
    args = parser.parse_args()    
    
    METHOD = 'correlation'    #bigger, better
    #METHOD = 'intersection'  #bigger, better
    #METHOD = 'bhattacharyya'
    #METHOD = 'chi-squared'

    # build the CSV matrix.
    #ROWS = [ 'neko', 'neko2', 'neko3', 'eli', 'firulais', 'firulais2', 'firulais3', 'blue_ball', 'red_jar', 'hand', 'empty']
    #COLS = [ 'neko', 'neko2', 'neko3', 'eli', 'firulais', 'firulais2', 'firulais3'] 
    #COEFS = { 'neko': [0.762,0.605,0.905], 'eli': [0.764,0.764,0.764], 'firulais': [0.502,0.224,0.821] } #correlation mode, bigger, better
    
    #ROWS = [ 'neko', 'neko2', 'eli', 'eli2', 'firulais', 'firulais2', 'blue_ball', 'red_jar', 'hand' ]
    #COLS = [ 'neko', 'neko2', 'eli', 'eli2', 'firulais', 'firulais2', 'blue_ball', 'red_jar', 'hand' ]
    
    #ROWS = [ 'blue_ball' ]
    #COLS = [ 'blue_ball' ]
    
    #ROWS = [ 'firulais','neko', 'eli', 'red_jar', ]
    ROWS = [ 'hand','empty', 'blue_ball', 'red_jar' ]
    COLS = [ 'eli' ]
        
    for r in range(len(ROWS)):
        for c in range(len(COLS)):
            TEST_ELEMENTS("%s/%s" % (DB_DIR,ROWS[r]), "%s/%s" % (DB_DIR,COLS[c]), METHOD, verbose=args.verbose)
            #frame_counter,matched_frames,avg, percent = TEST_ELEMENTS("videos/%s" % ROWS[r], "videos/%s" % COLS[c], METHOD, verbose=args.verbose)
            #print "%s vs %s %.3f%% %d/%d matched/total %.3f avg" % (ROWS[r], COLS[c], percent, matched_frames, frame_counter, avg) 
            
        print ""