#!/usr/bin/env python

import sys
import argparse
import os


from recognizer import *
import videotools

if __name__ == "__main__":


    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--confidence", help="Confidence of the detection", action="store", type=int, default=30)
    parser.add_argument("-v", "--verbose", help="Show images", action="store_true", default=False)
    parser.add_argument("trained_file", help="output file for the trained data", default="trained_video.yml")
    parser.add_argument("img_file", help="File to test")
    args = parser.parse_args()
        
    recog = Recognizer(trained_file=args.trained_file, confidence=args.confidence)



    if os.path.isdir(args.img_file):
        imagePaths=[os.path.join(args.img_file,f) for f in os.listdir(args.img_file)]
    else:
        imagePaths=[args.img_file]
         
    stats_total = len(imagePaths)
    stats_done = 0         
        
    for imagePath in imagePaths:

        im = cv2.imread(imagePath)
        
        im_annotated, idmatch = recog.MatchFaces(im)
        
        print "%s: %s" % (imagePath,idmatch)
        if idmatch:
            stats_done += 1
        
        if args.verbose:
            cv2.imshow('im',im_annotated) 
            cv2.waitKey(1000)


    cv2.destroyAllWindows()
    stats_percent = (stats_done * 100 / stats_total)
    print "Number of images: %d, processed: %d, Success: %3.2f %%" % (stats_total, stats_done, stats_percent)
            