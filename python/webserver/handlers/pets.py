import sys
import logging
import os
import os.path
import codecs
import json
import datetime
import config
import dateutil.relativedelta

import webserver.www as www
import webserver.templater as templater
import db




## register items


class PetList_Handler(www.Handler_Base):
    def __init__(self):
        www.Handler_Base.__init__(self)

    def Path(self):
        return ('/pets/list')
    
    def Dispatch(self, opts, request, args={}):

       
        
        pets = db.PetService().LoadAll()
        
        request.send_response(200)  # OK
        request.send_header('Content-type', self.ContentType())
        request.end_headers()
    
        tplmgr = templater.Templater(opts.rootdir)
        
        #demo_object.body = ""

        html = ""
        for pet in pets:
            
            
            
            pet.years = dateutil.relativedelta.relativedelta(datetime.datetime.now(),db.ConvertDate(pet.birthdate)).years
            fragment = tplmgr.GenerateFragment("listentry", [ { 'tag': 'pet',   'obj': pet } ],  subdir='pets')
            html += fragment
    
        g = config.O()
        g.page_title = config.www.generic_title + "Pets List"
        g.body = html
        g.title = "Pet List"

        fdata = tplmgr.Generate("generic", [ { 'tag': 'generic', 'obj': g } ] ) 
        request.wfile.write(fdata.encode('utf-8'))
    













def RegisterHandlers( handlers={} ):
    
    h = PetList_Handler()
    handlers[h.Path()] = h
    

    
    return handlers
