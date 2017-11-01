import logging
from nanpy import ArduinoApi
from nanpy import SerialManager
import time

import hardware as HW
from interface import HardwareInterface
import config




# PIN MAPPING
# 
# ARDUINO_GND (green)          PIN2 right GND (arduino USB connecto down)
# ARDUINO_VCC (red)            PIN4 right 5V
# 
# DOOR_PWM_1_IN (white / brown)    D6
# DOOR_DIRA_IN (brown)             D7             
# DOOR_DIRB_IN (green)             D4
# DOOR_RED_OUT                     motor_red
# DOOR_BLACK_OUT                   motor_black
# 
# LED_DIRA_IN                      jumped to VCC_ARDUINO (red)
# LED_DIRB_IN                      jumped to GND (black)
# LED_RED_OUT (white)
# LED_BLACK_OUT (red)
# LED_PWM_2_IN (white/green)       D5
# 
# S_OPEN (green with black)        A1 D9
# S_CLOSED (red with black)        A0 D10
# S_DETECTOR (white with back)     D2 
# 
# PIR http://www.instructables.com/id/PIR-Motion-Sensor-Tutorial/
#


class ArduinoInterface(HardwareInterface):
    
    def __init__(self, serial_port=None):

        HardwareInterface.__init__(self)
        
        # arduino pinout configuration
        
        self.PIN_DOOR_PWM_1_IN   = 6
        self.PIN_DOOR_DIRA_IN    = 7                   
        self.PIN_DOOR_DIRB_IN    = 4

        self.PIN_LED_PWM_2_IN    = 5

        self.PIN_S_OPEN      = 1 # 9 A1 # should be Digital PinS, but.
        self.PIN_S_CLOSED    = 0 # 10  A0 # should be Digital PinS, but.
        self.PIN_S_DETECTOR  = 2

        self. PIN_ARDUINO_LED  = 13

        self.serial_port = serial_port
        self.connection = None
        
        if self.serial_port:
            # mac, linux, windows
            self.connection = SerialManager(device=self.serial_port)
        else:
            # raspberry
            self.connection = SerialManager()
            
        self.arduino = ArduinoApi(connection=self.connection)

        # local variables and constants
        
        self.DETECTOR_TIMEOUT = config.arduino.detector_timeout # in seconds
        self.DELAY_PIR_INIT = config.arduino.delay_pir_init # seconds
        self.LIGHT_POWER =  config.arduino.light_max_power # 200
        self.MOTOR_POWER = config.arduino.motor_max_power  # 200
        self.MOTOR_DELAY = config.arduino.motor_delay # varies
        
        self.time_stamp = 0
        self.time_delta = 0
        
        self.door_open = self.LOW
        self.door_closed = self.LOW
        self.detector = self.LOW
        self.led = self.LOW
        self.light = self.LOW
        self.door = self.LOW
        
        logging.info("Created Arduino with Serial Port: '%s'" % (self.serial_port or ''))
        self.setup()


    def setup(self):
        self.arduino.pinMode(self.PIN_DOOR_PWM_1_IN, self.arduino.OUTPUT)
        self.arduino.pinMode(self.PIN_DOOR_DIRA_IN, self.arduino.OUTPUT)         
        self.arduino.pinMode(self.PIN_DOOR_DIRB_IN, self.arduino.OUTPUT)
        self.arduino.pinMode(self.PIN_LED_PWM_2_IN, self.arduino.OUTPUT)
    
        self.arduino.pinMode(self.PIN_S_CLOSED, self.arduino.INPUT)
        self.arduino.pinMode(self.PIN_S_OPEN,self.arduino.INPUT)
        self.arduino.pinMode(self.PIN_S_DETECTOR,self.arduino.INPUT)
        self.arduino.pinMode(self.PIN_ARDUINO_LED, self.arduino.OUTPUT) 
      
        # start clear
        self.SetAmbientLight_OFF()
        self.SetStatusLED_OFF()    
        
        #test motory delay in raspberry
        #self.OpenDoor()
        #HW.delay(2000)
        #self.CloseDoor()
        #import sys; sys.exit(0)
        
        self.GetSensorDoorOpen()
        self.GetSensorDoorClosed()
        self.GetSensorDetector()
      
        # stabilize the PIR.
        #logging.info("ARDUINO Hardware Layer. Waitting for PIR calibration %d seconds" % self.DELAY_PIR_INIT)  
        ## wait elsewhere up HW.delay(self.DELAY_PIR_INIT*1000) # seconds
        logging.info("ARDUINO Hardware Layer: Ready to Work!")              


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

    # debugging methods
        
    def _show(self, msg, a, v):
        if a in self.__dict__.keys():
            if a not in [ 'time_delta']:
                pass
                # remove to avoid too much messages
                #logging.info("%s: %s->%s" % (msg, a, v))
    
    def __setattr__(self, a, v):
       
        if v in self.STATE_LABELS.keys():
            self._show("Set: %s" % self.__class__, a, self.STATE_LABELS[v])
        else:
            self._show("%s" % self.__class__, a, v)
        self.__dict__[a] = v

    def __getattr__(self, a):
        self._show("Get: %s->%s" % self.__class__, a,  self.__dict__[a])
        return self.__dict__[a]

    
    
    # helper methods to get the values


    def GetLed(self):
        with HW.LOCK:               
            return self.led
    
    def GetLight(self):
        with HW.LOCK:                 
            return self.light
    
    def GetDoor(self):              
        with HW.LOCK:
            return self.door

    
    # physical interface methods

        
    def GetSensorDoorOpen(self):
        v = self.LOW
        with HW.LOCK:
            v = self.arduino.analogRead(self.PIN_S_OPEN)
            if v == 1023:
                self.door_open = 1
            else:
                self.door_open = 0
            #self.door_open = self.arduino.digitalRead(self.PIN_S_OPEN)
            v = self.door_open
        return v
    
    def GetSensorDoorClosed(self):  
        v = self.LOW
        with HW.LOCK:
            v = self.arduino.analogRead(self.PIN_S_CLOSED) 
            if v == 1023:
                self.door_closed = 1
            else:
                self.door_closed = 0
            #self.door_closed = self.arduino.digitalRead(self.PIN_S_CLOSED)
            v = self.door_closed
        return v
    
    def GetSensorDetector(self):    
        v = self.LOW
        with HW.LOCK:
            self.detector = self.arduino.digitalRead(self.PIN_S_DETECTOR)
            v = self.detector
        return v
    
    def SetStatusLED_ON(self):
        with HW.LOCK:      
            self.led = self.HIGH
            self.arduino.digitalWrite(self.PIN_ARDUINO_LED, self.arduino.HIGH)
        
    def SetStatusLED_OFF(self):     
        with HW.LOCK:
            self.led = self.LOW
            self.arduino.digitalWrite(self.PIN_ARDUINO_LED, self.arduino.LOW) 
        
    def SetAmbientLight_ON(self,value=None):   
        with HW.LOCK:
            
            Light_Power = value or self.LIGHT_POWER
            self.light = self.HIGH
            #for i in range(0,255):
            #    self.arduino.analogWrite(self.PIN_LED_PWM_2_IN, i)
            self.arduino.analogWrite(self.PIN_LED_PWM_2_IN, Light_Power)
        
    def SetAmbientLight_OFF(self):  
        with HW.LOCK:
            self.light = self.LOW
            #for i in range(255,-1,-1):
            #    self.arduino.analogWrite(self.PIN_LED_PWM_2_IN, i)
            self.arduino.analogWrite(self.PIN_LED_PWM_2_IN, 0) 
        
        
    def OpenDoor(self):
        """open door -> close feeder"""
        with HW.LOCK:
            self.door = self.HIGH
            
            self.arduino.analogWrite(self.PIN_DOOR_PWM_1_IN, self.MOTOR_POWER)
            self.arduino.digitalWrite(self.PIN_DOOR_DIRA_IN,self.arduino.HIGH)
            self.arduino.digitalWrite(self.PIN_DOOR_DIRB_IN,self.arduino.LOW)
            
            HW.delay(self.MOTOR_DELAY) # wait to open
            
            #for i in range(0,self.MOTOR_DELAY):
            #    self.arduino.analogWrite(self.PIN_DOOR_PWM_1_IN, self.MOTOR_POWER)
            #    self.arduino.digitalWrite(self.PIN_DOOR_DIRA_IN,self.arduino.HIGH)
            #    self.arduino.digitalWrite(self.PIN_DOOR_DIRB_IN,self.arduino.LOW)
                
            self.arduino.digitalWrite(self.PIN_DOOR_DIRA_IN,self.arduino.LOW)
            self.arduino.digitalWrite(self.PIN_DOOR_DIRB_IN,self.arduino.LOW)
        
    def CloseDoor(self):
        """close door -> open feeder"""
        with HW.LOCK:            
            self.door = self.LOW
            
            self.arduino.analogWrite(self.PIN_DOOR_PWM_1_IN, self.MOTOR_POWER)
            self.arduino.digitalWrite(self.PIN_DOOR_DIRA_IN,self.arduino.LOW)
            self.arduino.digitalWrite(self.PIN_DOOR_DIRB_IN,self.arduino.HIGH)
            
            HW.delay(self.MOTOR_DELAY)
            
            #for i in range(0,self.MOTOR_DELAY): # 10 mac, 50 raspy
            #    self.arduino.analogWrite(self.PIN_DOOR_PWM_1_IN, self.MOTOR_POWER)
            #    self.arduino.digitalWrite(self.PIN_DOOR_DIRA_IN,self.arduino.LOW)
            #    self.arduino.digitalWrite(self.PIN_DOOR_DIRB_IN,self.arduino.HIGH)
             
            self.arduino.digitalWrite(self.PIN_DOOR_DIRA_IN,self.arduino.LOW)
            self.arduino.digitalWrite(self.PIN_DOOR_DIRB_IN,self.arduino.LOW)
    
    
    def _SetSensorDetector(self,v):
        with HW.LOCK:            
            self.detector = v
    