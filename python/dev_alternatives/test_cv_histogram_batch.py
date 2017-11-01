import cv2
import argparse
import numpy as np
from matplotlib import pyplot as plt
import glob
from numpy import nan
import math
import sys



def RUN_TEST(element,testdir, CV_MODE, verbose=True):

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
        
            d_m = (d_h + d_s + d_v) / 3.0
        
            if verbose:
                print("%s Distance(%s) D(H,S,V,m): (%3.2f,%3.2f,%3.2f,%3.2f)" % (imagePath, CV_MODE, d_h, d_s, d_v, d_m))

            avg += d_m
            counter += 1   
        else:
            nan_frames +=1

    print "Nan_Frames: %d" % nan_frames

    avg = avg / float(counter)

    if verbose:
        print "total avg: %3.2f (#%d items)" % (avg, counter)
    
    return avg,d_h,d_s,d_v
     
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
    
    #OPENCV_METHODS = { "correlation": cv2.HISTCMP_CORREL }
    
    
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--element", help="Histogram", action="store")  
    parser.add_argument("-t", "--test", help="dir for test", action="store")
    parser.add_argument("-m", "--metrics", help="run metrics", action="store_true")
    parser.add_argument("-v", "--verbose", help="run metrics", action="store_true")
    parser.add_argument("-f", "--function", help="CV method function", action="store", default="bhattacharyya")
    args = parser.parse_args()    
    
    if not args.metrics:
        print RUN_TEST(args.element, args.test, args.function, verbose=args.verbose)
    else:
    
        # build the CSV matrix.
        ROWS = [ 'neko', 'neko2', 'eli', 'eli2', 'firulais', 'firulais2', 'firulais3', 'blue_ball', 'red_jar', 'hand', 'empty']
        COLS = [ 'neko', 'neko2', 'eli', 'eli2', 'firulais', 'firulais2', 'firulais3', 'blue_ball', 'red_jar', 'hand', 'empty']
        
        #ROWS = [ 'neko', 'red_jar'  ]
        #COLS = [ 'neko', 'red_jar'  ]
        
        for METHOD in OPENCV_METHODS.keys():
            
            # avg, h, s, v distances
            RESULTS = [ [ [0.0,0.0,0.0,0.0] ] * len(ROWS) ] * len(COLS)
            
            for r in range(len(ROWS)):
                for c in range(len(COLS)):
                    avg,d_h, d_s, d_v = RUN_TEST("videos/%s.npy" % COLS[c], "framedump-%s" % ROWS[r], METHOD, verbose=args.verbose)
                    print "Testing histogram(%s.npy) vs frames(%s) (%s: %.5f avg hsv=(%.5f,%.5f,%.5f) )" % (COLS[c], ROWS[r], METHOD, avg, d_h, d_s, d_v)
                    RESULTS[r][c] = [ avg, d_h, d_s, d_v ]
                    
                RESULTS[r] = [ ROWS[r] ] + RESULTS[r]
                 
            #results done. Create a fancy CSV file.
       
            sep=";"
            header = [ "HIST" ]
            for j in range(len(COLS)):
                for x in [ 'AVG', 'HUE','SAT','VAL']:
                    lab = COLS[j] + "_" + x
                    header.append(lab)
            header_s = sep.join(header)
            
           
            lines = [ header_s ]
            for i in range(len(ROWS)):
                r = RESULTS[i]
                data = []
                r_label = r[0]
                r = r[1:]
                for j in r:
                    data.append(sep.join(["%.5f" % x for x in j]))
                lines.append(sep.join([r_label] + data))
            data = "\n".join(lines)
            
            fd = file("results_%s.csv" % METHOD ,"wb+")
            fd.write(data)
            fd.close()
 
