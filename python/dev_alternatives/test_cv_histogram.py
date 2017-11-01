import cv2
import argparse
import numpy as np
from matplotlib import pyplot as plt



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--element", help="Histogram", action="store")  
    parser.add_argument("-t", "--test", help="img test", action="store")
    args = parser.parse_args()    
    
    
    base_histogram = np.load(args.element)

    base_histogram[0] = base_histogram[0].astype(np.float32)
    base_histogram[1] = base_histogram[1].astype(np.float32)
    base_histogram[2] = base_histogram[2].astype(np.float32)
    

    img = cv2.imread(args.test)
    
    img_roi = img[30:608, 30:600] # ROI. Was rotated!!
    
    hsv = cv2.cvtColor(img_roi, cv2.COLOR_BGR2HSV)
    
    
    hist_3d =   np.array([ np.zeros([180,1]), np.zeros([256,1]), np.zeros([256,1]) ])
    
    hist_3d[0] = cv2.calcHist([hsv],[0],None,[180],[0,180])
    hist_3d[1] = cv2.calcHist([hsv],[1],None,[256],[0,256])
    hist_3d[2] = cv2.calcHist([hsv],[2],None,[256],[0,256])


    
    cv2.normalize(hist_3d[0],hist_3d[0],0,180,cv2.NORM_MINMAX)
    cv2.normalize(hist_3d[1],hist_3d[1],0,255,cv2.NORM_MINMAX)
    cv2.normalize(hist_3d[2],hist_3d[2],0,255,cv2.NORM_MINMAX)

    #print base_histogram.shape, type(base_histogram[0][0][0])
    #print hist_3d.shape, type(hist_3d[0][0][0])


    d_h = cv2.compareHist(base_histogram[0], hist_3d[0], cv2.HISTCMP_BHATTACHARYYA)
    d_s = cv2.compareHist(base_histogram[1], hist_3d[1], cv2.HISTCMP_BHATTACHARYYA)
    d_v = cv2.compareHist(base_histogram[2], hist_3d[2], cv2.HISTCMP_BHATTACHARYYA)
    d_m = (d_h + d_s + d_v) / 3.0
    
    print ("Distance / HISTCMP_BHATTACHARYYA D(H,S,V,m): (%3.2f,%3.2f,%3.2f,%3.2f)" % (d_h, d_s, d_v, d_m))
        
    series = { 'h': ['r', 'HUE'], 's': ['g','SATURATION'], 'v': ['blue', 'VALUE'] }
    
    f, plots = plt.subplots(3, sharex=True, sharey=True)
    plots[0].set_title('Histogram HSV')
    
    series_l = ('h','s','v') 
    for i,serie in enumerate(series_l):
        col = series[serie][0]
        tit = series[serie][1]
        ind = np.arange(len(hist_3d[i]))
        plots[i].plot(hist_3d[i], color=col, label=tit, linewidth=2.0)
        plots[i].set_title(tit,loc='right',fontsize=10)
        plots[i].grid(True)
    
    f.subplots_adjust(hspace=0)
    plt.setp([a.get_xticklabels() for a in f.axes[:-1]], visible=False)
    plt.show()
    
