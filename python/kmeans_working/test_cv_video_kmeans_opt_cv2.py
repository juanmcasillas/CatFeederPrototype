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


    frame_counter = 0
    colors = []
    
    for video in args.input:

        print "Working on input [%s]" % video  

        cap = cv2.VideoCapture(video)
        frame_local = 0
        
        while True:
            result,img = cap.read()
            if not result:
                frame_counter += 1
                frame_local += 1
                break
           
            image = get_roi(img)
            image = remove_chroma(image)
            image = kmeans_resize(image, 100)
            image_nobg = kmeans_remove_bg(image)
                
            # opencv2 k-means cluster.
            
            hist,labels,centers = do_KMEANS(image_nobg, KCOLORS)
                    
            # add to the array of colors. Check that the color isn't in the array
            # by calculating the distance between existing colors and found colors.
            
            colors = add_colors_by_distance(hist, centers, colors, distance_max=2.0)
            
            #for (percent, color) in zip(hist, centers):
            #    rcol = np.int8(np.round(color,0))
            #    colors.append([color])
    
            #cv2.imwrite('framedump-TEST/frame_%08d.png' % (frame_counter), image )
    
            if args.verbose:
                bar = plot_colors(hist, centers)
                #cv2.imshow("image",cv2.cvtColor(img_roi, cv2.COLOR_HSV2BGR))
                cv2.imshow("image", cv2.cvtColor(bar, cv2.COLOR_HSV2BGR))
                if cv2.waitKey(33) & 0xFF==ord('q'):
                    break
                
            if frame_local % 25 == 0:
                print "frame: ", frame_local
            #if frame_counter >= 10:
            #    break
            
            frame_counter += 1
            frame_local += 1
    
    
    # END LOOP.
    # Process the "General" COLOR layout
    
    print "Frames processed: ", frame_counter
    print "Colors Found: ", len(colors)
    
    hist,labels,centers = do_KMEANS(np.array(colors), KCOLORS*2)
    
    
    zipped = zip (hist, centers)
    zipped.sort(reverse=True, key=lambda x : x[0])
    hist, centers = zip(*zipped)
    
    distance = kmeans_distance_between(centers)

    # create graphs

    ind = np.arange(len(hist))
    
    # compute the table 
    colors_rgb = []
    colors = []
  
    print "=" * 80
    for (percent, color) in zip(hist, centers):
        #rcol = np.int8(np.round(color,0))
        a = np.uint8([[color]])
        x = cv2.cvtColor(a,cv2.COLOR_HSV2RGB)
        print "%.5f %s" % (percent, color)
        colors_rgb.append(x[0][0] / 255.0)
        colors.append([np.round(color,0)])
        
    #vname = os.path.splitext(os.path.basename(args.element))[0]
    #dname = os.path.dirname(args.element)
    
    vname = args.id
    dname = 'videos'
     
     
    l = plt.bar(ind, hist, linewidth=1, color=colors_rgb, align="center")
    plt.xticks( ind,  map(lambda x: str(x), ind) )
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

