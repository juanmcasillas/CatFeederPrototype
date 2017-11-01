
class HardwareInterface:
    HIGH = 1
    LOW = 0
    STATE_LABELS = { 0: 'LOW', 1: 'HIGH' }
    PIR_STATE = 0

     
    def __init__(self):
        pass
    
    def GetSensorDoorOpen(self):    pass
    def GetSensorDoorClosed(self):  pass
    def GetSensorDetector(self):    pass
    def GetLed(self):               pass
    def GetLight(self):             pass
    def GetDoor(self):              pass
    
    def SetStatusLED_ON(self):      pass
    def SetStatusLED_OFF(self):     pass
    def SetAmbientLight_ON(self,value=None):   pass
    def SetAmbientLight_OFF(self):  pass
    def OpenDoor(self):             pass
    def CloseDoor(self):            pass
    def GetActivationState(self):   pass
    
    # for devel only !!!
    def _SetSensorDetector(self,v): pass