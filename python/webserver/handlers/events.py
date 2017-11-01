import sys
import logging
import os
import os.path
import codecs
import json

import webserver.www as www
import webserver.templater as templater

import config
import db
import datetime


class EventsJSON_Handler(www.Handler_Base):
    def __init__(self):
        www.Handler_Base.__init__(self)

    def Path(self):
        return ('/events/json')

    def ContentType(self):
        return "application/json"
    
    def Dispatch(self, opts, request, args={}):

        # /demo?id=3

        #http://localhost:8088/events/json?start=2017-08-27&end=2017-10-08&_=1505141709367 
        if len(args) == 3:
            start = args['start'][0]
            end   = args['end'][0]
            d     = args['_'][0]
        else:
            start = end = d = None
        
    
        request.send_response(200)  # OK
        request.send_header('Content-type', self.ContentType())
        request.end_headers()

        events = db.EventService().LoadInDataRange(start,end)
    
        fdata = json.dumps([ob.__dict__ for ob in events])
        request.wfile.write(fdata.encode('utf-8'))


## register items


class EventView_Handler(www.Handler_Base):
    def __init__(self):
        www.Handler_Base.__init__(self)

    def Path(self):
        return ('/events/view')

    
    def Dispatch(self, opts, request, args={}):

        # /demo?id=3
 
        if len(args) == 0 or not 'id' in args.keys():
            request.send_response(500)
            request.end_headers()
            return

        
        id = int(args['id'][0])
      
        
        event = db.EventService().Load(id)
        if not event:
            request.send_response(500)
            request.end_headers()
            dbm.Close()
            return
        
        event.pet = db.PetService().Load(event.petid)
         
        request.send_response(200)  # OK
        request.send_header('Content-type', self.ContentType())
        request.end_headers()
    
        tplmgr = templater.Templater(opts.rootdir)
        
        #demo_object.body = ""
        g = config.O()
        g.page_title = config.www.generic_title + "Event View"
  
        # pretty print
  
        event.photo = config.PathToURL(event.photo)
  
        if event.allowed:
            event.allowed = "Yes"
        else:
            event.allowed = "No"

        # modify track info to print it right.
        fdata = tplmgr.Generate("eventview", [ 
                                { 'tag': 'event', 'obj': event } , 
                                { 'tag': 'pet',   'obj': event.pet },
                                { 'tag': 'generic', 'obj': g } 
                            ], subdir='events')
    
      
        request.wfile.write(fdata.encode('utf-8'))
    



class EventDelete_Handler(www.Handler_Base):
    def __init__(self):
        www.Handler_Base.__init__(self)

    def Path(self):
        return ('/events/delete')

    
    def Dispatch(self, opts, request, args={}):

        # /demo?id=3
 
        if len(args) == 0 or not 'id' in args.keys():
            request.send_response(500)
            request.end_headers()
            return

        
        id = int(args['id'][0])
      
        ev = db.Event(id)
        
        event = db.EventService().Delete(ev)
        db.CloseAndCommit()
               
        request.send_response(302)  # OK
        request.send_header('Content-type', self.ContentType())
        request.send_header('Location', '/')
        request.end_headers()


def RegisterHandlers( handlers={} ):

    for k in [ EventsJSON_Handler, 
              EventView_Handler, 
              EventDelete_Handler
              ]:
    
        h = k()
        handlers[h.Path()] = h
 
    return handlers

