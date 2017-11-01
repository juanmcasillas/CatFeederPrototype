import cv2
import argparse
import numpy as np
from matplotlib import pyplot as plt
import glob
from numpy import nan
import math
import os
import PIL
from cStringIO import StringIO




def savitzky_golay(y, window_size, order, deriv=0, rate=1):
    r"""Smooth (and optionally differentiate) data with a Savitzky-Golay filter.
    The Savitzky-Golay filter removes high frequency noise from data.
    It has the advantage of preserving the original shape and
    features of the signal better than other types of filtering
    approaches, such as moving averages techniques.
    Parameters
    ----------
    y : array_like, shape (N,)
        the values of the time history of the signal.
    window_size : int
        the length of the window. Must be an odd integer number.
    order : int
        the order of the polynomial used in the filtering.
        Must be less then `window_size` - 1.
    deriv: int
        the order of the derivative to compute (default = 0 means only smoothing)
    Returns
    -------
    ys : ndarray, shape (N)
        the smoothed signal (or it's n-th derivative).
    Notes
    -----
    The Savitzky-Golay is a type of low-pass filter, particularly
    suited for smoothing noisy data. The main idea behind this
    approach is to make for each point a least-square fit with a
    polynomial of high order over a odd-sized window centered at
    the point.
    Examples
    --------
    t = np.linspace(-4, 4, 500)
    y = np.exp( -t**2 ) + np.random.normal(0, 0.05, t.shape)
    ysg = savitzky_golay(y, window_size=31, order=4)
    import matplotlib.pyplot as plt
    plt.plot(t, y, label='Noisy signal')
    plt.plot(t, np.exp(-t**2), 'k', lw=1.5, label='Original signal')
    plt.plot(t, ysg, 'r', label='Filtered signal')
    plt.legend()
    plt.show()
    References
    ----------
    .. [1] A. Savitzky, M. J. E. Golay, Smoothing and Differentiation of
       Data by Simplified Least Squares Procedures. Analytical
       Chemistry, 1964, 36 (8), pp 1627-1639.
    .. [2] Numerical Recipes 3rd Edition: The Art of Scientific Computing
       W.H. Press, S.A. Teukolsky, W.T. Vetterling, B.P. Flannery
       Cambridge University Press ISBN-13: 9780521880688
    """
    import numpy as np
    from math import factorial
    
    try:
        window_size = np.abs(np.int(window_size))
        order = np.abs(np.int(order))
    except ValueError, msg:
        raise ValueError("window_size and order have to be of type int")
    if window_size % 2 != 1 or window_size < 1:
        raise TypeError("window_size size must be a positive odd number")
    if window_size < order + 2:
        raise TypeError("window_size is too small for the polynomials order")
    order_range = range(order+1)
    half_window = (window_size -1) // 2
    # precompute coefficients
    b = np.mat([[k**i for i in order_range] for k in range(-half_window, half_window+1)])
    m = np.linalg.pinv(b).A[deriv] * rate**deriv * factorial(deriv)
    # pad the signal at the extremes with
    # values taken from the signal itself
    firstvals = y[0] - np.abs( y[1:half_window+1][::-1] - y[0] )
    lastvals = y[-1] + np.abs(y[-half_window-1:-1][::-1] - y[-1])
    y = np.concatenate((firstvals, y, lastvals))
    return np.convolve( m[::-1], y, mode='valid')



def RUN_TEST_MATCH_VIDEO(histogram,max_histogram, video, CV_MODE, verbose=True):

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
    
    bins_h = 128
    bins_s = 128
    bins_v = 128
    
    base_histogram = np.load(histogram)
    maximums_histogram = np.load(max_histogram)
   
    hist_3d   =   np.array([ np.zeros([bins_h]), np.zeros([bins_s]), np.zeros([bins_v]) ])
    hist_3d_s =   np.array([ np.zeros([bins_h]), np.zeros([bins_s]), np.zeros([bins_v]) ])
        
    avg = 0.0
    counter = 0
    matches = 0
    
    
    hsvMin = np.array([25, 43, 0],np.uint8) # BGR green box
    hsvMax = np.array([91, 255, 255],np.uint8) # BGR green box
  
    cap = cv2.VideoCapture(video)
   
    
    #print "Building histograms for  H(%s) video %s" % (histogram, video)
    score_avg = 0.0
    position = None
    
    while True:
        result,img = cap.read()
        if not result:
            break
        
        img_roi = img[30:608, 30:600] # ROI. Was rotated!!
       
        img_roi = cv2.cvtColor(img_roi, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(img_roi, hsvMin, hsvMax)
        _, mask = cv2.threshold(mask,20, 255, cv2.THRESH_BINARY_INV)
        kernel = np.ones((5,5),np.uint8)
        mask = cv2.erode(mask, kernel, iterations=2)
        hsv = cv2.bitwise_and(img_roi,img_roi,mask= mask)
        
        h = cv2.calcHist([hsv],[0],None,[bins_h],[0,bins_h])
        s = cv2.calcHist([hsv],[1],None,[bins_s],[0,bins_s])
        v = cv2.calcHist([hsv],[2],None,[bins_v],[0,bins_v])
    
        hist_3d[0] = h.reshape((bins_h))
        hist_3d[1] = s.reshape((bins_s))
        hist_3d[2] = v.reshape((bins_v))
    
        # clear borders
        border_size = 10
        for i in range(3):
            if i == 0:
                hist_3d[i][0:border_size] = 0.0
                hist_3d[i][bins_h-1-border_size:bins_h-1] = 0.0
            else:
                hist_3d[i][0:border_size] = 0.0
                hist_3d[i][bins_s-1-border_size:bins_s-1] = 0.0
        
        # remove too bright and too dark frames
        #max_array_s = np.argpartition(hist_3d[1], -1)[-1:]
        #max_array_v = np.argpartition(hist_3d[2], -1)[-1:]
        #if max_array_s[0] < 20 or max_array_s[0] > 120 or \
        #    max_array_v[0] < 20 or max_array_v[0] > 120:
        #    counter += 1
        #    continue      
       

        
        cv2.normalize(hist_3d[0],hist_3d[0],0,bins_h,cv2.NORM_MINMAX)
        cv2.normalize(hist_3d[1],hist_3d[1],0,bins_s,cv2.NORM_MINMAX)
        cv2.normalize(hist_3d[2],hist_3d[2],0,bins_v,cv2.NORM_MINMAX)

                

                
        hist_3d_s[0] = savitzky_golay(hist_3d[0], 41, 3) # window size 51, polynomial order 3 / 21-9 / 21 -13
        hist_3d_s[1] = savitzky_golay(hist_3d[1], 41, 3) # window size 51, polynomial order 3
        hist_3d_s[2] = savitzky_golay(hist_3d[2], 41, 3) # window size 51, polynomial order 3
    

        #a1 =  base_histogram[0].astype(np.float32,casting='unsafe',copy=False)
        #a2 =  base_histogram[1].astype(np.float32,casting='unsafe',copy=False)
        #a3 =  base_histogram[2].astype(np.float32,casting='unsafe',copy=False)
        
        #b1 =  hist_3d_s[0].astype(np.float32,casting='unsafe',copy=False)
        #b2 =  hist_3d_s[1].astype(np.float32,casting='unsafe',copy=False)
        #b3 =  hist_3d_s[2].astype(np.float32,casting='unsafe',copy=False)
        
        #d_h = cv2.compareHist(a1, b1, CV_MODE_TYPE)
        #d_s = cv2.compareHist(a2, b2, CV_MODE_TYPE)
        #d_v = cv2.compareHist(a3, b3, CV_MODE_TYPE)
        
        #print "-" * 80
        #print d_h
        #print d_s
        #print d_v
        
        
        MAXIMUM_SIZE = 3
        maximums = []
        maximums_values = [0.0] * 3 # each channel
        hdist = [ 0.0 ] * (MAXIMUM_SIZE*2)
        diff = [ None ] * (MAXIMUM_SIZE*2)
        
        distance = [ 0.0 ] * 3
        
        
        for i in range(3):
            max_array = np.argpartition(hist_3d_s[i], -MAXIMUM_SIZE)[-MAXIMUM_SIZE:]
            #min_array = np.argpartition(hist_3d_s[i],  MAXIMUM_SIZE)[:MAXIMUM_SIZE]    # minimum 
        
            # get the MAXIMUM value for each channel, only the first, and calculate 
            # the difference.
            maximums_values[i] = math.fabs( np.max(base_histogram[i]) - np.max(hist_3d_s[i]) )
        
            #max_array = np.concatenate((max_array,min_array))
            
            maximums.append (max_array)
            diff[i] = np.subtract(maximums_histogram[i], maximums[i] )
            
            # add coefs between maximums
            #diff[i] = np.multiply( diff[i] , [ 2, 1.5, 1.1 ])
            
            #a1 = maximums_histogram[i].astype(np.float32,casting='unsafe',copy=False)
            #b1 = maximums[i].astype(np.float32,casting='unsafe',copy=False)
            #distance[i] = math.fabs(cv2.compareHist(a1,b1, CV_MODE_TYPE))
            
            hdist[i] = np.sum(np.absolute(diff[i]))
            
            #print "#%d Distance: %.5f | Difference between %s and %s: %s" % (counter, hdist[i], maximums_histogram[i], maximums[i], diff[i])
            
        # data calculated in all channels, stimate the error for the frame and score it.
        # H 50%
        # S 30%
        # V 20%
        match = False
        #score = hdist[0]*0.5 + hdist[1]*0.3 + hdist[2]*0.2 +  maximums_values[0]*0.5 + maximums_values[1]*0.3 + maximums_values[2]*0.2
        #score_avg = (score_avg + score) / 2.0
    
        score_h = hdist[0] + maximums_values[0] 

        score_s =hdist[1] 
        
        #score_h = d_h + d_s + d_v
        #print score_h, score_s
        SCORE = 30  
        if score_avg <= SCORE and not position:
            position = counter
        
        if (hdist[0] + maximums_values[0]  < SCORE and hdist[1] + maximums_values[1] < 25) or \
           (hdist[0] + maximums_values[0]  < SCORE and hdist[2] + maximums_values[2] < 25):
            match = True
            matches += 1
       
        
        DEBUG=False
        if DEBUG:
            print "-- FRAME #%05d (Matches: %s) score: %.5f " % (counter, matches, score_h), "-" * 70 
            print "H_MAX %s H_LOCAL: %s DIFF: %s DIST: %s %.5f %.5f" % (maximums_histogram[0], maximums[0], diff[0], hdist[0], distance[0], maximums_values[0])
            print "S_MAX %s S_LOCAL: %s DIFF: %s DIST: %s %.5f %.5f" % (maximums_histogram[1], maximums[1], diff[1], hdist[1], distance[1], maximums_values[1])
            print "V_MAX %s V_LOCAL: %s DIFF: %s DIST: %s %.5f %.5f" % (maximums_histogram[2], maximums[2], diff[2], hdist[2], distance[2], maximums_values[2])
        # debug --- end
        
        counter += 1 

    percent = 0.0
    if counter > 0:
        percent = (matches*100.0/counter)
    
    position = position or -1
                
    print "Results: H(%s) video %s (Matches/Counter) %d/%d %d%% [converged at # %d]" % (histogram, video, matches, counter, percent, position)
  



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
    
    ROWS = [ 'neko', 'neko2', 'eli', 'eli2', 'firulais', 'firulais2', 'blue_ball', 'red_jar', 'hand', 'empty']
    COLS = [ 'neko', 'neko2', 'eli', 'eli2', 'firulais', 'firulais2', 'blue_ball', 'red_jar', 'hand', 'empty']
    
    #ROWS = [ 'firulais', 'red_jar' ]
    #COLS = [ 'firulais', 'red_jar' ]
        
    for r in range(len(ROWS)):
        for c in range(len(COLS)):
            avg= RUN_TEST_MATCH_VIDEO("videos/%s.npy" % ROWS[r], "videos/max_%s.npy" % ROWS[r], "videos/%s.h264" % COLS[c], METHOD, verbose=args.verbose)
            
        print ""