import cv2
import argparse
import numpy as np

# to avoid RASPBERRY problems with the backend (non interactive)
import matplotlib
matplotlib.use('Agg')

from matplotlib import pyplot as plt

import matplotlib.colors

import sys
import os
import os.path


from colormath.color_objects import LabColor, sRGBColor
from colormath.color_diff import delta_e_cie2000
from colormath.color_conversions import convert_color

## raspy
# pip --no-cache-dir install matplotlib
# pip --no-cache-dir install colormath
# pip --no-cache-dir uninstall networkx
# pip --no-cache-dir install networkx==1.11
# apt-get install python-scipy (binary depot)
# apt-get install python-sklearn (binary depot) 
# pip --no-cache-dir install scipy
# pip --no-cache-dir install sklearn


# on raspy --no-cache-dir pip to avoid MemoryError
        
#pip install scipy
#pip install sklearn
# /usr/local/bin/pip install colormath 
# NOTE: pip install networkx==1.11
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
        col = np.round(color, 0)
        # plot the relative percentage of each cluster
        endX = startX + (percent * 300)
        cv2.rectangle(bar, (int(startX), 0), (int(endX), 50),
            col.astype("uint8").tolist(), -1)
        startX = endX

    # return the bar chart

    return cv2.cvtColor(bar,cv2.COLOR_HSV2RGB)

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




def map_colors(hist, centroids,channels):



    return channels

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--element", help="Element", action="store")
    parser.add_argument("-v", "--verbose", help="verbose mode", action="store_true")

    args = parser.parse_args()
    cap = cv2.VideoCapture(args.element)

    hsvMin = np.array([25, 43, 0],np.uint8) # BGR green box
    hsvMax = np.array([91, 255, 255],np.uint8) # BGR green box

    frame_counter = 0

    colors = []
    
    while True:
        result,img = cap.read()
        if not result:
            break

        img_roi = img[30:608, 30:600] # ROI. Was rotated!!
       
        
        # REMOVE THE GREEN CHROMA
        
        img_roi = cv2.cvtColor(img_roi, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(img_roi, hsvMin, hsvMax)
        _, mask = cv2.threshold(mask,20, 255, cv2.THRESH_BINARY_INV)
        kernel = np.ones((5,5),np.uint8)
        mask = cv2.erode(mask, kernel, iterations=2)
        hsv = cv2.bitwise_and(img_roi,img_roi,mask= mask)

        #hsv = cv2.bilateralFilter(hsv,13,75,75)
        #KMEANS
        #works on HSV also!

        image = hsv
        if True:
            #image = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)
            # Resize it
            IMG_SIZE_R = 200
            h, w, _ = image.shape
            w_new = int(IMG_SIZE_R * w / max(w, h) )
            h_new = int(IMG_SIZE_R * h / max(w, h) )
            image = cv2.resize(image, (w_new, h_new));
            

        # Reshape the image to be a list of pixels
        image_array = image.reshape((image.shape[0] * image.shape[1], 3))
        clt = KMeans(n_clusters = 5)
        clt.fit(image_array)
        hist = centroid_histogram(clt)


        # add to the array of colors
        ##print "-" * 80
        for (percent, color) in zip(hist, clt.cluster_centers_):
            #rcol = np.int8(np.round(color,0))
            ##print "%.5f %s" % (percent, color)
            colors.append(color)

        #cv2.imwrite('framedump-TEST/frame_%08d.png' % (frame_counter), img )

        if args.verbose:
            bar = plot_colors(hist, clt.cluster_centers_)
            plt.figure()
            plt.axis("off")
            plt.imshow(bar)
            plt.show()

        frame_counter += 1

            # Wait longer to prevent freeze for videos.
        if args.verbose:
            if cv2.waitKey(10) & 0xFF == ord('q'):
                break

        #print frame_counter
        #if frame_counter > 10:
        #    break

    print "Frames processed: ", frame_counter

    if args.verbose:
        cv2.destroyAllWindows()

    clt = KMeans(n_clusters = 5)
    clt.fit(colors)
    hist = centroid_histogram(clt)

    # for order. don't needeit
    zipped = zip (hist, clt.cluster_centers_)
    zipped.sort(reverse=True, key=lambda x : x[0])
    hist, clt.cluster_centers_ = zip(*zipped)
    
    ### calculate histogram for colors.
    ###bin_len = len(channels.COLORS)
    ##bin_len = 16
    ##(hist, X) = np.histogram(channels.COLORS, bins = bin_len)
    ##print len(channels.COLORS)
    ### normalize the histogram, such that it sums to one
    ##hist = hist.astype("float")
  
    ###### GENERAL
      
    ind = np.arange(len(hist))
    
    colors_rgb = []
    print "=" * 80
    for (percent, color) in zip(hist, clt.cluster_centers_):
        #rcol = np.int8(np.round(color,0))
        a = np.uint8([[color]])
        x = cv2.cvtColor(a,cv2.COLOR_HSV2RGB)
        print "%.5f %s" % (percent, color)
        colors_rgb.append(x[0][0] / 255.0)
        
    for i in range(len(clt.cluster_centers_)-1):
        for j in range(i+1,len(clt.cluster_centers_)):
                    
            col_i = cv2.cvtColor(np.uint8([[clt.cluster_centers_[i]]]),cv2.COLOR_HSV2RGB)[0][0] / 255.0
            col_j = cv2.cvtColor(np.uint8([[clt.cluster_centers_[j]]]),cv2.COLOR_HSV2RGB)[0][0] / 255.0
           
            A_rgb = sRGBColor( col_i[0], col_i[1], col_i[2] )
            B_rgb = sRGBColor( col_j[0], col_j[1], col_j[2] )
    
            A = convert_color(A_rgb, LabColor)
            B = convert_color(B_rgb, LabColor)
         
            delta_e = delta_e_cie2000(A, B)
            print "(%s->%s) DE [%05.2f]%s -> %s" % (i,j, delta_e, np.round(col_i,2), np.round(col_j,2))
        
     
    l = plt.bar(ind, hist, linewidth=1, color=colors_rgb)
    plt.xlabel('Colors')
    plt.ylabel('Frequency')
    plt.title('Color Frequency)')
    plt.grid(True)

    dname = os.path.dirname(args.element)
    farg_png = "%s/%s_sklearn.png" % (dname, os.path.splitext(os.path.basename(args.element))[0])
    print("Writting to %s" % farg_png)
    plt.savefig(farg_png)

    



