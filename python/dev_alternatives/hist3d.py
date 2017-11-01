from color_histogram.io_util.image import loadRGB
from color_histogram.core.hist_3d import Hist3D
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import cv2
import numpy as np

# Load image.

hsvMin = np.array([25, 43, 0],np.uint8) # BGR green box
hsvMax = np.array([91, 255, 255],np.uint8) # BGR green box

image_file="framedump-TEST/frame_00000000.png"
img = cv2.imread(image_file)
img_roi = img[30:608, 30:600] # ROI. Was rotated!!
#img_roi = cv2.bilateralFilter(img_roi,13,75,75)
img_roi = cv2.cvtColor(img_roi, cv2.COLOR_BGR2HSV)
mask = cv2.inRange(img_roi, hsvMin, hsvMax)
_, mask = cv2.threshold(mask,20, 255, cv2.THRESH_BINARY_INV)
kernel = np.ones((5,5),np.uint8)
mask = cv2.erode(mask, kernel, iterations=2)
hsv = cv2.bitwise_and(img_roi,img_roi,mask= mask)

#rgb = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)

#histogram 3d
bins_A = bins_B = bins_C = 16
lims_A = lims_B = lims_C = 256
lims_A = 128
hist = cv2.calcHist([hsv],[0,1,2],None,[bins_A,bins_B,bins_C],[0, lims_A, 0, lims_B, 0, lims_C])

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# Construct arrays for the anchor positions of the 16 bars.
# Note: np.meshgrid gives arrays in (ny, nx) so we use 'F' to flatten xpos,
# ypos in column-major order. For numpy >= 1.7, we could instead call meshgrid
# with indexing='ij'.
#xpos, ypos = np.meshgrid(xedges[:-1] + 0.25, yedges[:-1] + 0.25)
#xpos = xpos.flatten('F')
#ypos = ypos.flatten('F')
#zpos = np.zeros_like(xpos)

# Construct arrays with the dimensions for the 16 bars.
#dx = 0.5 * np.ones_like(zpos)
#dy = dx.copy()
#dz = hist.flatten()

ax.contourf3D(hist[0], hist[1], hist[2])
plt.show()

# 16 bins, rgb color space
#hist3D = Hist3D(rgb, num_bins=128, color_space='rgb')
#fig = plt.figure()
#ax = fig.add_subplot(111, projection='3d')
#hist3D.plot(ax)
#plt.show()

