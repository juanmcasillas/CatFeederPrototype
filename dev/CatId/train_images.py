#!/usr/bin/env python

import argparse
import sys
import os

from PIL import Image

from recognizer import *

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help="Show images", action="store_true", default=False)
    parser.add_argument("image_path", help="Directory with images in id_name-seq.jpg format (can be a file)")
    parser.add_argument("output_file", help="Output file for the trained net", default="trained.yml")
    args = parser.parse_args()
    
    recog = Recognizer()
    recog.Configure(minSize=(300,300)) # to fix small faces artifacts
    recog.PrintConfig()
    
    imagePaths=[os.path.join(args.image_path,f) for f in os.listdir(args.image_path)] 
    
    stats_total = len(imagePaths)
    stats_done = 0
    
    for imagePath in imagePaths:
        

        id, idlabel = recog.ExtractData(imagePath)
        if not id:
            print "Can't extract id from %s. check format (ID_name-SEQ.ext)" % imagePath
            sys.exit(1)
        

        img = cv2.imread(imagePath) # read in color cv2.IMREAD_GRAYSCALE
        
        #hist_red = cv2.calcHist([img],[0],None,[256],[0,256]) 
        #hist_green = cv2.calcHist([img],[1],None,[256],[0,256]) 
        #hist_blue = cv2.calcHist([img],[2],None,[256],[0,256])
        
        
        
        
        img_annotated = recog.ExtractFace(id, img, imagePath)
        
        if len(img_annotated) > 0:
            stats_done +=1
        
        if args.verbose and len(img_annotated)>0:
            cv2.imshow('im',img_annotated) 
            cv2.waitKey(100)

    stats_percent = (stats_done * 100 / stats_total)
    print "Number of images: %d, processed: %d, used: %3.2f %%" % (stats_total, stats_done, stats_percent)
        
    train_ok = recog.TrainAndSave(args.output_file)
    if not train_ok:
        print "Can't get anything to train. Bailing out"
        sys.exit(0)    
    
    
    #im_annotated = recog.MatchFaces(im)
    #cv2.imshow('im',im_annotated) 

    #while True:
    #    if cv2.waitKey(10) &  0xFF==ord('q'):
    #        break
    #cv2.destroyAllWindows()


