#!/usr/bin/env python

from nanpy import ArduinoApi
from nanpy import SerialManager
import time
import logging

# mimic arduino time functions
delay  = lambda x: time.sleep(x/1000.0)
millis = lambda: time.time() * 1000.0

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
# S_OPEN (green with black)        A1 
# S_CLOSED (red with black)        A0
# S_DETECTOR (white with back)     D2
# 
# PIR http://www.instructables.com/id/PIR-Motion-Sensor-Tutorial/
#
class ArduinoConfigFactory:
    def __init__(self, serial_port=None, detector_timeout=30):
        self.PIN_DOOR_PWM_1_IN   = 6
        self.PIN_DOOR_DIRA_IN    = 7                   
        self.PIN_DOOR_DIRB_IN    = 4

        self.PIN_LED_PWM_2_IN    = 5

        self.PIN_S_OPEN      = 1 # A1
        self.PIN_S_CLOSED    = 0 # A0
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
        
        self.DETECTOR_TIMEOUT = detector_timeout # in seconds
        self.PIR_STATE = 0
        self.time_stamp = 0
        self.time_delta = 0
        self.door_open = 0
        self.door_closed = 0
        self.detector = 0

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
        self._led_off()
        self._light_off()
        self._get_s_door_open()
        self._get_s_door_closed()
        self._get_s_detector()
      
        # stabilize the PIR.
        delay(6000) # seconds
        logging.info("ARDUINO Hardware Layer: Ready to Work!")      
    
    def loop(self):
        self.door_open = self.arduino.analogRead(self.PIN_S_OPEN)
        self.door_closed = self.arduino.analogRead(self.PIN_S_CLOSED)
        
        if self.arduino.digitalRead(self.PIN_S_DETECTOR):
                  
            self.time_stamp = millis()
            
            logging.info("ARDUINO_HW: Detector Activated")
            self.arduino.digitalWrite(self.PIN_ARDUINO_LED, self.arduino.HIGH)
            delay(10)
            self.arduino.digitalWrite(self.PIN_ARDUINO_LED, self.arduino.LOW)
            delay(10)
            self.arduino.digitalWrite(self.PIN_ARDUINO_LED, self.arduino.HIGH)

            if self.PIR_STATE == 0:
                # turn on lights and issue camera detection
                # led test 
                for i in range(0,255):
                    self.arduino.analogWrite(self.PIN_LED_PWM_2_IN, i)
                    delay(1)
                
                #    
                # cat detection goes here
                # 
                delay(2000) # 2 secs is fine for testing
                
                self.arduino.analogWrite(self.PIN_LED_PWM_2_IN, 0) # shut down lights
      
                for i in range(0,10):
                    self.arduino.analogWrite(self.PIN_DOOR_PWM_1_IN, 200)
                    self.arduino.digitalWrite(self.PIN_DOOR_DIRA_IN,self.arduino.HIGH)
                    self.arduino.digitalWrite(self.PIN_DOOR_DIRB_IN,self.arduino.LOW)
                    #delay(2) # from 7 to 2
                 
                #brake motor 
                self.arduino.digitalWrite(self.PIN_DOOR_DIRA_IN,self.arduino.LOW)
                self.arduino.digitalWrite(self.PIN_DOOR_DIRB_IN,self.arduino.LOW)
              
            self.PIR_STATE = 1
  
        self.time_delta = millis() - self.time_stamp
      
        if (self.time_delta >= (self.DETECTOR_TIMEOUT *1000)) and (self.PIR_STATE == 1):
            
            logging.info("ARDUINO_HW: Timeout Passed. Closing")
            self.PIR_STATE = 0
            self.arduino.digitalWrite(self.PIN_ARDUINO_LED, self.arduino.LOW)
    
            # close door 
            for i in range(0,10):
                self.arduino.analogWrite(self.PIN_DOOR_PWM_1_IN, 200)
                self.arduino.digitalWrite(self.PIN_DOOR_DIRA_IN,self.arduino.LOW)
                self.arduino.digitalWrite(self.PIN_DOOR_DIRB_IN,self.arduino.HIGH)
                #delay(2) # from 7 to 2

            #brake motor
            self.arduino.digitalWrite(self.PIN_DOOR_DIRA_IN,self.arduino.LOW)
            self.arduino.digitalWrite(self.PIN_DOOR_DIRB_IN,self.arduino.LOW)

    ## helpers
          
    def _led_on(self): 
        self.arduino.digitalWrite(self.PIN_ARDUINO_LED, self.arduino.HIGH)
     
    def _led_off(self): 
        self.arduino.digitalWrite(self.PIN_ARDUINO_LED, self.arduino.LOW)   

    def _light_on(self,value=255): 
        #for i in range(0,255):
        #    self.arduino.analogWrite(self.PIN_LED_PWM_2_IN, i)
        self.arduino.analogWrite(self.PIN_LED_PWM_2_IN, value)
        
    def _light_off(self): 
    
        #for i in range(255,-1,-1):
        #    self.arduino.analogWrite(self.PIN_LED_PWM_2_IN, i)
        self.arduino.analogWrite(self.PIN_LED_PWM_2_IN, 0) 
    
        
    def _get_s_door_open(self):
        self.door_open = self.arduino.analogRead(self.PIN_S_OPEN)
        if self.door_open == 1023:
            self.door_open = 1
        else:
            self.door_open = 0
        
        return self.door_open
    
    def _get_s_door_closed(self):
        self.door_closed = self.arduino.analogRead(self.PIN_S_CLOSED) 
        if self.door_closed == 1023:
            self.door_closed = 1
        else:
            self.door_closed = 0
            
        return self.door_closed
        
    def _get_s_detector(self):
        self.detector = self.arduino.digitalRead(self.PIN_S_DETECTOR)
        return self.detector
        
    def _open_door(self):
        for i in range(0,10):
            self.arduino.analogWrite(self.PIN_DOOR_PWM_1_IN, 200)
            self.arduino.digitalWrite(self.PIN_DOOR_DIRA_IN,self.arduino.HIGH)
            self.arduino.digitalWrite(self.PIN_DOOR_DIRB_IN,self.arduino.LOW)
                    #delay(2) # from 7 to 2
        
        self.arduino.digitalWrite(self.PIN_DOOR_DIRA_IN,self.arduino.LOW)
        self.arduino.digitalWrite(self.PIN_DOOR_DIRB_IN,self.arduino.LOW)
    
    def _close_door(self):
        for i in range(0,10):
            self.arduino.analogWrite(self.PIN_DOOR_PWM_1_IN, 200)
            self.arduino.digitalWrite(self.PIN_DOOR_DIRA_IN,self.arduino.LOW)
            self.arduino.digitalWrite(self.PIN_DOOR_DIRB_IN,self.arduino.HIGH)
            #delay(2) # from 7 to 2
        
        self.arduino.digitalWrite(self.PIN_DOOR_DIRA_IN,self.arduino.LOW)
        self.arduino.digitalWrite(self.PIN_DOOR_DIRB_IN,self.arduino.LOW)
    
if __name__ == "__main__":
    
    arduino = ArduinoConfigFactory('/dev/cu.wchusbserial1a1130', 20)
    arduino.setup()
    
    while True:
        arduino.loop()
    
    
    