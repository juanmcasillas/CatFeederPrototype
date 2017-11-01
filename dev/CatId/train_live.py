#!/usr/bin/env python


import sys
import os.path
import argparse
from videotools import *
from recognizer import *
from check_pi import *


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help="Show images", action="store_true", default=False)
    parser.add_argument("-c", "--confidence", help="Confidence of the detection", action="store", type=int, default=20)
    parser.add_argument("-i", "--id", help="id for the subject", action="store", type=int,default=99)
    parser.add_argument("-l", "--label", help="Label of the detected element", action="store", default="default")
    parser.add_argument("-c:w", "--camera_width", help="Capture Width", action="store", type=int, default=800)
    parser.add_argument("-c:h", "--camera_height", help="Capture Height", action="store", type=int, default=608)
    parser.add_argument("-c:f", "--camera_fps", help="Frames per second", action="store", type=int, default=30)
    parser.add_argument("-c:r", "--camera_rotation", help="Camera Rotation", action="store", type=int, default=0)
    parser.add_argument("-nt", "--no_train", help="No train, just grab the images (default TRAIN)", action="store_true", default=False)
    parser.add_argument("output_file", help="output file for the trained data", default="trained_video.yml")
    parser.add_argument("output_dir", help="output directory for the images", default="images_output")
        
    args = parser.parse_args()

    recog = Recognizer(confidence=args.confidence)
    recog.Configure(minSize=(300,300))
    recog.PrintConfig()

    pos_frame = 0

    stats_total = 0
    stats_done = 0
    img_counter = 0

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

    if not os.path.exists(args.output_dir):
        print "Creating %s dir" % args.output_dir
        os.makedirs(args.output_dir)
                       
    #for result,im in camHandler.read():
    
    while True:
        result,img = camHandler.read()
        if not result:
            break

        img_annotated = recog.ExtractFace(args.id, img, "#%d" % pos_frame)        
        
        if len(img_annotated)>0:
            if args.verbose: cv2.imshow('im',img_annotated) 
            ftarget = "%s/%02d_%s-%d.jpg" % (args.output_dir, args.id,args.label,img_counter)
            cv2.imwrite(ftarget,img)
            print "writting: %s" % ftarget
            img_counter += 1
            stats_done +=1
            
        else:
            if args.verbose: cv2.imshow('im',img) 
            
        
        if not WaitForKeyToExit():
            break
        
        pos_frame += 1
        stats_total  +=1
        
    stats_percent = (stats_done * 100 / stats_total)
    print "%s Number of frames: %d, processed: %d, used: %3.2f %%" % ("-livel-", stats_total, stats_done, stats_percent)  
    cv2.destroyAllWindows()
    
    if not args.no_train:
        train_ok = recog.TrainAndSave(args.output_file)
        if not train_ok:
            print "Can't get anything to train. Bailing out"
            sys.exit(0)
    else:
        print "not trainning selected"
