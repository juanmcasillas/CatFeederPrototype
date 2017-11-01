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
  
    cap = cv2.VideoCapture(video)
    #cv2.namedWindow('image')

    print "Building histograms for video %s H(%s)" % (video,histogram)
    while True:
        result,img = cap.read()
        if not result:
            break
        
        img_roi = img[30:608, 30:600] # ROI. Was rotated!!
        #hsv = cv2.cvtColor(img_roi, cv2.COLOR_BGR2HSV)
        
        ## removed # img_roi = cv2.bilateralFilter(img_roi,13,75,75)
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
            
            #print("%s#%d vs %s (%s) D(H,S,V,m)  Matches: %s : (%3.2f,%3.2f,%3.2f)" % (video, counter, histogram, CV_MODE, match, d_h, d_s, d_v))
            if d_h > h_delta and d_s > s_delta and d_v > v_delta: 
                match = True
                matches += 1
                #print("%s#%d vs %s (%s) D(H,S,V,m)  Matches: %s : (%3.2f,%3.2f,%3.2f)" % (video, counter, histogram, CV_MODE, match, d_h, d_s, d_v))
                
                
        else:
            match = False
            nan_frames +=1


        # debug --- begin
        # create good histogram of the frame
                
        hist_3d_s[0] = savitzky_golay(hist_3d[0], 21, 11) # window size 51, polynomial order 3
        hist_3d_s[1] = savitzky_golay(hist_3d[1], 21, 11) # window size 51, polynomial order 3
        hist_3d_s[2] = savitzky_golay(hist_3d[2], 21, 11) # window size 51, polynomial order 3
    
        series = { 'h': ['b', 'HUE'], 's': ['g','SATURATION'], 'v': ['r', 'VALUE'] }
        l_handles = []
        
        f, plots = plt.subplots(3, sharex=True, sharey=True)
        plots[0].set_title('LOCAL Histogram HSV')
        
        MAXIMUM_SIZE = 3
        maximums = []
        series_l = ('h','s','v') 
        for i,serie in enumerate(series_l):
    
            col = series[serie][0]
            tit = series[serie][1]
            
            ind = np.arange(len(hist_3d_s[i]))
            #h = plots[i].bar(ind, hist_3d_m[i], color="#cacaca", label=tit)
            plots[i].plot(hist_3d[i], color='#cacaca', label=tit, linewidth=1.2)
            plots[i].plot(hist_3d_s[i], color=col, label=tit, linewidth=1.2)
            
            
            max_array = np.argpartition(hist_3d_s[i], -MAXIMUM_SIZE)[-MAXIMUM_SIZE:]
            min_array = np.argpartition(hist_3d_s[i],  MAXIMUM_SIZE)[:MAXIMUM_SIZE]    # minimum 
            #max_array = np.concatenate((max_array,min_array))
            maximums.append (max_array)
        
            for am in max_array:
                plots[i].axvline(am, color='#9E7a7a', linestyle='dashed', linewidth=1.0)            
                
            plots[i].set_title(tit,loc='right',fontsize=10)
            plots[i].grid(True)
        
        
        f.subplots_adjust(hspace=0)
        plt.setp([a.get_xticklabels() for a in f.axes[:-1]], visible=False)
     
        buffer_ = StringIO()
        plt.savefig(buffer_, format = "png")
        buffer_.seek(0)
        image = PIL.Image.open(buffer_)
        local_hist = np.asarray(image)
        buffer_.close()
        
        
        # create diference plot

        

        f, plots = plt.subplots(3, sharex=True, sharey=True)
        plots[0].set_title('Difference')
    
        series = { 'h': ['b', 'HUE-MAX'], 's': ['g','SATURATION-MAX'], 'v': ['r', 'VALUE-MAX'] }
        series_l = ('h','s','v') 
        #print "-" * 78
        for i,serie in enumerate(series_l):

            col = series[serie][0]
            tit = series[serie][1]
            
            ind = np.arange(len(maximums[i]))
            #plots[i].plot(maximums[i], color=col, label=tit, linewidth=1.2)
            
            #print "A",maximums_histogram[i].astype(np.float)
            #print "B",maximums[i].astype(np.float)
            
            
            d = np.subtract(maximums_histogram[i], maximums[i] )
            #print "#%0d MAX %s, LOCAL %s, d %s" % (counter, maximums_histogram[i],maximums[i], d )
            
            plots[i].bar(range(len(maximums[i])),maximums[i], color="#cacaca", label=tit)
            plots[i].bar(range(len(d)),d, color=col, label=tit)
            
            
            plots[i].set_title(tit,loc='right',fontsize=10)
            plots[i].grid(True)
        
        f.subplots_adjust(hspace=0)
        plt.setp([a.get_xticklabels() for a in f.axes[:-1]], visible=False)        
       
        buffer_ = StringIO()
        plt.savefig(buffer_, format = "png")
        buffer_.seek(0)
        image = PIL.Image.open(buffer_)
        local_max = np.asarray(image)
        buffer_.close()
        
        # until here
        
        #dname = os.path.dirname(args.element)
        #farg_png = "%s/%s.png" % (dname, os.path.splitext(os.path.basename(args.element))[0])
        
        
        # create big figure.
        img_bgr = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR) # to bgr
        
        img_scaled = cv2.resize(img_bgr,(640, 480), interpolation = cv2.INTER_CUBIC)
        hfname = os.path.splitext(os.path.basename(histogram))[0]
        hfvideo = os.path.splitext(os.path.basename(video))[0]
        img_hist = cv2.imread('videos/%s.png' % hfname)
        img_hist = cv2.resize(img_hist,(640, 480), interpolation = cv2.INTER_CUBIC)
        local_hist = cv2.resize(local_hist,(640, 480), interpolation = cv2.INTER_CUBIC)
        local_hist = local_hist[:,:,:3]
        local_max = cv2.resize(local_max,(640, 480), interpolation = cv2.INTER_CUBIC)
        local_max = local_max[:,:,:3]
        
        height = img_scaled.shape[0] + img_hist.shape[0]
        width  = img_scaled.shape[1] + local_hist.shape[1]
       
        #print "W: %3.2f, H: %3.2f" % (width, height)
        
        new_img = np.zeros((height,width,3), np.uint8)
        
        new_img[ 0:img_scaled.shape[0], 0:img_scaled.shape[1] ] = img_scaled
        new_img[ img_scaled.shape[0]:img_scaled.shape[0] + img_hist.shape[0], 0:img_hist.shape[1] ] = img_hist
        new_img[ 0:img_scaled.shape[0], img_scaled.shape[1]:img_scaled.shape[1] + local_hist.shape[1]] = local_hist
        
        new_img[ img_scaled.shape[0]:img_scaled.shape[0] + local_max.shape[0], img_scaled.shape[1]:img_scaled.shape[1] + local_max.shape[1]] = local_max
        
        
        #print "W: %3.2f, H: %3.2f (%3.2f, %3.2f)" % (width, height, new_img.shape[0], new_img.shape[1])
        #print "(%3.2f, %3.2f)" % (img_hist.shape[0], img_hist.shape[1])
        #print "(%3.2f, %3.2f)" % (local_hist.shape[0], local_hist.shape[1])
        
    
        #new_img[0:img_scaled.shape[0],0:img_scaled.shape[1]] = img_scaled
        #new_img[0:img_hist.shape[0],
        #        img_scaled.shape[1]:img_scaled.shape[1]+img_hist.shape[1]] = img_hist
        
        #new_img[0:img_hist.shape[0],
        #        0:img_hist.shape[1]] = img_hist
        
        #new_img[ 0:img_scaled.shape[0]+11+300,
        #         img_scaled.shape[1]:img_scaled.shape[1]+local_hist.shape[1]] = local_hist
        
        
        #new_img[0:0+img_scaled.shape[0], 0:0+img_scaled.shape[1]] = img_hist
        #l_img[y_offset:y_offset+s_img.shape[0], x_offset:x_offset+s_img.shape[1]] = s_img
        
        dirpath = 'framedump-%s-%s' % (hfname,hfvideo)
        if not os.path.exists(dirpath):
            os.makedirs(dirpath)
        fname = '%s/frame_%08d.png' % (dirpath, counter)
        #print "writting ", fname
        cv2.imwrite(fname, new_img )
        plt.close('all')

        
        
        # debug --- end
        


        counter += 1 


    percent = 0.0
    if counter > 0:
        percent = (matches*100.0/counter)
                
    #print "Matches: (%s vs %s) %d/%d %d%%" % (video, histogram, matches, counter, percent)




if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--element", help="Histogram", action="store")  
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
    COLS = [ 'eli', 'neko2', 'neko3', 'eli', 'firulais', 'firulais2', 'firulais3'] 
    
    ROWS = [ 'firulais', 'firulais2', 'red_jar' ]
    COLS = [ 'firulais', 'firulais2', 'red_jar' ]
   
    ROWS = [ 'neko', 'neko2' ]
    COLS = [ 'neko', 'neko2' ]
   
        
    for r in range(len(ROWS)):
        for c in range(len(COLS)):
            avg= RUN_TEST_MATCH_VIDEO("videos/%s.npy" % ROWS[r], "videos/max_%s.npy" % ROWS[r], "videos/%s.h264" % COLS[c], METHOD, verbose=args.verbose)
            