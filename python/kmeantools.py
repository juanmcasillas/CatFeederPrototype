import cv2
from colormath.color_objects import LabColor, sRGBColor
from colormath.color_diff import delta_e_cie2000, delta_e_cie1976, delta_e_cmc
from colormath.color_conversions import convert_color
import numpy as np
import PIL
from cStringIO import StringIO
#from matplotlib import pyplot as plt
import pickle

#latest: 1.13.3
#mac: numpy 1.13.1
#py: 1.8.2
#win: 1.13.0

class O:
    def __init__(self): 
        pass

# constants

MAXIMUMS_SIZE = 2
bins = O()
bins.clipping = 10
bins.A = bins.B = bins.C = 128 
bins.Ac = bins.Bc = bins.Cc = bins.A + (bins.clipping * 2)
bins.sz = O()
bins.sz.A = bins.sz.B = bins.sz.C = 256


DB_DIR='data'
KMEANS_ITERATIONS = 10
KMEANS_IMAGE_SZ = 100

KCOLORS = 6 # 8
DELTA_E_RANGE = 10 # 9.5
NUM_IGNORE_COLORS = 2 # ignore 2 color (matched: LEN-2 = 3 colors)
FRAME_LIMIT = None


PERCENT_MATCH = 85 # 95, range 10
PERCENT_MATCH_THRESHOLD = 5
FRAMES_MATCH = 20


# ---
class DeltaECache:
    def __init__(self):
        self.cache = {}
        self.asks = 0
        self.hits = 0
        
    def Get(self, hsv, lab):
        
        self.asks += 1
        key = self.Key(hsv, lab)
        #print key
        if key in self.cache.keys():
            self.hits += 1
        else:
            col = cv2.cvtColor(np.uint8([[hsv]]),cv2.COLOR_HSV2RGB)[0][0] / 255.0
            A_rgb = sRGBColor( col[0], col[1], col[2] )
            A = convert_color(A_rgb, LabColor)
            #delta_e = delta_e_cie1976(A, lab) # big problem here with this. Implement some type of cache.
            delta_e = delta_e_cmc(A, lab) # FASTEST calculation and works fine.
            #delta_e = delta_e_cie2000(A, lab) # big problem here with this. Implement some type of cache.
            self.cache[key] = delta_e
        return self.cache[key]
                        
        
    def Key(self, A, B):
        s = "%03d:%03d:%03d|%3.1f:%3.1f:%3.1f" % (A[0],A[1],A[2],B.lab_l, B.lab_a, B.lab_b)
        # s = "%3.3f:%3.3f:%3.3f|%3.3f:%3.3f:%3.3f" % (A[0],A[1],A[2],B[0],B[1],B[2])
        return s

    def Store(self, fname):
        pickle.dump( self.cache, open( fname, "wb" ) )
        
    def Load(self, fname):
        return pickle.load( open( fname, "rb" ) )
        
    def LoadAndAppend(self, fname):
        items = self.Load(fname) 
        self.cache.update( items )
        print "[CACHE] Updated with %d items" % len(items)
        
DELTA_E_CACHE = DeltaECache()
 
        




def autolabel(rects):
    """
    Attach a text label above each bar displaying its height. MATPLOTLIB
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
    return img[:,:,:3] # RETURN RGB without ALPHA channel.


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


def get_roi(img):
    img_roi = img[30:608, 30:600] # ROI. Was rotated!!

    #130,100 X (x1,y1)
    #615,560 Y (x2,y2)
    #https://stackoverflow.com/questions/9084609/how-to-copy-a-image-region-using-opencv-in-python
    #If X(x1,y1) and Y(x2,y2) are the two opposite vertices of plate you obtained, then simply use function:
    #roi = gray[y1:y2, x1:x2]

    #img_roi = img[30:608, 30:600] # ROI. Was rotated!!
    img_roi = img[100:560, 130:615]
    #cv2.imwrite("roi2.png", img_roi)
    #sys.exit(0)
    
    return img_roi


def remove_chroma(img):
    
    
    #hsvMin = np.array([25, 43, 0],np.uint8) # BGR green box
    #hsvMax = np.array([180, 255, 255],np.uint8) # BGR green box

    hsvMin = np.array([38, 137, 0],np.uint8) # BGR
    hsvMax = np.array([72, 255, 255],np.uint8) # BGR
    
    img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(img, hsvMin, hsvMax)
    _, mask = cv2.threshold(mask,20, 255, cv2.THRESH_BINARY_INV)
    kernel = np.ones((5,5),np.uint8)
    mask = cv2.erode(mask, kernel, iterations=2)
    return cv2.bitwise_and(img,img,mask= mask)
   

def kmeans_resize(img, img_size_r):        
    h, w, _ = img.shape
    w_new = int(img_size_r * w / max(w, h) )
    h_new = int(img_size_r * h / max(w, h) )
    return cv2.resize(img, (w_new, h_new), interpolation = cv2.INTER_CUBIC);
    
    
def kmeans_remove_bg(image):
    # remove the background. Note that this changes the size and the shape
    # so I have to fill with "empty" values the difference.

    remove_bg = True
    use_for = False # it's working !
    
    if remove_bg:  
       
        if use_for:
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

    if len(image_no_bg) == 0 or len(image_no_bg) < KMEANS_ITERATIONS:
        return image
    

    return image_no_bg


def do_KMEANS(img, bins):
        #Z = image_no_bg.reshape((-1,3)) # not required after bg removed
        # define criteria, number of clusters(K) and apply kmeans()
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
        ret,labels,centers=cv2.kmeans(np.float32(img),bins,None,criteria,KMEANS_ITERATIONS,cv2.KMEANS_RANDOM_CENTERS)
        hist = centroid_histogram(labels)
        
        return hist,centers

def get_colors(centers, colors):
    for x in centers:
        colors.append(x)

    return colors

def add_colors_by_distance(hist, centers, colors, distance_max=1.0):
    
    
    # use only the adding for the master one.

    for (percent, color) in zip(hist, centers):
        #rcol = np.int8(np.round(color,0))
        colors.append([np.round(color,0)])
    return colors

    ## NOT REACHED ########################################

    # first time, add all the colors (no colors in array)
    if len(colors) == 0:
        for (percent, color) in zip(hist, centers):
            rcol = np.int8(np.round(color,0))
            colors.append([rcol])
        return colors


    #TOO_SLOW BECOUSE colors get big.    
    for i in range(len(centers)):

        for j in range(len(colors)):
            
            col_i = cv2.cvtColor(np.uint8([[ centers[i] ]]),cv2.COLOR_HSV2RGB)[0][0] / 255.0
            col_j = cv2.cvtColor(np.uint8([[ colors[j][0] ]]),cv2.COLOR_HSV2RGB)[0][0] / 255.0

            A_rgb = sRGBColor( col_i[0], col_i[1], col_i[2] )
            B_rgb = sRGBColor( col_j[0], col_j[1], col_j[2] )
    
            A = convert_color(A_rgb, LabColor)
            B = convert_color(B_rgb, LabColor)
         
            delta_e = delta_e_cie2000(A, B)
            c = np.int8(np.round(centers[i],0))
            if delta_e < distance_max and not [c] in np.array(colors):
                colors.append([c])
                #colors.append(np.int8(np.round(centers[i],0)))
                    
            
    return colors


    
def kmeans_distance_between(centers, verbose=False):
    distance = [[ None ] * len(centers)] * len(centers)
    for i in range(len(centers)-1):
        for j in range(i+1,len(centers)):
                    
            col_i = cv2.cvtColor(np.uint8([[centers[i]]]),cv2.COLOR_HSV2RGB)[0][0] / 255.0
            col_j = cv2.cvtColor(np.uint8([[centers[j]]]),cv2.COLOR_HSV2RGB)[0][0] / 255.0
           
            A_rgb = sRGBColor( col_i[0], col_i[1], col_i[2] )
            B_rgb = sRGBColor( col_j[0], col_j[1], col_j[2] )
    
            A = convert_color(A_rgb, LabColor)
            B = convert_color(B_rgb, LabColor)
         
            #delta_e = delta_e_cie2000(A, B)
            delta_e = delta_e_cmc(A, B) 
            distance[i][j] = [col_i, col_j, delta_e]
            if verbose:
                print "(%s->%s) DE [%05.2f]%s -> %s" % (i,j, delta_e, np.round(col_i,2), np.round(col_j,2))
    return distance

def GetUniqueColors(colors):
    mapped = {}
    ret = []
    for c in colors:
        key = "%03d%03d%03d" % (int(c[0]),int(c[1]), int(c[2]))
        
        if not key in mapped.keys():
            mapped[key] = True
            ret.append(c)
            
   
    return ret
    
    


def PrepareMasterColors(centers):
    
    
    colors = []
    for j in range(len(centers)):
           
        col = cv2.cvtColor(np.uint8([[centers[j]]]),cv2.COLOR_HSV2RGB)[0][0] / 255.0
        B_rgb = sRGBColor( col[0], col[1], col[2] )
        B = convert_color(B_rgb, LabColor)
      
        colors.append(B)

    return colors


def kmeans_distance_master_non_optimized(element_hist, element_centers, master_hist, master_centers):
    # distance to master colors 
    distance_master = []
    colors_found = []
    global DELTA_E_CACHE
     
    for i in range(len(element_centers)):
        
        col_values = []
        #element_percent = element_hist[i]
        
        for j in range(len(master_centers)):
            master_percent = master_hist[j]
                    
            col_i = cv2.cvtColor(np.uint8([[element_centers[i]]]),cv2.COLOR_HSV2RGB)[0][0] / 255.0
            col_j = cv2.cvtColor(np.uint8([[master_centers[j]]]),cv2.COLOR_HSV2RGB)[0][0] / 255.0 # optimization, not much significate.
   
            A_rgb = sRGBColor( col_i[0], col_i[1], col_i[2] )
            B_rgb = sRGBColor( col_j[0], col_j[1], col_j[2] )
    
            A = convert_color(A_rgb, LabColor)
            B = convert_color(B_rgb, LabColor)
         
            
            #delta_e = delta_e_cie2000(A, B) # big problem here with this. Implement some type of cache.
            delta_e = delta_e_cmc(A, B) # fastest calc 
             
            #distance_master[i][j] = [col_i, col_j, delta_e]
            #print "(E.%s->M.%s) DE [%05.2f]%s -> %s" % (i,j, delta_e, np.round(col_i,2), np.round(col_j,2)) 
            #if j not in colors_found:
            
            col_values.append( (delta_e, col_i, col_j, j, master_percent) ) # use master percent to calculate the distance value.
            
            #colors_found.append(j)
        
        # store the minimum value for each color, ordered by color
        # also not duplicate target results (e.g. 0->1 2->1 not. just one)
        #if col_values:
        result = min(col_values, key=lambda x: x[0])
        #distance_master.append(result)
        
        if result[3] not in colors_found:
            distance_master.append(result)
            colors_found.append(result[3])
        else:
            for i in range(len(distance_master)):
                s = distance_master[i]
                
                # 4 is the percent.
                if result[4] > s[4]:
                    # we have a max value. Change it.
                    distance_master[i] = result
                    break

    return distance_master


def kmeans_distance_master(element_centers, master_centers, master_hist=None ):
    # distance to master colors 
    distance_master = []
    colors_found = []
    global DELTA_E_CACHE
     

     
    for i in range(len(element_centers)):
        
        col_values = []
        #element_percent = element_hist[i]
        
        for j in range(len(master_centers)):
            master_percent = 0.0
            if master_hist is not None:
                master_percent = master_hist[j]
                    
            #col_i = cv2.cvtColor(np.uint8([[element_centers[i]]]),cv2.COLOR_HSV2RGB)[0][0] / 255.0
            #col_j = cv2.cvtColor(np.uint8([[master_centers[j]]]),cv2.COLOR_HSV2RGB)[0][0] / 255.0 # optimization, not much significate.
            B = master_centers[j] # color is precalculated.
           
            #A_rgb = sRGBColor( col_i[0], col_i[1], col_i[2] )
            #B_rgb = sRGBColor( col_j[0], col_j[1], col_j[2] )
    
            #A = convert_color(A_rgb, LabColor)
            #B = convert_color(B_rgb, LabColor)
         
            delta_e = DELTA_E_CACHE.Get(element_centers[i], master_centers[j])
            
            #delta_e = delta_e_cie2000(A, B) # big problem here with this. Implement some type of cache.
            
            #distance_master[i][j] = [col_i, col_j, delta_e]
            #print "(E.%s->M.%s) DE [%05.2f]%s -> %s" % (i,j, delta_e, np.round(col_i,2), np.round(col_j,2)) 
            #if j not in colors_found:
            #col_values.append( (delta_e, col_i, col_j, j, master_percent) ) # use master percent to calculate the distance value.
            
            col_values.append( (delta_e, j, master_percent) ) # use master percent to calculate the distance value.
            
            #colors_found.append(j)
        
        # store the minimum value for each color, ordered by color
        # also not duplicate target results (e.g. 0->1 2->1 not. just one)
        #if col_values:
        result = min(col_values, key=lambda x: x[0])
        #distance_master.append(result)
        
        
        if result[1] not in colors_found:
            distance_master.append(result)
            colors_found.append(result[1])
        else:
            for i in range(len(distance_master)):
                s = distance_master[i]
                
                # 4 is the percent.
                if result[2] > s[2]:
                    # we have a max value. Change it.
                    distance_master[i] = result
                    break
        


    return distance_master

# client


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