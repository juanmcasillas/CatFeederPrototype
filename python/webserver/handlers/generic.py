
import sys
import logging
import os
import os.path
import codecs

import webserver.www as www
import webserver.templater as templater
import config 
import datetime

class Generic_Handler(www.Handler_Base):
    def __init__(self):
        www.Handler_Base.__init__(self)

    def Path(self):
        return ('/genericpage')

    def Dispatch(self, opts, request, args={}):

        request.send_response(200)  # OK
        request.send_header('Content-type', self.ContentType())
        request.end_headers()

        # load page template.

        tplmgr = templater.Templater(opts.rootdir)

        demo_object = config.O()
        demo_object.name = args['response'][0]
        demo_object.body = args['desc'][0]
        demo_object.title = args['title'][0]
        demo_object.page_title = config.www.generic_title + "Ooops"
        
        # modify track info to print it right.
        fdata = tplmgr.Generate("generic", [ { 'tag': 'generic', 'obj': demo_object } ])
        request.wfile.write(fdata.encode('utf-8'))

class GenericListDir_Handler(www.Handler_Base):
    def __init__(self):
        www.Handler_Base.__init__(self)

    def Path(self):
        return ('/listdir')

    def Dispatch(self, opts, request, args={}):

        request.send_response(200)  # OK
        request.send_header('Content-type', self.ContentType())
        request.end_headers()

        # load page template.

        tplmgr = templater.Templater(opts.rootdir)

        demo_object = config.O()
        demo_object.name = "CatFeeder List Directory"
       
        #demo_object.body = ""
        demo_object.title = "Photo Archive"
        demo_object.page_title = "Photo Archive"
        
          
        # Make the directory path navigable.
        dirstr = ''
        href = None
        for seg in opts.rpath.split('/'):
            if href is None:
                href = seg
            else:
                href = href + '/' + seg
                dirstr += '/'
            dirstr += '<a href="%s">%s</a>' % (href, seg)
     
        demo_object.crumb = dirstr
        
        body = ""
        fnames = ['..']
        fnames.extend(sorted(os.listdir(opts.dirpath), key=str.lower))
        
        for fname in fnames:
                                     
            path = opts.rpath + '/' + fname
            fpath = os.path.join(opts.dirpath, fname)
            stat = os.stat(fpath)
            ctime = stat.st_ctime
            ctime = datetime.datetime.fromtimestamp(ctime).strftime('%m/%d/%Y %H:%M:%S')

            dirent = config.O()
            dirent.url = "%s%s" % (opts.serverpath, path)
            dirent.name = "%s" % fname
            dirent.size = "%3.2f" % ((os.path.getsize(fpath) / 1024.0))
            dirent.time = "%s" % (ctime)
            
       

            if os.path.isdir(fpath):
                print fpath
                dirent.name = "%s/" % fname #add the / to indicate directory
           
                
            fragment = tplmgr.GenerateFragment("direntry", [ { 'tag': 'dir',   'obj': dirent } ],  subdir='generic')
            body += fragment
        
        g = config.O()
        g.body = body
        g.breadcrumb =  demo_object.crumb
        html = tplmgr.GenerateFragment("dirwrapper", [ { 'tag': 'wrapper',   'obj': g } ],  subdir='generic')
        
        demo_object.body = html 
             
     
        # modify track info to print it right.
        fdata = tplmgr.Generate("listdir", [ { 'tag': 'generic', 'obj': demo_object } ])
        request.wfile.write(fdata.encode('utf-8'))
        #
        #r 

#                       
        #


## register items

def RegisterHandlers( handlers={} ):

    for k in [ Generic_Handler, 
              GenericListDir_Handler
              ]:
    
        h = k()
        handlers[h.Path()] = h
 
    return handlers
