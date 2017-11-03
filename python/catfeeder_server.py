import time        
import datetime
import argparse
import os.path
import sys 
import webserver 
import hardware as HW
import threading
import logging
import logging.config
import wsock
import config
import detector
from db.rules import RuleService
import db
import hardware
import ipnetutils

class CatFeederServer:
    def __init__(self):
        
        self.info = config.O()
        self.info.pet = None
        self.info.photo = None
        self.info.start_meal = 0
        self.info.end_meal = 0
        self.info.ruleid = 0
        self.info.allowed = 0
        
        self.wait_time = 0
        detector.instance = detector.Detector() 
        

    def Define_Arguments(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("-d", "--debug", help="Show debug info", action="store", default=logging.INFO)
        parser.add_argument("-o", "--host", help="Host running the server", action="store", default=ipnetutils.get_default_ip())
        parser.add_argument("-p", "--port", help="Port running the server", action="store", default=8088)
        parser.add_argument("-D", "--dummy", help="Run in dummy mode (no hardware attached)", action="store_true", default=False)
        #parser.add_argument("-wp", "--wsock_port", help="Port running the server (WSOCK)", action="store", default=8089)
        parser.add_argument("-s", "--serial_port", help="Serial Port for Arduino", action="store", default='/dev/cu.wchusbserial1a1130')
        
        parser.add_argument("database", help="DatabaseFile")
        args = parser.parse_args()
        
        return args

    def Do_Checks(self,args):
        if not os.path.exists(args.database):
            print "Can't open database: '%s'. Bailing out" % (args.database)
            sys.exit(1)
        
    def Setup_Environment(self,args):
        
        
        HW.LOCK = threading.Lock()
        HW.instance = HW.Interface(args.serial_port)
        db.Connect(args.database)   
        
        
        logging.basicConfig(level=args.debug,
                    format='%(asctime)s [%(levelname)s] %(message)s',
                    datefmt='%m/%d/%Y %H:%M:%S',
                    )
        
        logging.getLogger().setLevel(args.debug)
        root = logging.getLogger()
        hdlr = root.handlers[0]
        fmt = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
        hdlr.setFormatter(fmt)
        fh = logging.FileHandler(config.LOG_FILE, mode=config.LOG_FILE_MODE)
        fh.setFormatter(fmt)
        root.addHandler(fh)
        logging.info("Setup_Environment() done.")
        
     
    def Start_WebServer(self,args):
        
        logging.info("Start_WebServer()")
        opts = webserver.www.Opts()
        opts.host = args.host
        opts.port = args.port
        opts.rootdir = config.www.root
        opts.no_dirlist = False
        opts.level = args.debug
        
        #opts.nocache = False
        #opts.cachedir = '.'
        #opts.dbfile = args.database
    
        #webserver.start_www_server_standalone(opts)
        webserver.start_www_server_thread(opts)
    
        # for testing the presence only
        # wsock.websocketserver_start(args.host,int(args.wsock_port))
    
    
    def Init_Hardware(self,args=None):
        """Reset the HW (Arduino) to default settings"""
        
        # for testing the interface. Works.
        #HW.instance.detector = 1
        #HW.instance.door_open = 1
        #HW.instance.door_closed = 1
        
        # start with door OPEN
        # lights off
        
        logging.info("Init_Hardware()")
        HW.instance.SetAmbientLight_OFF()
        #if HW.instance.GetSensorDoorClosed() == HW.instance.HIGH:
        #    logging.info("Closing Feeder (Opening door)")
        
        # for trainning, let the door OPEN
        if not config.TRAIN_MODE:
            HW.instance.OpenDoor()
        else:
            HW.instance.CloseDoor()
        HW.instance.SetStatusLED_OFF()
        
    
    def Init_Detector(self,args):
        """init the OPENCV interface"""
        logging.info("Init_Detector() (waitting %d seconds for Camera Init)" % config.CAMERA_WAIT_TIME)
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
        
        if HW.STATE == HW.AUTO and HW.AUTO_STATE == HW.AUTO_INIT and HW.instance.GetActivationState():
            #cat enters in the CatFeeder
            HW.instance.SetAmbientLight_ON()
            pet,photo = detector.instance.Identify()
            if not photo:
                photo = detector.instance.GetPhoto()
            HW.instance.SetAmbientLight_OFF()
    
            if pet:
                self.info.pet = pet
                self.info.photo = photo
                
                logging.info("Detected pet %s" % self.info.pet.name)

                self.info.start_meal =  db.FormatDateTime(datetime.datetime.now())
                ruleid = db.RuleService().CheckRules(self.info.pet.name)
                if ruleid:
                    HW.SetAutoState(HW.AUTO_OPEN)
                    if not config.TRAIN_MODE:
                        HW.instance.CloseDoor() # open feeder
                    self.info.ruleid = ruleid
                    self.info.allowed = 1
                else:
                    # pet is not allowed to eat notify and don' change state.
                    HW.SetAutoState(HW.AUTO_REJECT)
                    self.info.allowed = 0
                    logging.info("Pet %s is not allowed to eat" % self.info.pet.name)
            else:
                # manage unknown pet (problem detection)
                self.info.pet = db.PetService().Load(config.pets.UNKNOWN_PET)
                self.info.photo = photo
                self.info.start_meal =  db.FormatDateTime(datetime.datetime.now())
                self.info.end_meal =  db.FormatDateTime(datetime.datetime.now())
                self.info.allowed = 0
                logging.info("Unknown cat found. Taking photo and saving event. Done")
                HW.SetAutoState(HW.AUTO_REJECT)
                self.LogState()
                self.SaveEvent()      
                
        if HW.STATE == HW.AUTO and HW.AUTO_STATE == HW.AUTO_OPEN and not HW.instance.GetActivationState():
            if not config.TRAIN_MODE:
                HW.instance.OpenDoor() # close feeder
            HW.SetAutoState(HW.AUTO_WAIT)
            self.LogState()
            self.wait_time = time.time()
            logging.info("Pet stops eating. Done %s" % self.info.pet.name)
            self.info.end_meal =  db.FormatDateTime(datetime.datetime.now())
            self.SaveEvent()
 
        if HW.STATE == HW.AUTO and HW.AUTO_STATE == HW.AUTO_REJECT and not HW.instance.GetActivationState():
            HW.SetAutoState(HW.AUTO_WAIT)
            self.LogState()
            self.wait_time = time.time()
            logging.info("Rejected pet goes away Done %s" % self.info.pet.name)
            self.info.end_meal =  db.FormatDateTime(datetime.datetime.now())
            self.SaveEvent()
            
        if HW.STATE == HW.AUTO and HW.AUTO_STATE == HW.AUTO_WAIT:
            if time.time() - self.wait_time > config.WAIT_STATE_TIMEOUT:
                HW.SetAutoState(HW.AUTO_INIT)
                self.LogState()
                logging.info("Wait done. Going out")
                
            else:
                logging.info("Waitting state - stabilize sensors")
                time.sleep(config.WAIT_STATE_SLEEP)
            
   
    def Run_Manual(self):
        """the manual operation. Does nothing, because it's controlled by the web"""
        pass

    def LogState(self):
        global HW
        if HW.STATE == HW.AUTO:
            logging.info("CatFeeder %s/%s" % (HW.STATE, HW.AUTO_STATE))
        else:
            logging.info("CatFeeder State: %s", HW.STATE)    
        

if __name__ == "__main__":
    
    
    # raspberry run
    # python catfeeder_server.py catfeeder.db --serial_port='' --host=0.0.0.0

    server = CatFeederServer()
    args = server.Define_Arguments()
    server.Do_Checks(args)

    # configure dummy interface
    
    if args.dummy:
        logging.info("Using DUMMY Hardware interface (for devel)")
        hardware.Interface = hardware.ArduinoInterfaceMock
        
   
    server.Setup_Environment(args)
    server.Init_Detector(args) # wait for cam stabilization & pir (arduino).
    server.Init_Hardware(args)
    server.Start_WebServer(args)
    logging.info("Server started!")
    
    if config.TRAIN_MODE:
        logging.info("Trainning mode activated. Don't move the DOOR")
      
    with HW.LOCK:
        HW.STATE = HW.AUTO
    
    server.LogState()
    
    while True:    
       
        # this should be removed.
        
        if HW.STATE == HW.AUTO:
            server.Run_Automatic()
        else:
            server.LogState()
            server.Run_Manual()
            if HW.Timeout():
                logging.info("Timeout Expired, returning to AUTO")
                with HW.LOCK:
                    HW.STATE = HW.AUTO
                    HW.AUTO_STATE = HW.AUTO_INIT
                    server.LogState()
                server.Init_Hardware()
                    
        time.sleep(config.SERVER_SLEEP) # 1 second