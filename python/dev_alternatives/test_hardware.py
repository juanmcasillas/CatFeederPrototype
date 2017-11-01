from hardware import Interface
import hardware as HW
import threading

if __name__ == "__main__":


    HW.LOCK = threading.Lock()
    
    interface = Interface()
    interface.SetAmbientLight_OFF()
    interface.SetAmbientLight_ON()
    interface.SetAmbientLight_OFF()