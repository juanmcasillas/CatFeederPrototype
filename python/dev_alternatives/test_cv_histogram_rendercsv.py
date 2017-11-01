import cv2
import argparse
import numpy as np
from matplotlib import pyplot as plt
import glob
from numpy import nan
import math

def RUN_TEST_MATCH(element,testdir, CV_MODE, coefs, verbose=True):

    OPENCV_METHODS = {
                      "correlation": cv2.HISTCMP_CORREL,        # bigger better
                      "chi-squared": cv2.HISTCMP_CHISQR,
                      "intersection": cv2.HISTCMP_INTERSECT,    # bigger better
                      "bhattacharyya": cv2.HISTCMP_BHATTACHARYYA
        }  
    
    CV_MODE_TYPE = OPENCV_METHODS[CV_MODE]

  
    base_histogram = np.load(element)
    hist_3d =   np.array([ np.zeros([180,1]), np.zeros([256,1]), np.zeros([256,1]) ])
    
    base_histogram[0] = base_histogram[0].astype(np.float32)
    base_histogram[1] = base_histogram[1].astype(np.float32)
    base_histogram[2] = base_histogram[2].astype(np.float32)
    
    avg = 0.0
    counter = 0
    nan_frames = 0
    matches = 0
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
    
        d_h = cv2.compareHist(base_histogram[0], hist_3d[0], CV_MODE_TYPE)
        d_s = cv2.compareHist(base_histogram[1], hist_3d[1], CV_MODE_TYPE)
        d_v = cv2.compareHist(base_histogram[2], hist_3d[2], CV_MODE_TYPE)
        
        if not math.isnan(d_v):
            # if real value, add to the average, else skip.
            #d_v = 1.0
            #d_m = (d_h + d_s + d_v) / 3.0
            match = False
            h_delta = 0.5
            s_delta = 0.5
            v_delta = 0.5
            
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

 
    
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--element", help="Histogram", action="store")  
    parser.add_argument("-v", "--verbose", help="run metrics", action="store_true")
    args = parser.parse_args()    
    
    METHOD = 'correlation'
            
    data = CREATE_DATA("videos/%s.npy" % COLS[c], "framedump-%s" % ROWS[r], METHOD, COEFS[key_coef], verbose=args.verbose)
                