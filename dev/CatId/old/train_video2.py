#!/usr/bin/env python


import sys
import os.path
import argparse
from videotools import *
from recognizer import *


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--id", help="Id for the trainned video", action="store", type=int)
    parser.add_argument("video", help="Video to process")
    parser.add_argument("trained_file", help="output file for the trained data", default="trained_video.yml")
    args = parser.parse_args()

    recog = Recognizer()

    
    cap = cv2.VideoCapture(args.video)
    
    video_info = VideoInfo(cap, args.video)
    video_info.PrintInfo()

    faceSamples=[]
    #create empty ID list
    Ids=[]
    #now looping through all the image paths and loading the Ids and the images

    pos_frame = cap.get(cv2.CAP_PROP_POS_FRAMES)

    while True:
        flag, frame = cap.read()
        if flag:
            pos_frame = cap.get(cv2.CAP_PROP_POS_FRAMES)
        else:
            print "skipping frame..."
            cap.set(cv2.CAP_PROP_POS_FRAMES, pos_frame-1)
            cv2.waitKey(1000)
    

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)
        faces=recog.detector.detectMultiScale(frame, scaleFactor=1.3, minNeighbors=10, minSize=(200, 200))
    
        #If a face is there then append that in the list as well as Id of it
        for (x,y,w,h) in faces:
            print "(cat) Face Found at %d (id: %d)" % (pos_frame, args.id)
            cv2.rectangle(frame,(x,y),(x+w,y+h),(225,0,0),2)
            cv2.imshow('im',frame)
            faceSamples.append(gray[y:y+h,x:x+w])
            Ids.append(args.id)
            cv2.waitKey(100)
    
        if cap.get(cv2.CAP_PROP_POS_FRAMES) == cap.get(cv2.CAP_PROP_FRAME_COUNT):
            break


    cap.release()
    cv2.destroyAllWindows()

    recog.recognizer.train(faceSamples, np.array(Ids))
    recog.recognizer.save(args.trained_file)

