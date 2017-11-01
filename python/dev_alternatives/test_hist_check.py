# import the necessary packages
import matplotlib.pyplot as plt
import numpy as np
import argparse
import glob
import cv2


# construct the argument parser and parse the arguments
parser = argparse.ArgumentParser()
parser.add_argument("-d", "--dataset", help="Port running the server", action="store", required=True)
parser.add_argument("-i", "--image", help="Port running the server (WSOCK)", action="store", required=True)
        
args = parser.parse_args()



# initialize the index dictionary to store the image name
# and corresponding histograms and the images dictionary
# to store the images themselves
iindex = {}
images = {}
#args.image = filename = args.image[args.image.rfind("/") + 1:]

# loop over the image paths
iters = glob.glob(args.dataset + "/*.jpg")
if not args.image in iters:
    iters.append(args.image)
    
for imagePath in iters:

    # extract the image filename (assumed to be unique) and
    # load the image, updating the images dictionary
    filename = imagePath[imagePath.rfind("/") + 1:]
    image = cv2.imread(imagePath)
   
    #images[filename] = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    images[imagePath] = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    # extract a 3D RGB color histogram from the image,
    # using 8 bins per channel, normalize, and update
    # the index
    #hist = cv2.calcHist([image], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
    #hist = cv2.normalize(hist,hist).flatten()
    hist = cv2.calcHist([image], [0,1],None,[180,256],ranges=[0,180,0,256])
    #cv2.normalize(hist,hist,0,255,cv2.NORM_MINMAX)
    iindex[imagePath] = hist




# METHOD #1: UTILIZING OPENCV
# initialize OpenCV methods for histogram comparison
OPENCV_METHODS = (
    ("Correlation", cv2.HISTCMP_CORREL),        # bigger better
    ("Chi-Squared", cv2.HISTCMP_CHISQR),
    ("Intersection", cv2.HISTCMP_INTERSECT),    # bigger better
    ("Hellinger", cv2.HISTCMP_BHATTACHARYYA))   

results = {}
reverse = False


# loop over the index
for (k, hist) in iindex.items():
    # compute the distance between the two histograms
    # using the method and update the results dictionary
    d = cv2.compareHist(iindex[args.image], hist, cv2.HISTCMP_BHATTACHARYYA)
    results[k] = d

# sort the results
results = sorted([(v, k) for (k, v) in results.items()], reverse = reverse)

# loop over the results
for (i, (v, k)) in enumerate(results):
    # show the result
    print("%s: %.2f" % (k, v))
   
