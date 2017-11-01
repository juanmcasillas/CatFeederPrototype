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
import math


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

    return bar



def centroid_histogram(labels):
    # grab the number of different clusters and create a histogram
    # based on the number of pixels assigned to each cluster
    numLabels = np.arange(0, len(np.unique(labels)) + 1)
    
    (hist, _) = np.histogram(labels, bins = numLabels)

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
    cap = cv2.VideoCapture(args.element)

    #hsvMin = np.array([25, 43, 0],np.uint8) # BGR green box
    hsvMin = np.array([25, 43, 0],np.uint8) # BGR green box
    hsvMax = np.array([180, 255, 255],np.uint8) # BGR green box

    hsvMin = np.array([38, 137, 0],np.uint8) # BGR
    hsvMax = np.array([72, 255, 255],np.uint8) # BGR
    
    frame_counter = 0

    colors = []

    if args.verbose:
        cv2.namedWindow("image")
    
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
            IMG_SIZE_R = 100
            h, w, _ = image.shape
            w_new = int(IMG_SIZE_R * w / max(w, h) )
            h_new = int(IMG_SIZE_R * h / max(w, h) )
            image = cv2.resize(image, (w_new, h_new));
        
        # remove the background. Note that this changes the size and the shape
        # so I have to fill with "empty" values the difference.
        
        if True:  
           
            if True:
                # slow but accurate ??
                # what happen ??
                # mask colors ?
           
                image = image.reshape(-1,3)
                image_no_bg = []   
                for x in image:
                    if not np.array_equal(x, [0, 0, 0]):
                        image_no_bg.append(x)
            else:
                image = image.reshape(-1,3)
                mask = (image[:,0]!=0) & (image[:,1]!=0) & (image[:,2]!=0)
                image_no_bg = np.copy(image[mask])
            
            #image_no_bg.reshape(-1,3)
            #idx = np.nonzero(image)
            #print idx
            #print  image[idx]
            #sys.exit()
          
            #image_no_bg=image[image!=[0,0,0]]
            #image_no_bg.reshape(1,3)
            
            #l = len(image_no_bg)
            #if l % 3 != 0:
            #    l = int (3 * math.ceil( l / 3.))
           
            #for i in range(l - len(image_no_bg)):
            #    empty = np.zeros(1,)
            #    image_no_bg = np.append(image_no_bg, empty, axis=0)
             
            #image_no_bg=image_no_bg.reshape(l/3,3)
        else:
            image_no_bg = image
            
        # opencv2 k-means cluster.
        
        #Z = image_no_bg.reshape((-1,3)) # not required after bg removed
        Z = image_no_bg
        Z = np.float32(Z)
        # define criteria, number of clusters(K) and apply kmeans()
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
        K = 5
        ret,labels,centers=cv2.kmeans(Z,K,None,criteria,10,cv2.KMEANS_RANDOM_CENTERS)
        hist = centroid_histogram(labels)

        # add to the array of colors
        #print "-" * 80
        for (percent, color) in zip(hist, centers):
            rcol = np.int8(np.round(color,0))
            colors.append([color])

        #cv2.imwrite('framedump-TEST/frame_%08d.png' % (frame_counter), img )

        if args.verbose:
            bar = plot_colors(hist, centers)
            #cv2.imshow("image",cv2.cvtColor(img_roi, cv2.COLOR_HSV2BGR))
            cv2.imshow("image", cv2.cvtColor(bar, cv2.COLOR_HSV2BGR))
            if cv2.waitKey(33) & 0xFF==ord('q'):
                break
            
        frame_counter += 1
        
        print "frame: ", frame_counter
        #if frame_counter >= 10:
        #    break

    print "Frames processed: ", frame_counter
    
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    K = 5
    Z = np.array(colors)
    ret,labels,centers=cv2.kmeans(Z,K,None,criteria,10,cv2.KMEANS_RANDOM_CENTERS)
    hist = centroid_histogram(labels)

    zipped = zip (hist, centers)
    zipped.sort(reverse=True, key=lambda x : x[0])
    hist, centers = zip(*zipped)
    
    # MASTER
      
    ind = np.arange(len(hist))
    
    colors_rgb = []
    print "=" * 80
    for (percent, color) in zip(hist, centers):
        #rcol = np.int8(np.round(color,0))
        a = np.uint8([[color]])
        x = cv2.cvtColor(a,cv2.COLOR_HSV2RGB)
        print "%.5f %s" % (percent, color)
        colors_rgb.append(x[0][0] / 255.0)
        
    distance = [[ None ] * len(centers)] * len(centers)
    for i in range(len(centers)-1):
        for j in range(i+1,len(centers)):
                    
            col_i = cv2.cvtColor(np.uint8([[centers[i]]]),cv2.COLOR_HSV2RGB)[0][0] / 255.0
            col_j = cv2.cvtColor(np.uint8([[centers[j]]]),cv2.COLOR_HSV2RGB)[0][0] / 255.0
           
            A_rgb = sRGBColor( col_i[0], col_i[1], col_i[2] )
            B_rgb = sRGBColor( col_j[0], col_j[1], col_j[2] )
    
            A = convert_color(A_rgb, LabColor)
            B = convert_color(B_rgb, LabColor)
         
            delta_e = delta_e_cie2000(A, B)
            distance[i][j] = [col_i, col_j, delta_e]
            print "(%s->%s) DE [%05.2f]%s -> %s" % (i,j, delta_e, np.round(col_i,2), np.round(col_j,2))
        
    
    vname = os.path.splitext(os.path.basename(args.element))[0]
    dname = os.path.dirname(args.element)
     
    l = plt.bar(ind, hist, linewidth=1, color=colors_rgb)
    plt.xlabel('Colors')
    plt.ylabel('Frequency')
    plt.title('Color Frequency [%s]' % vname)
    plt.grid(True)

    
    
    farg_np = "%s/%s" % (dname, vname)

    print("Writting to %s.png" % farg_np)
    print("Writting to %s.npy" % farg_np)
    print("Writting to %s_centers.npy" % farg_np)
    print("Writting to %s_colors.npy" % farg_np)
    print("Writting to %s_distance.npy" % farg_np)
    
    # save data for later.
    
    np.save("%s_hist" % farg_np, hist)
    np.save("%s_centers" % farg_np, centers)
    np.save("%s_colors" % farg_np, colors)
    np.save("%s_distance" % farg_np, distance)
    plt.savefig("%s.png" % farg_np)

    

