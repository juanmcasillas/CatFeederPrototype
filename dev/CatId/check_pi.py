#!/usr/bin/env python 
#
# check if runnin on raspy hardware (for the camera)
#
import os, os.path
import re

def IsRaspberry():
    cpuinfo = '/proc/cpuinfo'
    if not os.path.exists(cpuinfo):
        return False
    
    fd = file(cpuinfo)
    data = fd.readlines()
    fd.close()
    
    for l in data:
        x = re.sub(r"\s+", '', l)
        x = x.split(":")
        if x[0].lower() == 'hardware' and x[1].upper() in [ 'BCM2708', 'BCM2835' ]:
            return True
        
    return False

        
        
        
if __name__ == "__main__":
    
    print IsRaspberry()
    
