import cv2
import argparse
import numpy as np
from matplotlib import pyplot as plt
import sys
import os
import os.path


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


class CVHistogramChannelViewer:
    def __init__(self, window_name):
        self.hist_height = 256
        self.hist_width = 512
        self.nbins = 128
        self.bin_width = self.hist_width/self.nbins        
        self.h = np.zeros((self.hist_height,self.hist_width))
        self.bins = np.arange(self.nbins,dtype=np.int32).reshape(self.nbins,1)
        self.window_name = window_name
    
    def Draw(self,img,channel, upper_limit=256):
        #Calculate and normalise the histogram
        hist_hue = cv2.calcHist([img],[channel],None,[self.nbins],[0,upper_limit])
        # cv2.normalize(hist_hue,hist_hue,self.hist_height,cv2.NORM_MINMAX)
        self.hist=np.int32(np.around(hist_hue))
        self.pts = np.column_stack((self.bins,self.hist))

        #Loop through each bin and plot the rectangle in white
        for x,y in enumerate(self.hist):
            cv2.rectangle(self.h,(x*self.bin_width,y),(x*self.bin_width + self.bin_width-1,self.hist_height),(255),-1)

        #Flip upside down
        h=np.flipud(self.h)
        cv2.imshow(self.window_name, self.h)
        self.h = np.zeros((self.hist_height,self.hist_width))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--element", help="Element", action="store")  
    parser.add_argument("-v", "--verbose", help="verbose mode", action="store_true")
    
    args = parser.parse_args()    
    
    
    #cv2.namedWindow('image')
    
    if args.verbose:
        
        hist_r = CVHistogramChannelViewer('colorhist_h')
        hist_g = CVHistogramChannelViewer('colorhist_s')
        hist_b = CVHistogramChannelViewer('colorhist_v')
        
    cap = cv2.VideoCapture(args.element)

    bins_h = 180
    bins_s = 256
    bins_v = 256
    
    bins_h = 128
    bins_s = 128
    bins_v = 128
    
    
    hsvMin = np.array([25, 43, 0],np.uint8) # BGR green box
    hsvMax = np.array([91, 255, 255],np.uint8) # BGR green box
 
    hist_3d_m = np.array([ np.zeros([bins_h]), np.zeros([bins_s]), np.zeros([bins_v]) ])
    hist_3d_s = np.array([ np.zeros([bins_h]), np.zeros([bins_s]), np.zeros([bins_v]) ])
    hist_3d =   np.array([ np.zeros([bins_h]), np.zeros([bins_s]), np.zeros([bins_v]) ])
    
    frame_counter=0
    fname_alone = os.path.splitext(os.path.basename(args.element))[0]
    fname_alone_path = "framedump-%s" % fname_alone
    if not os.path.exists(fname_alone_path):
        os.makedirs(fname_alone_path)
    
    while True:
        result,img = cap.read()
        if not result:
            break
        
        img_roi = img[30:608, 30:600] # ROI. Was rotated!!
        #img_roi = cv2.bilateralFilter(img_roi,13,75,75)
        img_roi = cv2.cvtColor(img_roi, cv2.COLOR_BGR2HSV)
     
        mask = cv2.inRange(img_roi, hsvMin, hsvMax)
        
        _, mask = cv2.threshold(mask,20, 255, cv2.THRESH_BINARY_INV)
        kernel = np.ones((5,5),np.uint8)
        mask = cv2.erode(mask, kernel, iterations=2)
        
        hsv = cv2.bitwise_and(img_roi,img_roi,mask= mask)
        #
        # leave it has HSV
        # hsv = cv2.cvtColor(hsv, cv2.COLOR_BHSV2BGR)
        
        #cv2.imshow('image', hsv)
        #cv2.waitKey(5)
        
        #print hist_3d[0].shape
        bgr = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
        hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2LAB)
        
         
        h = cv2.calcHist([hsv],[0],None,[bins_h],[0,bins_h])
        s = cv2.calcHist([hsv],[1],None,[bins_s],[0,bins_s])
        v = cv2.calcHist([hsv],[2],None,[bins_v],[0,bins_v])
    
        hist_3d[0] = h.reshape((bins_h))
        hist_3d[1] = s.reshape((bins_s))
        hist_3d[2] = v.reshape((bins_v))
    
   
    
        #cv2.normalize(hist_3d[0],hist_3d[0],0,bins_h,cv2.NORM_MINMAX)
        #cv2.normalize(hist_3d[1],hist_3d[1],0,bins_s,cv2.NORM_MINMAX)
        #cv2.normalize(hist_3d[2],hist_3d[2],0,bins_v,cv2.NORM_MINMAX)
        
        # clear borders    
        if True:
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
        #if max_array_s[0] < 10 or max_array_s[0] > 120 or \
        #    max_array_v[0] < 10 or max_array_v[0] > 120:
        #    continue        

        
        if hist_3d_m[0] is None:
            hist_3d_m[0] = hist_3d[0]
            hist_3d_m[1] = hist_3d[1]
            hist_3d_m[2] = hist_3d[2]
        else:
            #print hist_3d_m[0].ndim,hist_3d_m[0].shape, hist_3d_m[0]
            #print  hist_3d_m[0].shape, hist_3d[0].shape
            
            hist_3d_m[0] = np.add(hist_3d_m[0], hist_3d[0]) / 1.0
            hist_3d_m[1] = np.add(hist_3d_m[1], hist_3d[1]) / 1.0
            hist_3d_m[2] = np.add(hist_3d_m[2], hist_3d[2]) / 1.0
            #print hist_3d_m[0].ndim,hist_3d_m[0].shape, hist_3d_m[0] 
            
         
    
        #cv2.imwrite('framedump-TEST/frame_%08d.png' % (frame_counter), img )       
    
        if args.verbose:
            #hist_r.Draw(hsv, 0, upper_limit=180) #h
            #hist_g.Draw(hsv, 1) #s
            #hist_b.Draw(hsv, 2) #v
            cv2.imshow('image', cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR))
            cv2.imwrite('framedump-%s/frame_%08d.png' % (fname_alone,frame_counter), img )
        
        frame_counter += 1
 
            # Wait longer to prevent freeze for videos.
        if args.verbose:
            if cv2.waitKey(10) & 0xFF == ord('q'):
                break
    
    
    
    print "Frames processed: ", frame_counter     
    # calculate the "average" histogram. This doens't reflect the ADDitive of the all histograms.
    
    # calculate the average per point at last.
    #for i in range(3):
    #    hist_3d_m[i] = hist_3d_m[i] / float(frame_counter) #calculate the average.
 
 
 
    cv2.normalize(hist_3d_m[0],hist_3d_m[0],0,bins_h,cv2.NORM_MINMAX)
    cv2.normalize(hist_3d_m[1],hist_3d_m[1],0,bins_s,cv2.NORM_MINMAX)
    cv2.normalize(hist_3d_m[2],hist_3d_m[2],0,bins_v,cv2.NORM_MINMAX)
    
    hist_3d_s[0] = savitzky_golay(hist_3d_m[0], 11, 9) # window size 51, polynomial order 3
    hist_3d_s[1] = savitzky_golay(hist_3d_m[1], 11, 9) # window size 51, polynomial order 3
    hist_3d_s[2] = savitzky_golay(hist_3d_m[2], 11, 9) # window size 51, polynomial order 3
    if args.verbose:
        cv2.destroyAllWindows()
    

    
    
    series = { 'h': ['r', 'HUE'], 's': ['g','SATURATION'], 'v': ['b', 'VALUE'] }
    l_handles = []
    
    f, plots = plt.subplots(3, sharex=True, sharey=True)
    plots[0].set_title('Histogram LAB')
    
    MAXIMUM_SIZE = 3
    maximums = []
    series_l = ('h','s','v') 
    for i,serie in enumerate(series_l):
        

        col = series[serie][0]
        tit = series[serie][1]
        
        ind = np.arange(len(hist_3d_s[i]))
        #h = plots[i].bar(ind, hist_3d_m[i], color="#cacaca", label=tit)
        plots[i].plot(hist_3d_m[i], color='#cacaca', label=tit, linewidth=1.2)
        plots[i].plot(hist_3d_s[i], color=col, label=tit, linewidth=1.2)
        
        #max
        #plots[i].axvline(hist_3d_m[i].argmax(), color='#9E7a7a', linestyle='dashed', linewidth=1.0)
        
        max_array = np.argpartition(hist_3d_s[i], -MAXIMUM_SIZE)[-MAXIMUM_SIZE:]  # maximum
        #min_array = np.argpartition(hist_3d_s[i], MAXIMUM_SIZE)[:MAXIMUM_SIZE]    # minimum 
        #max_array = np.concatenate((max_array,min_array))
        maximums.append(max_array)
        

        for am in max_array:
            plots[i].axvline(am, color='#9E7a7a', linestyle='dashed', linewidth=1.0)
           
        
        plots[i].set_title(tit,loc='right',fontsize=10)
        plots[i].grid(True)
    
    
    #print maximums
    #plt.xlabel('Smarts')
    #plt.ylabel('Probability')
    #plt.title('Histogram of IQ')
    #plt.text(60, .025, r'$\mu=100,\ \sigma=15$')
    # Fine-tune figure; make subplots close to each other and hide x ticks for
    # all but bottom plot.
    f.subplots_adjust(hspace=0)
    plt.setp([a.get_xticklabels() for a in f.axes[:-1]], visible=False)
    #plt.show()
    
    dname = os.path.dirname(args.element)
    farg_png = "%s/%s.png" % (dname, os.path.splitext(os.path.basename(args.element))[0])
    farg_np = "%s/%s" % (dname, os.path.splitext(os.path.basename(args.element))[0])
    farg_max = "%s/max_%s" % (dname, os.path.splitext(os.path.basename(args.element))[0])
    print("Writting to %s" % farg_png)
    print("Writting to %s.npy" % farg_np)
    print("Writting to %s.npy" % farg_max)
    plt.savefig(farg_png)
    np.save(farg_np, hist_3d_s)
    
    #for i in range(len(maximums)):
    #    maximums[i] = maximums[i].astype(np.integer)
        
    #print type(maximums)
    #print maximums
    
    np.save(farg_max, maximums)



