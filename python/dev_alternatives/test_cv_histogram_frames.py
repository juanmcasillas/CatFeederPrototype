import cv2
import argparse
import numpy as np
from matplotlib import pyplot as plt
import glob
from numpy import nan
import math







def RUN_TEST_MATCH(element,testdir, CV_MODE, verbose=True):

    OPENCV_METHODS = {
                      "correlation": cv2.HISTCMP_CORREL,        # bigger better
                      "chi-squared": cv2.HISTCMP_CHISQR,
                      "intersection": cv2.HISTCMP_INTERSECT,    # bigger better
                      "bhattacharyya": cv2.HISTCMP_BHATTACHARYYA
        }  
    
    CV_MODE_TYPE = OPENCV_METHODS[CV_MODE]
  
    bins_h = 180
    bins_s = 256
    bins_v = 256
    
    base_histogram = np.load(element)
    hist_3d =   np.array([ np.zeros([bins_h,1]), np.zeros([bins_s,1]), np.zeros([bins_v,1]) ])
    #base_histogram[0].dtype = np.float32
    #base_histogram[1].dtype = np.float32
    #base_histogram[2].dtype = np.float32
    #base_histogram.dtype = np.float32
        
    #base_histogram[0] = base_histogram[0].astype(np.float32, copy=False)
    #base_histogram[1] = base_histogram[1].astype(np.float32, copy=False)
    #base_histogram[2] = base_histogram[2].astype(np.float32, copy=False)
        
    avg = 0.0
    counter = 0
    nan_frames = 0
    matches = 0
    
    hsvMin = np.array([25, 43, 0],np.uint8) # BGR green box
    hsvMax = np.array([91, 255, 255],np.uint8) # BGR green box
  
    for imagePath in glob.glob(testdir + "/*.png"):
        # extract the image filename (assumed to be unique) and
        # load the image, updating the images dictionary
        filename = imagePath[imagePath.rfind("/") + 1:]
        
        img = cv2.imread(imagePath)
        
        img_roi = img[30:608, 30:600] # ROI. Was rotated!!
        #hsv = cv2.cvtColor(img_roi, cv2.COLOR_BGR2HSV)
        
        img_roi = cv2.bilateralFilter(img_roi,13,75,75)
        img_roi = cv2.cvtColor(img_roi, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(img_roi, hsvMin, hsvMax)
        _, mask = cv2.threshold(mask,20, 255, cv2.THRESH_BINARY_INV)
        kernel = np.ones((5,5),np.uint8)
        mask = cv2.erode(mask, kernel, iterations=2)
        hsv = cv2.bitwise_and(img_roi,img_roi,mask= mask)
        # leave it as hsv
        #hsv = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR) # to bgr
        
        #cv2.imshow('image', hsv)
        #cv2.waitKey(5)
        
        hist_3d[0] = cv2.calcHist([hsv],[0],None,[bins_h],[0,bins_h])
        hist_3d[1] = cv2.calcHist([hsv],[1],None,[bins_s],[0,bins_s])
        hist_3d[2] = cv2.calcHist([hsv],[2],None,[bins_v],[0,bins_v])
    
        cv2.normalize(hist_3d[0],hist_3d[0],0,bins_h,cv2.NORM_MINMAX)
        cv2.normalize(hist_3d[1],hist_3d[1],0,bins_s,cv2.NORM_MINMAX)
        cv2.normalize(hist_3d[2],hist_3d[2],0,bins_v,cv2.NORM_MINMAX)

        a1 =  base_histogram[0].astype(np.float32,casting='unsafe',copy=False)
        a2 =  base_histogram[1].astype(np.float32,casting='unsafe',copy=False)
        a3 =  base_histogram[2].astype(np.float32,casting='unsafe',copy=False)
        
        b1 =  hist_3d[0].astype(np.float32,casting='unsafe',copy=False)
        b2 =  hist_3d[1].astype(np.float32,casting='unsafe',copy=False)
        b3 =  hist_3d[2].astype(np.float32,casting='unsafe',copy=False)
        
        #print base_histogram[0].shape, hist_3d[0].shape
        #print type(base_histogram[0][0][0]), type(hist_3d[0][0][0])
        #print a1.shape, type(a1[0][0])
        
        #d_h = cv2.compareHist(base_histogram[0], hist_3d[0], CV_MODE_TYPE)
        #d_s = cv2.compareHist(base_histogram[1], hist_3d[1], CV_MODE_TYPE)
        #d_v = cv2.compareHist(base_histogram[2], hist_3d[2], CV_MODE_TYPE)
       
        d_h = cv2.compareHist(a1, b1, CV_MODE_TYPE)
        d_s = cv2.compareHist(a2, b2, CV_MODE_TYPE)
        d_v = cv2.compareHist(a3, b3, CV_MODE_TYPE)
        
        if not math.isnan(d_v):
            # if real value, add to the average, else skip.
            #d_v = 1.0
            #d_m = (d_h + d_s + d_v) / 3.0
            match = False
            h_delta = 300
            s_delta = 400
            v_delta = 400
            
            #intersection
            h_delta = 180
            s_delta = 250
            v_delta = 250
            
            #correlation
            #h_delta = 0.9
            #s_delta = 0.9
            #v_delta = 0.9
            
            #print("%s vs %s (%s) D(H,S,V,m)  Matches: %s : (%3.2f,%3.2f,%3.2f)" % (imagePath, element, CV_MODE, match, d_h, d_s, d_v))
            if d_h > h_delta and d_s > s_delta and d_v > v_delta: 
                match = True
                matches += 1
                #print("%s vs %s (%s) D(H,S,V,m)  Matches: %s : (%3.2f,%3.2f,%3.2f)" % (imagePath, element, CV_MODE, match, d_h, d_s, d_v))
        else:
            match = False
            nan_frames +=1

        counter += 1 


    percent = 0.0
    if counter > 0:
        percent = (matches*100.0/counter)
                
    print "Matches: (%s vs %s) %d/%d %d%%" % (testdir, element, matches, counter, percent)




if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--element", help="Histogram", action="store")  
    parser.add_argument("-t", "--test", help="dir for test", action="store")
    parser.add_argument("-v", "--verbose", help="run metrics", action="store_true")
    parser.add_argument("-f", "--function", help="CV method function", action="store", default="bhattacharyya")
    args = parser.parse_args()    
    
    METHOD = 'correlation'
    METHOD = 'intersection'

    # build the CSV matrix.
    #ROWS = [ 'neko', 'neko2', 'neko3', 'eli', 'firulais', 'firulais2', 'firulais3', 'blue_ball', 'red_jar', 'hand', 'empty']
    #COLS = [ 'neko', 'neko2', 'neko3', 'eli', 'firulais', 'firulais2', 'firulais3'] 
    #COEFS = { 'neko': [0.762,0.605,0.905], 'eli': [0.764,0.764,0.764], 'firulais': [0.502,0.224,0.821] } #correlation mode, bigger, better
    
    ROWS = [ 'neko', 'neko2', 'eli', 'eli2', 'firulais', 'firulais2', 'blue_ball', 'red_jar', 'hand', 'empty']
    COLS = [ 'neko', 'neko2', 'eli', 'eli2', 'firulais', 'firulais2', 'blue_ball', 'red_jar', 'hand', 'empty'] 
        
    for r in range(len(ROWS)):
        for c in range(len(COLS)):
            
            avg= RUN_TEST_MATCH("videos/%s.npy" % COLS[c], "framedump-%s" % ROWS[r], METHOD, verbose=args.verbose)
            