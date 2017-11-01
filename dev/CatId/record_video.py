#!/usr/bin/env python
import sys
import time
import argparse


from videotools import *
from recognizer import *
from check_pi import *
from cameratools import *

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help="Show images", action="store_true", default=False)
    parser.add_argument("-c", "--confidence", help="Confidence of the detection", action="store", type=int, default=20)
    parser.add_argument("-c:w", "--camera_width", help="Capture Width", action="store", type=int, default=800)
    parser.add_argument("-c:h", "--camera_height", help="Capture Height", action="store", type=int, default=608)
    parser.add_argument("-c:f", "--camera_fps", help="Frames per second", action="store", type=int, default=30)
    parser.add_argument("-c:r", "--camera_rotation", help="Camera Rotation", action="store", type=int, default=0)
    parser.add_argument("-d", "--duration", help="Duration, in seconds", action="store", type=int, default=10)
    parser.add_argument("video_file", help="output file for the video", default="video_output.mp4")
    args = parser.parse_args()

    camHandler = PiCameraHandler(resolution=(args.camera_width,args.camera_height), framerate=args.camera_fps, rotation=args.camera_rotation)
    
    if args.verbose:
        camera.start_preview()
    
    stamp = time.strftime("%H:%M:%S", time.localtime())
    print "Recording started at %s [%s]" % (stamp, args.video_file)
    
    camera.start_recording(args.video_file)
    time.sleep(args.duration)
    camera.stop_recording()
    
    if args.verbose:
        camera.stop_preview()
        
    stamp = time.strftime("%H:%M:%S", time.localtime())        
    print "Recording End at %s [%s]" % (stamp, args.video_file)