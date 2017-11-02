#!/usr/bin/env python
import sys
import time
import argparse

from videotools import *
from recognizer import *
from check_pi import *

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help="Show images", action="store_true", default=False)
    parser.add_argument("-c", "--confidence", help="Confidence of the detection", action="store", type=int, default=30)
    parser.add_argument("-c:w", "--camera_width", help="Capture Width", action="store", type=int, default=800)
    parser.add_argument("-c:h", "--camera_height", help="Capture Height", action="store", type=int, default=608)
    parser.add_argument("-c:f", "--camera_fps", help="Frames per second", action="store", type=int, default=30)
    parser.add_argument("-c:r", "--camera_rotation", help="Camera Rotation", action="store", type=int, default=0)
    parser.add_argument("trained_file", help="output file for the trained data", default="trained_video.yml")
    args = parser.parse_args()

    recog = Recognizer(trained_file=args.trained_file, confidence=args.confidence)

    if IsRaspberry():
        from cameratools import *
        camHandler = PiCameraHandler(resolution=(args.camera_width,args.camera_height), framerate=args.camera_fps, rotation=args.camera_rotation)
        print "Using Raspberry Camera"
    else:
        camHandler = cv2.VideoCapture(0)
        camHandler.set(cv2.CAP_PROP_FRAME_WIDTH, args.camera_width)
        camHandler.set(cv2.CAP_PROP_FRAME_HEIGHT, args.camera_height)
        camHandler.set(cv2.CAP_PROP_FPS, args.camera_fps)
                
        print "Using Generic Webcam"
                       
    #for result,im in camHandler.read():
    while True:
        result,im = camHandler.read()
        if not result:
            break
        
        im_annotated, idmatch = recog.MatchFaces(im)
        if idmatch:
            print idmatch
        
        if args.verbose:
            cv2.imshow('im',im_annotated) 
 
        if not WaitForKeyToExit():
            break
    
    cv2.destroyAllWindows()
