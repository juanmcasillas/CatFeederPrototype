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




## register items


class RuleList_Handler(www.Handler_Base):
    def __init__(self):
        www.Handler_Base.__init__(self)

    def Path(self):
        return ('/rules/list')
    
    def Dispatch(self, opts, request, args={}):

       
        
        rules = db.RuleService().LoadAll()
        
        request.send_response(200)  # OK
        request.send_header('Content-type', self.ContentType())
        request.end_headers()
    
        tplmgr = templater.Templater(opts.rootdir)
        
        html = ""
        for rule in rules:
            
            fragment = tplmgr.GenerateFragment("listentry", [ { 'tag': 'rule',   'obj': rule } ],  subdir='rules')
            html += fragment

        g = config.O()
        g.body = html
        html = tplmgr.GenerateFragment("listwrapper", [ { 'tag': 'wrapper',   'obj': g } ],  subdir='rules')
    
        g = config.O()
        g.page_title = config.www.generic_title + "Rule List"
        g.body = html
        g.title = "Rule List"

        fdata = tplmgr.Generate("generic", [ { 'tag': 'generic', 'obj': g } ] ) 
        request.wfile.write(fdata.encode('utf-8'))
    













def RegisterHandlers( handlers={} ):
    
    h = RuleList_Handler()
    handlers[h.Path()] = h
    

    
    return handlers
