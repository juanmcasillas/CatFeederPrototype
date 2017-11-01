import logging
import hardware as HW
from interface import HardwareInterface
import config


class ArduinoInterfaceMock(HardwareInterface):
    def __init__(self, serial_port=None):
        
        HardwareInterface.__init__(self)

        self.time_stamp = 0
        self.time_delta = 0        
        self.serial_port = serial_port
        self.door_open = self.LOW
        self.door_closed = self.LOW
        self.detector = self.LOW
        self.led = self.LOW
        self.light = self.LOW
        self.door = self.LOW
        self.DETECTOR_TIMEOUT = config.arduino.detector_timeout # in seconds
        self.DELAY_PIR = config.arduino.delay_pir_init # seconds
        self.LIGHT_POWER =  config.arduino.light_max_power # 200
        self.MOTOR_POWER = config.arduino.motor_max_power  # 200
        
    def _show(self, msg, a, v):
        if a in self.__dict__.keys():
            if a not in [ 'time_delta']:
                logging.info("%s: %s->%s" % (msg, a, v))
    
    def __setattr__(self, a, v):
        with HW.LOCK:
            
            
            
            if v in self.STATE_LABELS.keys():
                self._show("%s" % self.__class__, a, self.STATE_LABELS[v])
            else:
                self._show("%s" % self.__class__, a, v)
            
            
            self.__dict__[a] = v

    def __getattr__(self, a):
        with HW.LOCK:
            return self.__dict__[a]
        
    
    def GetSensorDoorOpen(self):    return self.door_open
    def GetSensorDoorClosed(self):  return self.door_closed
    def GetSensorDetector(self):    return self.detector
    def GetLed(self):               return self.led
    def GetLight(self):             return self.light
    def GetDoor(self):              return self.door
    
    def SetStatusLED_ON(self):      self.led      = self.HIGH
    def SetStatusLED_OFF(self):     self.led      = self.LOW
    def SetAmbientLight_ON(self,value=None):   self.light    = self.HIGH
    def SetAmbientLight_OFF(self):  self.light    = self.LOW
    
    def OpenDoor(self):
        """open door -> close feeder"""             
        self.door = self.HIGH
        self.door_open = self.HIGH
        self.door_closed = self.LOW
        
    def CloseDoor(self):            
        """close door -> open feeder"""
        
        self.door = self.LOW
        self.door_closed = self.HIGH
        self.door_open = self.LOW
    
    def GetActivationState(self):
        """this method should run inside a LOOP to work propertly"""
        
        detector_value = self.GetSensorDetector()
        if detector_value:
            self.time_stamp = HW.millis()
            logging.info("%s: Detector Activated" % self.__class__)

            if self.PIR_STATE == 0:
                # things to do at the first time of the cycle detector.
                pass
            self.PIR_STATE = 1
  
        self.time_delta = HW.millis() - self.time_stamp
      
        if (self.time_delta >= (self.DETECTOR_TIMEOUT *1000)) and (self.PIR_STATE == 1):
            logging.info("%s: Timeout Passed. Closing" % self.__class__)
            self.PIR_STATE = 0
            
        return self.PIR_STATE
    # testing
    def _SetSensorDetector(self,v):
        self.detector = v