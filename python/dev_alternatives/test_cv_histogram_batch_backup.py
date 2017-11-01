import cv2
import argparse
import numpy as np
from matplotlib import pyplot as plt
import glob
from numpy import nan
import math

def RUN_TEST(element,testdir, CV_MODE, verbose=True):

  
    base_histogram = np.load(element)
    hist_3d =   np.array([ np.zeros([180,1]), np.zeros([256,1]), np.zeros([256,1]) ])
    
    base_histogram[0] = base_histogram[0].astype(np.float32)
    base_histogram[1] = base_histogram[1].astype(np.float32)
    base_histogram[2] = base_histogram[2].astype(np.float32)
    
    avg = 0.0
    counter = 0
    nan_frames = 0
    for imagePath in glob.glob(testdir + "/*.png"):
        # extract the image filename (assumed to be unique) and
        # load the image, updating the images dictionary
        filename = imagePath[imagePath.rfind("/") + 1:]
        
        img = cv2.imread(imagePath)
        
        img_roi = img[30:608, 30:600] # ROI. Was rotated!!
        
        hsv = cv2.cvtColor(img_roi, cv2.COLOR_BGR2HSV)
        
        hist_3d[0] = cv2.calcHist([hsv],[0],None,[180],[0,180])
        hist_3d[1] = cv2.calcHist([hsv],[1],None,[256],[0,256])
        hist_3d[2] = cv2.calcHist([hsv],[2],None,[256],[0,256])
    
        cv2.normalize(hist_3d[0],hist_3d[0],0,180,cv2.NORM_MINMAX)
        cv2.normalize(hist_3d[1],hist_3d[1],0,255,cv2.NORM_MINMAX)
        cv2.normalize(hist_3d[2],hist_3d[2],0,255,cv2.NORM_MINMAX)
    
        d_h = cv2.compareHist(base_histogram[0], hist_3d[0], CV_MODE)
        d_s = cv2.compareHist(base_histogram[1], hist_3d[1], CV_MODE)
        d_v = cv2.compareHist(base_histogram[2], hist_3d[2], CV_MODE)
        
        if not math.isnan(d_v):
            # if real value, add to the average, else skip.
            #d_v = 1.0
        
            d_m = (d_h + d_s + d_v) / 3.0
        
            if verbose:
                 print("%s Distance(HISTCMP_BHATTACHARYYA) D(H,S,V,m): (%3.2f,%3.2f,%3.2f,%3.2f)" % (imagePath, d_h, d_s, d_v, d_m))

            avg += d_m
            counter += 1   
        else:
            nan_frames +=1

    print "Nan_Frames: %d" % nan_frames

    avg = avg / float(counter)

    if verbose:
        print "total avg: %3.2f (#%d items)" % (avg, counter)
    
    return avg
     
#         series = { 'h': ['r', 'HUE'], 's': ['g','SATURATION'], 'v': ['blue', 'VALUE'] }
#         
#         f, plots = plt.subplots(3, sharex=True, sharey=True)
#         plots[0].set_title('Histogram HSV')
#         
#         series_l = ('h','s','v') 
#         for i,serie in enumerate(series_l):
#             col = series[serie][0]
#             tit = series[serie][1]
#             ind = np.arange(len(hist_3d[i]))
#             plots[i].plot(hist_3d[i], color=col, label=tit, linewidth=2.0)
#             plots[i].set_title(tit,loc='right',fontsize=10)
#             plots[i].grid(True)
#         
#         f.subplots_adjust(hspace=0)
#         plt.setp([a.get_xticklabels() for a in f.axes[:-1]], visible=False)
#         plt.show()
    

if __name__ == "__main__":

    OPENCV_METHODS = {
                      "correlation": cv2.HISTCMP_CORREL,        # bigger better
                      "chi-squared": cv2.HISTCMP_CHISQR,
                      "intersection": cv2.HISTCMP_INTERSECT,    # bigger better
                      "bhattacharyya": cv2.HISTCMP_BHATTACHARYYA
        }  
    
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--element", help="Histogram", action="store")  
    parser.add_argument("-t", "--test", help="dir for test", action="store")
    parser.add_argument("-m", "--metrics", help="run metrics", action="store_true")
    parser.add_argument("-v", "--verbose", help="run metrics", action="store_true")
    parser.add_argument("-f", "--function", help="CV method function", action="store", default="bhattacharyya")
    args = parser.parse_args()    
    
    if not args.metrics:
        print RUN_TEST(args.element, args.test, OPENCV_METHODS[args.function], verbose=args.verbose)
    else:
    
        # build the CSV matrix.
        ROWS = [ 'neko', 'neko2', 'neko3', 'eli', 'firulais', 'firulais2', 'firulais3', 'blue_ball', 'red_jar', 'hand', 'empty']
        COLS = [ 'neko', 'neko2', 'neko3', 'eli', 'firulais', 'firulais2', 'firulais3', 'blue_ball', 'red_jar', 'hand', 'empty']
        
        for METHOD in OPENCV_METHODS.keys():
            
            RESULTS = [ [ 0.0 ] * len(ROWS) ] * len(COLS)
            
            for r in range(len(ROWS)):
                for c in range(len(COLS)):
                    avg= RUN_TEST("videos/%s.npy" % COLS[c], "framedump-%s" % ROWS[r], OPENCV_METHODS[METHOD], verbose=args.verbose)
                    print "Testing histogram(%s.npy) vs frames(%s) (%s %3.2f avg)" % (COLS[c], ROWS[r], METHOD, avg)
                    RESULTS[r][c] = avg
                RESULTS[r] = [ ROWS[r] ] + RESULTS[r]
                 
            #results done. Create a fancy CSV file.
            sep = ";"
            #fmt = sep.join( ['%s'] + ["%3.2f"] * len(COLS) )
            fmt = sep.join( ['%s'] * (len(COLS)+1) )
            
            np.savetxt("results_%s.csv" % METHOD, RESULTS, delimiter=sep, header= sep.join(['HIST'] + COLS), fmt=fmt , comments='')