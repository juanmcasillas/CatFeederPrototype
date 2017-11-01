import json
import logging
import hardware as HW

def HandleCommand(data, wsock=None):
        
    if data == None or data == "": return
     
    try:
        data = json.loads(data)
    except Exception, e:
        log.error("HandleData->JSON: %s" % e)
        return
    
    #print data
    
    if 'presence' in data.keys():
        presence = data['presence']
        if presence.upper() in [ 'TOGGLE' ]:
            v = HW.instance.GetSensorDetector()
            HW.instance._SetSensorDetector(not v)
        
#         if 'light' in data.keys():
#             light = data['light']
#             if light.upper() in ['HIGH', 'TRUE', '1', 'ON', 'OPEN']:
#                 instance.SetAmbientLight_ON()
#             else:
#                 instance.SetAmbientLight_OFF()
 
