import cv2
import argparse
import numpy as np
from matplotlib import pyplot as plt
import sys
import os
import os.path

#pip install scipy
#pip install sklearn
# https://pypi.python.org/pypi/scipy
#  C:\Python27\Scripts\pip.exe install E:\Descargas\scipy-1.0.0rc1-cp27-none-win32.whl (?? raspy?)

from sklearn.cluster import KMeans
from sklearn import metrics

def plot_colors(hist, centroids):
    # initialize the bar chart representing the relative frequency
    # of each of the colors
    bar = np.zeros((50, 300, 3), dtype = "uint8")
    startX = 0
 
    # loop over the percentage of each cluster and the color of
    # each cluster
    for (percent, color) in zip(hist, centroids):
        # plot the relative percentage of each cluster
        endX = startX + (percent * 300)
        cv2.rectangle(bar, (int(startX), 0), (int(endX), 50),
            color.astype("uint8").tolist(), -1)
        startX = endX
    
    # return the bar chart
    return bar

def centroid_histogram(clt):
    # grab the number of different clusters and create a histogram
    # based on the number of pixels assigned to each cluster
    numLabels = np.arange(0, len(np.unique(clt.labels_)) + 1)
    (hist, _) = np.histogram(clt.labels_, bins = numLabels)
 
    # normalize the histogram, such that it sums to one
    hist = hist.astype("float")
    hist /= hist.sum()
 
    # return the histogram
    return hist


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--element", help="Element", action="store")  
    parser.add_argument("-v", "--verbose", help="verbose mode", action="store_true")
    
    args = parser.parse_args()    
    
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

        #KMEANS
        image = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)
        # Resize it
        h, w, _ = image.shape
        w_new = int(100 * w / max(w, h) )
        h_new = int(100 * h / max(w, h) )
        image = cv2.resize(image, (w_new, h_new));

        # Reshape the image to be a list of pixels
        image_array = image.reshape((image.shape[0] * image.shape[1], 3))
        # Clusters the pixels
        clt = KMeans(n_clusters = 3)
        clt.fit(image_array)
        # Finds how many pixels are in each cluster
        hist = centroid_histogram(clt)
        
        # Sort the clusters according to how many pixel they have
        zipped = zip (hist, clt.cluster_centers_)
        zipped.sort(reverse=True, key=lambda x : x[0])
        hist, clt.cluster_centers = zip(*zipped)
        
        bestSilhouette = -1
        bestClusters = 0

        for clusters in range(2, 10):
            # Cluster colours
            clt = KMeans(n_clusters = clusters)
            clt.fit(image_array)
        
            # Validate clustering result
            silhouette = metrics.silhouette_score(image_array, clt.labels_, metric='euclidean', sample_size=3000)
        
            # Find the best one
            if silhouette > bestSilhouette:
                bestSilhouette = silhouette;
                bestClusters = clusters;
        
        print bestSilhouette
        print bestClusters
        clt = KMeans(n_clusters = bestClusters)
        clt.fit(image_array)
        # Finds how many pixels are in each cluster
        hist = centroid_histogram(clt)
        
        # Sort the clusters according to how many pixel they have
        zipped = zip (hist, clt.cluster_centers_)
        zipped.sort(reverse=True, key=lambda x : x[0])
        hist, clt.cluster_centers = zip(*zipped)
    
        bar = plot_colors(hist, clt.cluster_centers)
        
        # show our color bart
        plt.figure()
        plt.axis("off")
        plt.imshow(bar)
        plt.show()
    
        #cv2.imwrite('framedump-TEST/frame_%08d.png' % (frame_counter), img )       
    
        if args.verbose:
            cv2.imshow('image', cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR))
            cv2.imwrite('framedump-%s/frame_%08d.png' % (fname_alone,frame_counter), img )
        
        frame_counter += 1
 
            # Wait longer to prevent freeze for videos.
        if args.verbose:
            if cv2.waitKey(10) & 0xFF == ord('q'):
                break
    
    print "Frames processed: ", frame_counter     
   
    if args.verbose:
        cv2.destroyAllWindows()
    

    
   
    
   


