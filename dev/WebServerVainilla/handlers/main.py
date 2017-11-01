import sys
import logging
import www
import dbmanager
import os
import os.path
import codecs
import templater

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

        #dbm = dbmanager.DBManager()
        #dbm.Connect(opts.dbfile)
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

        tplmgr = templater.Templater()

        demo_object = dbmanager.D()
        demo_object.name = "The NAME"
        demo_object.body = "The VALUE"
        demo_object.title = "The Title"
        demo_object.page_title = "Cat Feeder: Main"

        # modify track info to print it right.
        fdata = tplmgr.Generate("generic", [ { 'tag': 'generic', 'obj': demo_object } ])
        request.wfile.write(fdata.encode('utf-8'))
        #dbm.Close()

## register items

def RegisterHandlers( handlers={} ):
    
    main_h = Main_Handler()
    handlers[main_h.Path()] = main_h
    return handlers
