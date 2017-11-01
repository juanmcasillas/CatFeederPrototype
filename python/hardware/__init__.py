from arduinomock import ArduinoInterfaceMock
from arduino import ArduinoInterface
# TBD from arduino import ArduinoInterface
import time

import config
import time
import logging





#Interface = ArduinoInterfaceMock    # demo interface
Interface = ArduinoInterface       # physical interface
instance = None

#HW_LOCK = threading.Lock()
LOCK = None

# state machine variable
STATE = 'AUTO' # can be "MANUAL" also. see state machine diagram XD
AUTO = 'AUTO'
MANUAL = 'MANUAL'

AUTO_STATE = 'INIT'     # automatic state transition

AUTO_INIT = 'INIT'
AUTO_OPEN = 'OPEN'
AUTO_REJECT = 'REJECT'
AUTO_WAIT = 'WAIT'


STATE_TIMEOUT = config.STATE_TIMEOUT # seconds
timeout_delta = 0

# mimic arduino time functions
delay  = lambda x: time.sleep(x/1000.0)
millis = lambda: time.time() * 1000.0


def ValidState(s):
    if s.upper() in [ AUTO, MANUAL ]:
        return True
    return False

def SetState(s):
    global STATE
    global timeout_delta
    with LOCK:
        if s.upper() == MANUAL and timeout_delta == 0:
            timeout_delta = time.time()
            
        STATE = s.upper()
        
def SetAutoState(s):
    global AUTO_STATE
    with LOCK:
        AUTO_STATE = s.upper()        

def Timeout():
    global STATE
    global timeout_delta
    with LOCK:
        time_delta = time.time() - timeout_delta
        if STATE == MANUAL and time_delta > STATE_TIMEOUT:
            # change state.
            timeout_delta = 0
            return True
    return False
            

#
# JSON status builder
#

def GetFullStatus():
    """build the JSON package with all the data. Done here because it's hardware related"""
    o = config.O()
    o.led = instance.GetLed()
    o.sensor_open = instance.GetSensorDoorOpen()
    o.sensor_closed = instance.GetSensorDoorClosed()
    o.detector = instance.GetSensorDetector()
    o.light = instance.GetLight()
    o.door = instance.GetDoor()
    o.activation = instance.GetActivationState()
    o.state = STATE
    return o


