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
        parser.add_argument("-d", "--debug", help="Show debug info", action="store", default=logging.INFO)
        parser.add_argument("-o", "--host", help="Host running the server", action="store", default="localhost")
        parser.add_argument("-p", "--port", help="Port running the server", action="store", default=8088)
        parser.add_argument("-wp", "--wsock_port", help="Port running the server (WSOCK)", action="store", default=8089)
        parser.add_argument("-s", "--serial_port", help="Serial Port for Arduino", action="store", default='/dev/cu.wchusbserial1a1130')
        
        parser.add_argument("database", help="DatabaseFile")
        args = parser.parse_args()
        return args

    def Do_Checks(self,args):
        if not os.path.exists(args.database):
            print "Can't open database: '%s'. Bailing out" % (args.database)
            sys.exit(1)
        
    def Setup_Environment(self,args):
        logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s', level=args.debug) # args.debug
        HW.LOCK = threading.Lock()
        HW.instance = HW.Interface(args.serial_port)
     
        db.Connect(args.database)   
     

    
    

        
    
    def Init_Detector(self,args):
        """init the OPENCV interface"""
        detector.instance.Setup()
    
    
    def SaveEvent(self):
        e = db.Event()
        e.start = self.info.start_meal
        e.end =   self.info.end_meal
        e.rule =  self.info.ruleid
        e.petid = self.info.pet.id
        e.allowed = self.info.allowed
        e.photo   = self.info.photo
 
        db.EventService().Insert(e)
        db.Commit()
    
    
    def Run_Automatic(self):
        """do the operation cycle here. Remember that this run inside a loop and can be interrupted by MANUAL STATUS"""
        
        pet = detector.instance.Identify()
        print pet
         
    def Run_Manual(self):
        """the manual operation. Does nothing, because it's controlled by the web"""
        pass

if __name__ == "__main__":
    
    # raspberry run
    # python catfeeder_server.py catfeeder.db --serial_port='' --host=0.0.0.0

    server = CatFeederServer()

    args = server.Define_Arguments()
    server.Do_Checks(args)
    
    server.Setup_Environment(args)
    server.Init_Detector(args)
    HW.instance.SetAmbientLight_ON()
    
    while True:    

        server.Run_Automatic()
        time.sleep(1)