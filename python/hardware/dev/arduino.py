import logging
import hardware as HW
from interface import HardwareInterface
import arduinowrapper 
import config

class ArduinoInterface(HardwareInterface):
    
    def __init__(self, serial_port= None):
        HardwareInterface.__init__(self)
        self.door_open = self.LOW
        self.door_closed = self.LOW
        self.detector = self.LOW
        self.led = self.LOW
        self.light = self.LOW
        self.door = self.LOW
        self.serial_port = serial_port
        
        self.arduino = arduinowrapper.ArduinoConfigFactory(self.serial_port, config.arduino.detector_timeout)
        logging.info("Created Arduino with Serial Port: '%s'" % (self.serial_port or ''))
        self.arduino.setup()
        
        
        
    def _show(self, msg, a, v):
        if a in self.__dict__.keys():
            logging.info("%s: %s->%s" % (msg, a, v))
    
    def __setattr__(self, a, v):
       
            if v in self.STATE_LABELS.keys():
                self._show("%s" % self.__class__, a, self.STATE_LABELS[v])
            else:
                self._show("%s" % self.__class__, a, v)
            self.__dict__[a] = v

    def __getattr__(self, a):
        
            #print "guarded"
            return self.__dict__[a]
        

    def GetLed(self):
        with HW.LOCK:               
            return self.led
    
    def GetLight(self):
        with HW.LOCK:                 
            return self.light
    
    def GetDoor(self):              
        with HW.LOCK:
            return self.door
        
    def GetSensorDoorOpen(self):    
        with HW.LOCK:
            self.door_open = self.arduino._get_s_door_open()
            return self.door_open
    
    def GetSensorDoorClosed(self):  
        with HW.LOCK:
            self.door_closed = self.arduino._get_s_door_closed()
            return self.door_closed
    
    def GetSensorDetector(self):    
        with HW.LOCK:
            self.detector = self.arduino._get_s_detector()
            return self.detector
    
    def SetStatusLED_ON(self):
        with HW.LOCK:      
            self.led = self.HIGH
            self.arduino._led_on()
        
    def SetStatusLED_OFF(self):     
        with HW.LOCK:
            self.led = self.LOW
            self.arduino._led_off()
        
    def SetAmbientLight_ON(self,value=None):   
        with HW.LOCK:
            self.light = self.HIGH
            self.arduino._light_on(value=value)
        
    def SetAmbientLight_OFF(self):  
        with HW.LOCK:
            self.light = self.LOW
            self.arduino._light_off()
        
        
    def OpenDoor(self):
        with HW.LOCK:
            self.door = self.HIGH
            self.arduino._open_door()
        
    def CloseDoor(self):
        with HW.LOCK:            
            self.door = self.LOW
            self.arduino._close_door()
    