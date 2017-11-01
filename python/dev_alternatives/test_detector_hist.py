import time        
import datetime
import argparse
import os.path
import sys 
import webserver 
import hardware as HW
import threading
import logging
import wsock
import config
import detector
from db.rules import RuleService
import db
from db.pets import Pet
import cv2

class CatFeederServer:
    def __init__(self):
        
        self.info = config.O()
        self.info.pet = None
        self.info.photo = None
        self.info.start_meal = 0
        self.info.end_meal = 0
        self.info.ruleid = 0
        self.info.allowed = 0
        
        detector.instance = detector.Detector() 
        

    def Define_Arguments(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("-e", "--element", help="Camera Rotation", action="store")  
        parser.add_argument("-d", "--debug", help="Show debug info", action="store", default=logging.INFO) 
        parser.add_argument("-s", "--serial_port", help="Serial Port for Arduino", action="store", default='')
        parser.add_argument("-r", "--record", help="record video", action="store", type=int, default=5)
        args = parser.parse_args()
        return args



    
    def Init(self,args):
        """init the OPENCV interface"""
        logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s', level=args.debug) # args.debug
        detector.instance.Setup()

        HW.LOCK = threading.Lock()
        HW.instance = HW.Interface(args.serial_port)

if __name__ == "__main__":
    
    # raspberry run
    # python catfeeder_server.py catfeeder.db --serial_port='' --host=0.0.0.0

    server = CatFeederServer()

    args = server.Define_Arguments()

    server.Init(args)

    HW.instance.SetAmbientLight_ON()
    
    if args.record: 
        print "Recording %d seconds into %s.h264" % (args.record, args.element)
        detector.instance.camHandler.cam.start_recording('%s.h264' % args.element, format='h264', quality=25)
        detector.instance.camHandler.cam.wait_recording(args.record)
        detector.instance.camHandler.cam.stop_recording()
        
    else:
        # else grab pics    
        if not os.path.exists(args.element):
            os.makedirs(args.element)
                    
        imgs = []
        for i in range(60):
            result,img = detector.instance.camHandler.read()
            if not result:
                break
            print "frame %d" % i
            imgs.append(img[0:608, 0:640]) # ROI. Was rotated!!
            
        for i in range(60):
            p = '%s/%07d.jpg' % (args.element,i)
            cv2.imwrite(p, imgs[i])

    HW.instance.SetAmbientLight_OFF()