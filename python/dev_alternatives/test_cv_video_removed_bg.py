import cv2
import argparse
import numpy as np
from matplotlib import pyplot as plt
import sys
import os
import os.path



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
    
    bg = cv2.imread("framedump-empty/frame_00000023.png")
    bg_roi = bg[30:608, 30:600] # ROI. Was rotated!!
    bg_roi = cv2.GaussianBlur(bg_roi,(5,5),0)
    
    cv2.namedWindow('image')
    
    if args.verbose:
        hist_r = CVHistogramChannelViewer('colorhist_h')
        hist_g = CVHistogramChannelViewer('colorhist_s')
        hist_b = CVHistogramChannelViewer('colorhist_v')
        
    cap = cv2.VideoCapture(args.element)
    

    hist_3d_m = np.array([ np.zeros([180,1]), np.zeros([256,1]), np.zeros([256,1]) ])
    hist_3d =   np.array([ np.zeros([180,1]), np.zeros([256,1]), np.zeros([256,1]) ])
    
    frame_counter=0
    while True:
        result,img = cap.read()
        if not result:
            break
        
        img_roi = img[30:608, 30:600] # ROI. Was rotated!!
        
        mask_roi = cv2.subtract(img_roi, bg_roi)
        mask_roi = cv2.cvtColor(mask_roi, cv2.COLOR_BGR2GRAY)
        kernel = np.ones((10,10),np.uint8)
        mask_roi = cv2.morphologyEx(mask_roi, cv2.MORPH_OPEN, kernel)
        mask_roi = cv2.threshold(mask_roi, 5, 255, cv2.THRESH_BINARY)[1]
        masked =  cv2.bitwise_and(img_roi,img_roi, mask= mask_roi)
     
        cv2.imshow('image', masked)
        hsv = cv2.cvtColor(masked, cv2.COLOR_BGR2HSV)
        
        
        hist_3d[0] = cv2.calcHist([hsv],[0],None,[180],[0,180])
        hist_3d[1] = cv2.calcHist([hsv],[1],None,[256],[0,256])
        hist_3d[2] = cv2.calcHist([hsv],[2],None,[256],[0,256])
        
        cv2.normalize(hist_3d[0],hist_3d[0],0,180,cv2.NORM_MINMAX)
        cv2.normalize(hist_3d[1],hist_3d[1],0,255,cv2.NORM_MINMAX)
        cv2.normalize(hist_3d[2],hist_3d[2],0,255,cv2.NORM_MINMAX)
        
        for i in range(3):
            if hist_3d_m[i] is None:
                hist_3d_m[i] = hist_3d[i]
            else:
                hist_3d_m[i] = np.add(hist_3d_m[i], hist_3d[i])
            
        if args.verbose:
            hist_r.Draw(hsv, 0, upper_limit=180) #h
            hist_g.Draw(hsv, 1) #s
            hist_b.Draw(hsv, 2) #v
            cv2.imshow('image',img)
            cv2.imwrite('framedump/frame_%08d.png' % frame_counter, img )
        
        frame_counter += 1
 
            # Wait longer to prevent freeze for videos.
        if args.verbose:
            if cv2.waitKey(33) & 0xFF == ord('q'):
                break
    
        if cv2.waitKey(33) & 0xFF == ord('q'):
            break
    
    for i in range(3):
        hist_3d_m[i] = hist_3d_m[i] / float(frame_counter) #calculate the average.
    
    if args.verbose:
        cv2.destroyAllWindows()
    
    series = { 'h': ['r', 'HUE'], 's': ['g','SATURATION'], 'v': ['blue', 'VALUE'] }
    l_handles = []
    
    
    f, plots = plt.subplots(3, sharex=True, sharey=True)
    plots[0].set_title('Histogram HSV')
    
    series_l = ('h','s','v') 
    for i,serie in enumerate(series_l):

        col = series[serie][0]
        tit = series[serie][1]
        
        ind = np.arange(len(hist_3d_m[i]))
        #h = plots[i].bar(ind, hist_3d_m[i], color="#cacaca", label=tit)
        plots[i].plot(hist_3d_m[i], color=col, label=tit, linewidth=2.0)
        plots[i].set_title(tit,loc='right',fontsize=10)
        plots[i].grid(True)
    
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
    print("Writting to %s" % farg_png)
    print("Writting to %s.npy" % farg_np)
    plt.savefig(farg_png)
    np.save(farg_np, hist_3d_m)



