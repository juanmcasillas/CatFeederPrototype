import cv2
import argparse
import numpy as np
import matplotlib
#matplotlib.use('Agg')

from matplotlib import pyplot as plt
import glob
from numpy import nan
import math
import os


from kmeantools import *


def TEST_ELEMENTS(Master, Element,  CV_MODE, verbose=True, drawit=False):
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

    frame_counter = 0
    colors = []
    
    element = O()
    
    #scores
    matched_frames = 0
    matched_avg = 0.0
    
    nonmatched_frames = 0
    nonmatched_avg = 0.0
    

    
    while True:
        result,img = cap.read()
        if not result:
            break

        
        image = get_roi(img)
        image = remove_chroma(image)
        image = kmeans_resize(image, 100)
        image_nobg = kmeans_remove_bg(image)
         
        # opencv2 k-means cluster.
        
        hist,labels,centers = do_KMEANS(image_nobg, KCOLORS)



        #cv2.imwrite('framedump-TEST/frame_%08d.png' % (frame_counter), img )

        if drawit:

            # add to the array of colors
            #print "-" * 80
            for (percent, color) in zip(hist, centers):
                #rcol = np.int8(np.round(color,0))
                #print "%.5f %s" % (percent, color)
                #rcol = np.int8(np.round(color,0))
                colors.append([color])            
                
            bar = plot_colors(hist, centers)
            #cv2.imshow("image",cv2.cvtColor(img_roi, cv2.COLOR_HSV2BGR))
            cv2.imshow("image", cv2.cvtColor(bar, cv2.COLOR_HSV2BGR))
            if cv2.waitKey(33) & 0xFF==ord('q'):
                break

        frame_counter += 1

        # calculate distance
        zipped = zip (hist, centers)
        zipped.sort(reverse=True, key=lambda x : x[0])
        hist, centers = zip(*zipped)
        
        colors_rgb = []
        #print "=" * 80
        for (percent, color) in zip(hist, centers):
            a = np.uint8([[color]])
            x = cv2.cvtColor(a,cv2.COLOR_HSV2RGB)
            #print "%.5f %s" % (percent, color)
            colors_rgb.append(x[0][0] / 255.0)
        
        distance = kmeans_distance_between(centers)    
        
        element.hist = hist
        element.centers = centers
        element.colors = colors or []
        element.distance = distance
        element.pngfile = "%s.png" % Element
        element.name = os.path.basename(Element)
        
        # IDEA: calculate the distance pondered with the ditribution of the color.
        # TODO. include also the distribution (hist) in  the calc.
        
        distance_master = kmeans_distance_master(element.hist, element.centers, master.hist, master.centers)
  
        ##
        ## use the distance_master_img to calculate the "difference" between images.
        ## also ...  
        ## plot things and create the master picture.
        ##
        ##
        ##----------------------------------------------------------------------
        
        plt_labels = []
        plt_colors = []
        plt_data = []
        
        local_matches = 0
        local_avg = 0.0
        
        local_nonmatches = 0
        local_avg_nonmatched = 0.0
               
        for i in range(len(distance_master)):
            delta_e, col_i, col_j, j, percent = distance_master[i]
            #print "*(E.%s->M.%s) DE [%05.2f]%s -> %s" % (i,j, delta_e, np.round(col_i,2), np.round(col_j,2)) 
            plt_labels.append("%s->%s" % (i,j)) 
            plt_colors.append(col_i)
            plt_data.append(delta_e)
        
            if verbose:
                print "(E.%s->M.%s) DE [%05.2f]%s -> %s [%.3f%%] [%.3f]" % (i,j, delta_e, np.round(col_i,2), np.round(col_j,2), percent, delta_e)
        
            #if delta_e - (delta_e * percent) <= DELTA_E_RANGE:
            if delta_e <= DELTA_E_RANGE:
                local_matches += 1
                local_avg += delta_e
            else:
                local_nonmatches += 1
                local_avg_nonmatched += delta_e 
        
        # this matches the minimum required number of colors to match.

        #master_colors_size = len(master.centers)
        #element_colors_size = len(element.centers)
        #matched_distance_size = len(distance_master)

        
        min_colors = int((len(master.centers) - NUM_IGNORE_COLORS) / 2.0)
        #print min_colors
                       
        if  local_matches >= min_colors:
            matched_frames += 1
            matched_avg += local_avg
            if verbose:
                print "Matched: %d frames, %.3f avg" % (matched_frames, matched_avg) 
        else:
            nonmatched_frames +=1
            nonmatched_avg += local_avg_nonmatched
            if verbose:
                print "NOT Matched: %d frames, %.3f avg" % (nonmatched_frames, nonmatched_avg)
        
        
        # stats
        
        
        if local_matches > 0:
            local_avg = local_avg / float(local_matches)
        else:
            local_avg = nan
                
        if local_nonmatches > 0:
            local_avg_nonmatched = local_avg_nonmatched / float(local_nonmatches)
        else:
            local_avg_nonmatched = nan
        
        

             
        if verbose: 
            print "MatchAVG: %.3f with %d colors / nonmatched: %.3f [%d]" % (local_avg, local_matches, local_avg_nonmatched, local_nonmatches)
        
       
        ##----------------------------------------------------------------------
        #
        # now plot things
        # 
        
                        
        ind = np.arange(len(hist)) 
        l = plt.bar(ind, hist, linewidth=1, color=colors_rgb, align="center")
        plt.xticks( ind,  map(lambda x: str(x), ind) )
        plt.xlabel('Colors')
        plt.ylabel('Frequency')
        plt.title('Color Frequency')
        plt.grid(True)        
       
        element.hist_img = Plot2Img(plt)
        
        plt.close('all')

        ind = np.arange(len(plt_labels))

        l = plt.bar(ind, plt_data, linewidth=1, color=plt_colors, align="center")
        plt.xticks( ind, plt_labels )
        plt.xlabel('Colors')
        plt.ylabel('Distance CIE2000')
        plt.title('Color distance Element->Master')
        plt.grid(True)   
        autolabel(l)     
        distance_master_img = Plot2Img(plt)
  
        #cv2.imshow('image', cv2.cvtColor(element.hist_img, cv2.COLOR_RGB2BGR))
        #if cv2.waitKey(33) & 0xFF==ord('q'):
        #    break
        
        img_output = ComposeImage(topleft=cv2.cvtColor(image, cv2.COLOR_HSV2BGR), 
                                  topright=cv2.cvtColor(element.hist_img, cv2.COLOR_RGB2BGR), 
                                  bottomleft=cv2.cvtColor(master.hist_img, cv2.COLOR_RGB2BGR),
                                  bottomright=cv2.cvtColor(distance_master_img, cv2.COLOR_RGB2BGR))

        
        dirpath = 'framedump-%s-%s' % (master.name,element.name)
        if not os.path.exists(dirpath):
            os.makedirs(dirpath)
        fname = '%s/frame_%08d.png' % (dirpath, frame_counter)
        cv2.imwrite(fname, img_output )
        plt.close('all')

        if frame_counter % 25 == 0:
                print "frame: ", frame_counter
        if FRAME_LIMIT and frame_counter > FRAME_LIMIT:
            break


    #
    # END LOOP.

    percent = matched_frames*100.0/ float(frame_counter)
   

    if matched_frames != 0:
        matched_avg = matched_avg / float(matched_frames)
    else:
        matched_avg = matched_avg / float(frame_counter)
    
    if verbose:
        print "Frames processed: ", frame_counter
        print "Matches: %d/%d frames %.2f%%" % (matched_frames, frame_counter, percent)
    
    if drawit:
        cv2.destroyAllWindows()   
    
    return frame_counter, matched_frames, matched_avg, percent
        

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
    
    #ROWS = [ 'neko', 'neko2', 'eli', 'eli2', 'firulais', 'firulais2', 'blue_ball', 'red_jar', 'hand' ]
    #COLS = [ 'neko', 'neko2', 'eli', 'eli2', 'firulais', 'firulais2', 'blue_ball', 'red_jar', 'hand' ]
    
    #ROWS = [ 'blue_ball' ]
    #COLS = [ 'blue_ball' ]
    
    ROWS = [ 'firulais','neko', 'eli' ]
    COLS = [ 'neko', 'firulais', 'eli' ]
        
    for r in range(len(ROWS)):
        for c in range(len(COLS)):
            frame_counter,matched_frames,avg, percent = TEST_ELEMENTS("videos/%s" % ROWS[r], "videos/%s" % COLS[c], METHOD, verbose=args.verbose)
            print "%s vs %s %.3f%% %d/%d matched/total %.3f avg" % (ROWS[r], COLS[c], percent, matched_frames, frame_counter, avg) 
            
        print ""