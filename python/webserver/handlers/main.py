import sys
import logging
import os
import os.path
import codecs
import webserver.www as www
import webserver.templater as templater
import config

class Main_Handler(www.Handler_Base):
    def __init__(self):
        www.Handler_Base.__init__(self)

    def Path(self):
        return ('/')

    def Dispatch(self, opts, request, args={}):

        # /demo?id=3

        #if len(args) == 0 or not 'id' in args.keys():
        #    request.send_response(500)
        #    request.end_headers()
        #    return

  
        #track = dbmanager.Track(None, None, None)

        #track.id = int(args['id'][0])
        #if not track.load(dbm.conn):
        #    request.send_response(500)
        #    request.end_headers()
        #    dbm.Close()
        #    return

        request.send_response(200)  # OK
        request.send_header('Content-type', self.ContentType())
        request.end_headers()

        # load page template.

        tplmgr = templater.Templater(opts.rootdir)

        demo_object = config.O()
        demo_object.name = "CatFeeder Event Log"
       
        #demo_object.body = ""
        demo_object.title = "CatFeeder Event Log"
        demo_object.page_title = config.www.generic_title + "Main"

        # modify track info to print it right.
        fdata = tplmgr.Generate("calendar", [ { 'tag': 'generic', 'obj': demo_object } ])
        request.wfile.write(fdata.encode('utf-8'))


## register items

def RegisterHandlers( handlers={} ):

    for k in [ Main_Handler 
              ]:
    
        h = k()
        handlers[h.Path()] = h
 
    return handlers
