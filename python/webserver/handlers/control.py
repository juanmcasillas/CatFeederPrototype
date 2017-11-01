import sys
import logging
import os
import os.path
import codecs
import json
import datetime
import config

import webserver.www as www
import webserver.templater as templater
import db

import hardware as HW
import detector



## register items


class ControlView_Handler(www.Handler_Base):
    def __init__(self):
        www.Handler_Base.__init__(self)

    def Path(self):
        return ('/control/view')
    
    def Dispatch(self, opts, request, args={}):

       
        request.send_response(200)  # OK
        request.send_header('Content-type', self.ContentType())
        request.end_headers()
    
        tplmgr = templater.Templater(opts.rootdir)
        
        g = config.O()
        g.page_title = config.www.generic_title + "HW Control"
        g.body = ""
        g.title = "HW Control"
        g.uptime = config.StrUptime()
     
        
        g.last_image = config.PathToURL(config.last_image)
        
        fdata = tplmgr.Generate("control", [ { 'tag': 'generic', 'obj': g } ] ) 
        request.wfile.write(fdata.encode('utf-8'))


class ControlChangeState_Handler(www.Handler_Base):
    def __init__(self):
        www.Handler_Base.__init__(self)

    def Path(self):
        return ('/control/change/state')

    def ContentType(self):
        return "application/json"
    
    def Dispatch(self, opts, request, args={}):

        if len(args) == 1:
            state = args['state'][0]
        else:
            request.send_response(500)
            request.end_headers()
            return
       
        if not HW.ValidState(state):
            request.send_response(500)
            request.end_headers()
            return
            
       
        HW.SetState(state)
       
        request.send_response(200)  # OK
        request.send_header('Content-type', self.ContentType())
        request.end_headers()
        
        g = config.O()
        g.state  = state
        #fdata = json.dumps([ob.__dict__ for ob in events])                
        fdata = json.dumps(g.__dict__)
        request.wfile.write(fdata.encode('utf-8'))


class ControlGetStatus_Handler(www.Handler_Base):
    def __init__(self):
        www.Handler_Base.__init__(self)

    def Path(self):
        return ('/control/status/json')

    def ContentType(self):
        return "application/json"
    
    def Dispatch(self, opts, request, args={}):

        # /demo?id=3

        request.send_response(200)  # OK
        request.send_header('Content-type', self.ContentType())
        request.end_headers()
        
        data = HW.GetFullStatus()
        #fdata = json.dumps([ob.__dict__ for ob in data])
        fdata = json.dumps(data.__dict__)
        request.wfile.write(fdata.encode('utf-8'))



# template class for our dispatchers
class ControlGeneric_Handler(www.Handler_Base):
    def __init__(self, attr, trigger=None):
        www.Handler_Base.__init__(self)
        self.attr_name = attr
        self.attr_value = None
        self.allowed_actions = ['HIGH', 'TRUE', '1', 'ON', 'OPEN' ]
        
        if trigger:
            self.allowed_actions.append(trigger.upper())

    def Path(self):
        return ('/control/change/' + self.attr_name)

    def ContentType(self):
        return "application/json"
    
    def ON(self): pass
    def OFF(self): pass
    
    
    def Dispatch(self, opts, request, args={}):

        if len(args) == 1:
            self.attr_value = args[self.attr_name][0]
        else:
            request.send_response(500)
            request.end_headers()
            return
       
        if self.attr_value.upper() in self.allowed_actions:
            self.ON()
        else:
            self.OFF()
            
       
        request.send_response(200)  # OK
        request.send_header('Content-type', self.ContentType())
        request.end_headers()
        
        g = config.O()
        setattr(g, self.attr_name, self.attr_value)
        #fdata = json.dumps([ob.__dict__ for ob in events])                
        fdata = json.dumps(g.__dict__)
        request.wfile.write(fdata.encode('utf-8'))


class ControlChangeLight_Handler(ControlGeneric_Handler):
    def __init__(self):
        ControlGeneric_Handler.__init__(self,'light')

    def ON(self):
        HW.instance.SetAmbientLight_ON()
        
    def OFF(self):
        HW.instance.SetAmbientLight_OFF()
        
class ControlChangeDoor_Handler(ControlGeneric_Handler):
    def __init__(self):
        ControlGeneric_Handler.__init__(self,'door')

    def ON(self):
        HW.instance.OpenDoor()
        
    def OFF(self):
        HW.instance.CloseDoor()

class ControlChangeLED_Handler(ControlGeneric_Handler):
    def __init__(self):
        ControlGeneric_Handler.__init__(self,'led')

    def ON(self):
        HW.instance.SetStatusLED_ON()
        
    def OFF(self):
        HW.instance.SetStatusLED_OFF()

class ControlChangePhoto_Handler(ControlGeneric_Handler):
    """snap a photo"""
    
    def __init__(self):
        ControlGeneric_Handler.__init__(self,'photo','take photo')

    def ON(self):
        photo = detector.instance.GetPhoto()
        
    def OFF(self):
        pass
    
class ControlShutdown_Handler(ControlGeneric_Handler):
    """snap a photo"""
    
    def __init__(self):
        ControlGeneric_Handler.__init__(self,'shutdown','shutdown')

    def ON(self):
        cmd = "sudo shutdown -h now"
        os.system(cmd)
        # goes away!
        
        
    def OFF(self):
        pass



class ControlClearLog_Handler(www.Handler_Base):
    def __init__(self):
        www.Handler_Base.__init__(self)

    def Path(self):
        return ('/control/clearlog')

    def ContentType(self):
        return "text/html"
    
    def Dispatch(self, opts, request, args={}):

        # /demo?id=3

        cmd = "cat /dev/null > %s" % config.LOG_FILE
        os.system(cmd)
        
        request.send_response(302)  # OK
        request.send_header('Content-type', self.ContentType())
        request.send_header('Location', '/control/log')
        request.end_headers()
      





class ControlReadLog_Handler(www.Handler_Base):
    def __init__(self):
        www.Handler_Base.__init__(self)

    def Path(self):
        return ('/control/log')

   
    
    def Dispatch(self, opts, request, args={}):
        
        #https://stackoverflow.com/questions/20735991/python-logging-for-tcp-server
  

        request.send_response(200)  # OK
        request.send_header('Content-type', self.ContentType())
        request.end_headers()
        
        f = open(config.LOG_FILE, "r")
        a = f.read()
        f.close()
        
        obj = config.O()
        obj.log = a
        
        tplmgr = templater.Templater(opts.rootdir) 

        fragment = tplmgr.GenerateFragment("log", [ { 'tag': 'control',   'obj': obj} ],  subdir='control')
    
        g = config.O()
        g.page_title = config.www.generic_title + "Log"
        g.body = fragment
        g.title = "Log"

        fdata = tplmgr.Generate("generic", [ { 'tag': 'generic', 'obj': g } ] ) 
        request.wfile.write(fdata.encode('utf-8'))

        
        # don't close it

def RegisterHandlers( handlers={} ):
    
    for k in [ ControlView_Handler, 
              ControlChangeState_Handler, 
              ControlGetStatus_Handler, 
              ControlChangeLight_Handler,
              ControlChangeDoor_Handler,
              ControlChangeLED_Handler,
              ControlChangePhoto_Handler,
              ControlShutdown_Handler,
              ControlClearLog_Handler,
              ControlReadLog_Handler
              ]:
    
        h = k()
        handlers[h.Path()] = h
 
    return handlers
