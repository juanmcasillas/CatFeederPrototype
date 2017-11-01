#https://github.com/tody411/ColorHistogram

from color_histogram.io_util.image import loadRGB
from color_histogram.core.hist_1d import Hist1D
import matplotlib.pyplot as plt
import cv2
import numpy as np

# Load image.
image_file = 'framedump-TEST/frame_00000059.png'
#image = loadRGB(image_file)

img = cv2.imread(image_file)

img_roi = img[30:608, 30:600] # ROI. Was rotated!!
#img_roi = cv2.bilateralFilter(img_roi,13,75,75)
img_roi = cv2.cvtColor(img_roi, cv2.COLOR_BGR2HSV)

hsvMin = np.array([25, 43, 0],np.uint8) # BGR green box
hsvMax = np.array([91, 255, 255],np.uint8) # BGR green box
mask = cv2.inRange(img_roi, hsvMin, hsvMax)

_, mask = cv2.threshold(mask,20, 255, cv2.THRESH_BINARY_INV)
kernel = np.ones((5,5),np.uint8)
mask = cv2.erode(mask, kernel, iterations=2)

hsv = cv2.bitwise_and(img_roi,img_roi,mask= mask)
#cv2.namedWindow('image')
img_rgb = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)
#cv2.imshow('image',hsv)

# 16 bins, Lab color space, target channel L ('Lab'[0])
hist1D_h = Hist1D(img_rgb, num_bins=90, color_space='hsv', channel=0)
hist1D_s= Hist1D(img_rgb, num_bins=90, color_space='hsv', channel=1)
hist1D_v = Hist1D(img_rgb, num_bins=90, color_space='hsv', channel=2)


figa = plt.figure()
ax = figa.add_subplot(111)
hist1D_h.plot(ax)

figb = plt.figure()
bx = figb.add_subplot(111)
hist1D_s.plot(bx)

figc = plt.figure()
cx = figc.add_subplot(111)
hist1D_v.plot(cx)
plt.show()