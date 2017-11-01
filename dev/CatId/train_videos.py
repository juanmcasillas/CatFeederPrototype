#!/usr/bin/env python


import sys
import os.path
import argparse
from videotools import *
from recognizer import *


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help="Show images", action="store_true", default=False)
    parser.add_argument("video", help="Video to process")
    parser.add_argument("output_file", help="output file for the trained data", default="trained_video.yml")

    args = parser.parse_args()

    recog = Recognizer()



    if os.path.isdir(args.video):
        imagePaths=[os.path.join(args.video,f) for f in os.listdir(args.video)]
    else:
        imagePaths=[args.video]

    for imagePath in imagePaths:
    
        id,idlabel = recog.ExtractData(imagePath)
        if not id:
            print "Can't extract id from %s. check format (ID_name-SEQ.ext)" % imagePath
            sys.exit(1)
    
        cap = cv2.VideoCapture(imagePath)
        video_info = VideoInfo(cap, imagePath)
        video_info.PrintInfo()
    
        stats_total = video_info.frames
        stats_done = 0

    
        pos_frame = cap.get(cv2.CAP_PROP_POS_FRAMES)
    
        while True:
            flag, frame = cap.read()
            if flag:
                pos_frame = cap.get(cv2.CAP_PROP_POS_FRAMES)
            else:
                print "skipping frame..."
                cap.set(cv2.CAP_PROP_POS_FRAMES, pos_frame-1)
                cv2.waitKey(1000)
        
    
            img_annotated = recog.ExtractFace(id, frame, "#%d" % pos_frame)
            
            if len(img_annotated) > 0:
                stats_done +=1
            
            if args.verbose and len(img_annotated)>0:
                cv2.imshow('im',img_annotated) 
                cv2.waitKey(100)
    
            if cap.get(cv2.CAP_PROP_POS_FRAMES) == cap.get(cv2.CAP_PROP_FRAME_COUNT):
                break
          
        stats_percent = (stats_done * 100 / stats_total)
        print "%s Number of frames: %d, processed: %d, used: %3.2f %%" % (imagePath, stats_total, stats_done, stats_percent)  
        cap.release()
        cv2.destroyAllWindows()

    train_ok = recog.TrainAndSave(args.output_file)
        
    if not train_ok:
        print "Can't get anything to train. Bailing out"
        sys.exit(0)

    

