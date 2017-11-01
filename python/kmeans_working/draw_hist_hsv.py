# import the necessary packages
import matplotlib.pyplot as plt
import numpy as np
import argparse
import glob
import cv2
import sys


# construct the argument parser and parse the arguments
parser = argparse.ArgumentParser()
parser.add_argument("-d", "--dataset", help="Port running the server", action="store", required=True)
parser.add_argument("-r", "--remove", help="Port running the server", action="store", required=True)
        
args = parser.parse_args()



# initialize the index dictionary to store the image name
# and corresponding histograms and the images dictionary
# to store the images themselves
iindex = {}
images = {}
cv2.namedWindow('hist')
cv2.namedWindow('img')
remove_img = cv2.imread(args.remove)
remove_hsv = cv2.cvtColor(remove_img, cv2.COLOR_BGR2HSV)


# loop over the image paths
for imagePath in glob.glob(args.dataset + "/*.jpg"):
    # extract the image filename (assumed to be unique) and
    # load the image, updating the images dictionary
    filename = imagePath[imagePath.rfind("/") + 1:]
    image = cv2.imread(imagePath)
    images[filename] = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    
    
    delta = cv2.subtract(images[filename], remove_hsv)
    delta = cv2.cvtColor(delta, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(delta, 20, 255, cv2.THRESH_BINARY)[1]
    thresh = cv2.dilate(thresh, None, iterations=2)
    
    #delta = cv2.cvtColor(delta, cv2.COLOR_BGR2GRAY)
    
    images[filename] = cv2.bitwise_and(images[filename], images[filename], mask = thresh) # to remove (debug)
        

    color = ('b','g','r')
    
 
    #for i,col in enumerate(color):
        # hist = cv2.calcHist([image], [i],None,[256],[0,256])
    hist = cv2.calcHist( [images[filename]], [0,1], None, [180, 256], [0, 180, 0, 256] )
    plt.plot(hist,color='r')
    #plt.imshow(hist, interpolation='nearest')
    #cv2.imshow('hist', hist)
    #cv2.imshow('img', images[filename])
    #plt.show()
    
    #key = cv2.waitKey(200)
    #if key == 27 or key==ord('q'):
    #    break
    
    #plt.xlim([0,256])
    
plt.show()
    