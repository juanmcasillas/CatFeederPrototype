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

from colormath.color_objects import LabColor, sRGBColor
from colormath.color_diff import delta_e_cie2000
from colormath.color_conversions import convert_color


class O:
    def __init__(self): 
        pass

def autolabel(rects):
    """
    Attach a text label above each bar displaying its height
    """
    for rect in rects:
        height = rect.get_height()
        plt.text(rect.get_x() + rect.get_width()/2., 1.00*height,
                '%.2f' % float(height),
                ha='center', va='bottom')


def Plot2Img(plt):
    buffer_ = StringIO()
    plt.savefig(buffer_, format = "png")
    buffer_.seek(0)
    image = PIL.Image.open(buffer_)
    img = np.asarray(image)
    buffer_.close()
    return img

def ComposeImage(topleft=None, topright=None, bottomleft=None, bottomright=None, resize=(680,480)):
# create big figure.

    imgs = [ topleft, topright, bottomleft, bottomright ]

  
    for i in range(len(imgs)):
        if imgs[i] is not None:
            imgs[i] = cv2.resize(imgs[i] ,resize, interpolation = cv2.INTER_CUBIC)
        else:
            imgs[i] = np.zeros((resize[1],resize[0],3), np.uint8)
  
   
    height = imgs[0].shape[0] + imgs[2].shape[0]
    width  = imgs[0].shape[1] + imgs[1].shape[1]
   
    #print "W: %3.2f, H: %3.2f" % (width, height)
    
    new_img = np.zeros((height,width,3), np.uint8)
    
    new_img[ 0:imgs[0].shape[0], 0:imgs[0].shape[1] ] = imgs[0]                                     #tl
    new_img[ 0:imgs[0].shape[0], imgs[0].shape[1]:imgs[0].shape[1] + imgs[1].shape[1] ] = imgs[1]    #tr
    new_img[ imgs[0].shape[0]:imgs[0].shape[0] + imgs[2].shape[0], 0:imgs[2].shape[1] ] = imgs[2]     #bl
    new_img[ imgs[0].shape[0]:imgs[0].shape[0] + imgs[3].shape[0], imgs[0].shape[1]:imgs[0].shape[1] + imgs[3].shape[1]] = imgs[3] #br
    
    return new_img

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


def TEST_ELEMENTS(Master, Element,  CV_MODE, verbose=True):
    """
    Master: name of the master element to check against (e.g. videos/firulais)
    Element: Data to test (e.g. videos/firulais)
    """
    
    OPENCV_METHODS = {
                      "correlation": cv2.HISTCMP_CORREL,        # bigger better
                      "chi-squared": cv2.HISTCMP_CHISQR,
                      "intersection": cv2.HISTCMP_INTERSECT,    # bigger better
                      "bhattacharyya": cv2.HISTCMP_BHATTACHARYYA
        }  
    
    CV_MODE_TYPE = OPENCV_METHODS[CV_MODE]
    
    # load things
    
    master = O()
    master.hist = np.load("%s_hist.npy" % Master)
    master.centers = np.load("%s_centers.npy" % Master)
    master.colors = np.load("%s_colors.npy" % Master)
    master.distance = np.load("%s_distance.npy" % Master)
    master.pngfile = "%s.png" % Master
    master.hist_img = cv2.imread(master.pngfile)
    master.hist_img = cv2.cvtColor(master.hist_img, cv2.COLOR_BGR2RGB)
    master.name = os.path.basename(Master)
    
    #for i in master.__dict__.keys():
    #    print "%s: %s" % (i, master.__dict__[i])
    
    cap = cv2.VideoCapture("%s.h264" % Element)

    hsvMin = np.array([25, 43, 0],np.uint8) # BGR green box
    hsvMax = np.array([91, 255, 255],np.uint8) # BGR green box
    #30/09/2017
    hsvMin = np.array([38, 137, 0],np.uint8) # BGR
    hsvMax = np.array([72, 255, 255],np.uint8) # BGR


    frame_counter = 0
    colors = []
    
    element = O()
    
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
            
        # opencv2 k-means cluster.
        
         
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
          
#             image_no_bg=image[image!=[0,0,0]]
#              
#             l = len(image_no_bg)
#             if l % 3 != 0:
#                 l = int (3 * math.ceil( l / 3.))
#             
#             for i in range(l - len(image_no_bg)):
#                 empty = np.zeros(1,)
#                 image_no_bg = np.append(image_no_bg, empty, axis=0)
#               
#             image_no_bg=image_no_bg.reshape(l/3,3)
            
        else:
            image_no_bg = image
                  


        # not needed
        #Z = image_no_bg.reshape((-1,3))
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
            #rcol = np.int8(np.round(color,0))
            #print "%.5f %s" % (percent, color)
            colors.append([color])

        #cv2.imwrite('framedump-TEST/frame_%08d.png' % (frame_counter), img )

        if args.verbose:
            bar = plot_colors(hist, centers)
            plt.figure()
            plt.axis("off")
            plt.imshow(bar)
            plt.show()

        frame_counter += 1

        # calculate distance
        zipped = zip (hist, centers)
        zipped.sort(reverse=True, key=lambda x : x[0])
        hist, centers = zip(*zipped)
        
        ###### GENERAL
          
       
        
        colors_rgb = []
        print "=" * 80
        for (percent, color) in zip(hist, centers):
            #rcol = np.int8(np.round(color,0))
            a = np.uint8([[color]])
            x = cv2.cvtColor(a,cv2.COLOR_HSV2RGB)
            print "%.5f %s" % (percent, color)
            colors_rgb.append(x[0][0] / 255.0)
            
        # distance between local colors
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
        
        element.hist = hist
        element.centers = centers
        element.colors = colors
        element.distance = distance
        element.pngfile = "%s.png" % Element
        element.name = os.path.basename(Element)
        
         
        # distance to master colors 
        distance_master = []
        for i in range(len(element.centers)):
            
            col_values = []
            
            for j in range(len(master.centers)):
                        
                col_i = cv2.cvtColor(np.uint8([[element.centers[i]]]),cv2.COLOR_HSV2RGB)[0][0] / 255.0
                col_j = cv2.cvtColor(np.uint8([[master.centers[j]]]),cv2.COLOR_HSV2RGB)[0][0] / 255.0
               
                A_rgb = sRGBColor( col_i[0], col_i[1], col_i[2] )
                B_rgb = sRGBColor( col_j[0], col_j[1], col_j[2] )
        
                A = convert_color(A_rgb, LabColor)
                B = convert_color(B_rgb, LabColor)
             
                delta_e = delta_e_cie2000(A, B)
                #distance_master[i][j] = [col_i, col_j, delta_e]
                #print "(E.%s->M.%s) DE [%05.2f]%s -> %s" % (i,j, delta_e, np.round(col_i,2), np.round(col_j,2)) 
                col_values.append( (delta_e, col_i, col_j, j) )
            
            
            # store the minimum value for each color, ordered by color
            distance_master.append(min(col_values, key=lambda x: x[0]))
            
        plt_labels = []
        plt_colors = []
        plt_data = []
        for i in range(len(distance_master)):
            delta_e, col_i, col_j, j = distance_master[i]
            print "*(E.%s->M.%s) DE [%05.2f]%s -> %s" % (i,j, delta_e, np.round(col_i,2), np.round(col_j,2)) 
            plt_labels.append("(E.%s->M.%s)" % (i,j)) 
            plt_colors.append(col_i)
            plt_data.append(delta_e)
                        
        ind = np.arange(len(hist)) 
        l = plt.bar(ind, hist, linewidth=1, color=colors_rgb)
        plt.xlabel('Colors')
        plt.ylabel('Frequency')
        plt.title('Color Frequency')
        plt.grid(True)        
        
        element.hist_img = Plot2Img(plt)
        plt.close('all')

  
        ind = np.arange(len(plt_labels))

        l = plt.bar(ind, plt_data, linewidth=1, color=plt_colors)
        plt.xticks( ind, plt_labels )
        plt.xlabel('Colors')
        plt.ylabel('Distance CIE2000')
        plt.title('Color distance Element->Master')
        plt.grid(True)   
        autolabel(l)     
        distance_master_img = Plot2Img(plt)
        
        
        

        img_output = ComposeImage(topleft=cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR), 
                                  topright=cv2.cvtColor(element.hist_img, cv2.COLOR_RGB2BGR), 
                                  bottomleft=cv2.cvtColor(master.hist_img, cv2.COLOR_RGB2BGR),
                                  bottomright=cv2.cvtColor(distance_master_img, cv2.COLOR_RGB2BGR))

        
        dirpath = 'framedump-%s-%s' % (master.name,element.name)
        if not os.path.exists(dirpath):
            os.makedirs(dirpath)
        fname = '%s/frame_%08d.png' % (dirpath, frame_counter)
        cv2.imwrite(fname, img_output )
        plt.close('all')



        # Wait longer to prevent freeze for videos.
        if args.verbose:
            if cv2.waitKey(10) & 0xFF == ord('q'):
                break

        print frame_counter
        if frame_counter > 10:
            break

    print "Frames processed: ", frame_counter

    if args.verbose:
        cv2.destroyAllWindows()   
  
        


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--element", help="Histogram", action="store")  
    parser.add_argument("-v", "--verbose", help="run metrics", action="store_true")
    parser.add_argument("-f", "--function", help="CV method function", action="store", default="bhattacharyya")
    args = parser.parse_args()    
    
    METHOD = 'correlation'    #bigger, better
    #METHOD = 'intersection'  #bigger, better
    #METHOD = 'bhattacharyya'
    #METHOD = 'chi-squared'

    # build the CSV matrix.
    #ROWS = [ 'neko', 'neko2', 'neko3', 'eli', 'firulais', 'firulais2', 'firulais3', 'blue_ball', 'red_jar', 'hand', 'empty']
    #COLS = [ 'neko', 'neko2', 'neko3', 'eli', 'firulais', 'firulais2', 'firulais3'] 
    #COEFS = { 'neko': [0.762,0.605,0.905], 'eli': [0.764,0.764,0.764], 'firulais': [0.502,0.224,0.821] } #correlation mode, bigger, better
    
    ROWS = [ 'neko', 'neko2', 'eli', 'eli2', 'firulais', 'firulais2', 'blue_ball', 'red_jar', 'hand' ]
    COLS = [ 'neko', 'neko2', 'eli', 'eli2', 'firulais', 'firulais2', 'blue_ball', 'red_jar', 'hand' ]
    
    #ROWS = [ 'blue_ball' ]
    #COLS = [ 'blue_ball' ]
        
    for r in range(len(ROWS)):
        for c in range(len(COLS)):
            result = TEST_ELEMENTS("videos/%s" % ROWS[r], "videos/%s" % COLS[c], METHOD, verbose=args.verbose)
            
        print ""