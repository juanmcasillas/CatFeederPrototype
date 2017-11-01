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

from kmeantools import * 


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


if __name__ == "__main__":

    
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--id", help="Id of the learn", action="store")
    parser.add_argument("-v", "--verbose", help="verbose mode", action="store_true")
    parser.add_argument('input', nargs='+')
    args = parser.parse_args()

    if args.verbose:
        cv2.namedWindow("image")

    img = O()


    frame_counter = 0
    colors = []
    hist_3d =   np.array([ np.zeros([bins.Ac]), np.zeros([bins.Bc]), np.zeros([bins.Cc]) ])
    hist_3d_m = np.array([ np.zeros([bins.Ac]), np.zeros([bins.Bc]), np.zeros([bins.Cc]) ])
    hist_3d_c = np.array([ np.zeros([bins.A]), np.zeros([bins.B]), np.zeros([bins.C]) ]) # clipped hist.
    
    for video in args.input:

        print "Working on input [%s]" % video  

        cap = cv2.VideoCapture(video)
        frame_local = 0
        
        while True:
            result,img.bgr = cap.read()
            if not result:
                frame_counter += 1
                frame_local += 1
                break
           
            img.roi = get_roi(img.bgr)
            img.chroma = remove_chroma(img.roi)
            img.chroma = kmeans_resize(img.chroma, KMEANS_IMAGE_SZ)
            #img.chroma = cv2.cvtColor(img.chroma, cv2.COLOR_BGR2HSV)
            #img.bgr = cv2.cvtColor(img.chroma, cv2.COLOR_HSV2BGR)
            #img.lab = cv2.cvtColor(img.chroma, cv2.COLOR_BGR2LAB)
            img.lab = cv2.cvtColor(img.chroma, cv2.COLOR_HSV2BGR)
            
            hist = O()
            hist.A = cv2.calcHist([img.lab],[0],None,[bins.Ac],[0,bins.sz.A])
            hist.B = cv2.calcHist([img.lab],[1],None,[bins.Bc],[0,bins.sz.B])
            hist.C = cv2.calcHist([img.lab],[2],None,[bins.Cc],[0,bins.sz.C])
    
            hist_3d[0] = hist.A.reshape((bins.Ac))
            hist_3d[1] = hist.B.reshape((bins.Bc))
            hist_3d[2] = hist.C.reshape((bins.Cc))
    
            #hist_3d = hist_3d.astype("float")
            #hist_3d /= hist_3d.sum()    
            
            if frame_counter == 0:
                hist_3d_m[0] = hist_3d[0]
                hist_3d_m[1] = hist_3d[1]
                hist_3d_m[2] = hist_3d[2]
            else:
                hist_3d_m[0] += hist_3d[0]
                hist_3d_m[1] += hist_3d[1]
                hist_3d_m[2] += hist_3d[2]
            
            if frame_local % 30 == 0:
                print "frame: ", frame_local
            #if frame_counter >= 10:
            #    break
            
            frame_counter += 1
            frame_local += 1
    
    # END LOOP.
    # Process the "General" COLOR layout

    # clipping 
    
    if True:
        for i in range(3):
            tmp = hist_3d_m[i][bins.clipping::]
            hist_3d_c[i] = tmp[0:-bins.clipping:]
            
        
    hist_3d_c = hist_3d_c.astype("float")
    hist_3d_c /= hist_3d_c.sum()  
 

    # plot

    series = { 'A': ['r', 'Lab'], 'B': ['g','A'], 'C': ['b', 'B'] }
    l_handles = []
    
    f, plots = plt.subplots(3, sharex=True, sharey=True)
    plots[0].set_title('Histogram LAB')
  
    maximums = []

    for i,serie in enumerate(('A','B','C')):

        col = series[serie][0]
        tit = series[serie][1]
        
        ind = np.arange(len(hist_3d_c[i]))
        #h = plots[i].bar(ind, hist_3d_m[i], color="#cacaca", label=tit)
        plots[i].plot(hist_3d_c[i], color=col, label=tit, linewidth=1.2)
        
        max_array = np.argpartition(hist_3d_c[i], -MAXIMUMS_SIZE)[-MAXIMUMS_SIZE:]  # maximum
        maximums.append(max_array)
        
        for am in max_array:
            plots[i].axvline(am, color='#9E7a7a', linestyle='dashed', linewidth=1.0)
        
        plots[i].set_title(tit,loc='right',fontsize=10)
        plots[i].grid(True)
    
    
    f.subplots_adjust(hspace=0)
    plt.setp([a.get_xticklabels() for a in f.axes[:-1]], visible=False)
    #plt.show()
    
    vname = args.id
    dname = DB_DIR
    
    farg_np = "%s/%s" % (dname, vname)

    print("Writting to %s.png" % farg_np)
    print("Writting to %s.npy" % farg_np)
    #print("Writting to %s_centers.npy" % farg_np)
    #print("Writting to %s_cache.pickle" % farg_np)
    #print("Writting to %s_colors.npy" % farg_np)
    #print("Writting to %s_distance.npy" % farg_np)
    
    # save data for later.
    
    np.save("%s_hist" % farg_np, hist_3d_c)
    #np.save("%s_centers" % farg_np, centers)
    #np.save("%s_colors" % farg_np, colors)
    #np.save("%s_distance" % farg_np, distance)
    plt.savefig("%s.png" % farg_np)
    #DELTA_E_CACHE.Store('%s_cache.pickle' % farg_np)
