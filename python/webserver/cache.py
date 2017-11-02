#!/usr/bin/env python

import os
import os.path
import hashlib



class CacheManager:
    def __init__(self, i=None,basedir='cache'):
        self.items = {}
        self.basedir = basedir
        self.hits = 0
        
        if i:
            self.items = i
        
        self.Add('default', 'default')
        
    def Add(self, d, k):
        self.items[d] = k 
        
    def _path(self, d, k):
        
        one = k[0:2]
        two = k[2:4]
        
        return os.sep.join([ self.basedir, d, one, two, k]) + ".%s" % d
        
    def Get(self, item, key):
        
        if not item in self.items.keys():
            self.items[item] = 'default'
            return ('',False)

        d = self.items[item]
        mkey = hashlib.md5(str(key)).hexdigest()
        p = self._path(d, mkey)
        
        if os.path.exists(p):
            self.hits += 1
            fd = open(p,"rb")
            data = fd.read()
            fd.close()
            return (p, data)
        
        # not found
        return (p, False)
    
    def Store(self, p, data):
        
        bd = os.path.dirname(p)
        if not os.path.exists(bd):
            os.makedirs(bd)
        fd = open(p, "wb+")
        
        if type(data) == unicode:
            fd.write(data.encode('utf-8'))
        else:
            fd.write(data)
        fd.close()
        
    
if __name__ == "__main__":
    
    cm = CacheManager( {'png': 'png', 'kml': 'kml'} );
    
    png = cm.Get('png',"1")
    kml = cm.Get('kml',"2")
    
    if not png[1]: cm.Store(png[0], "this is a PNG file")
    if not kml[1]: cm.Store(kml[0], "this is a KML file") 
        
    png = cm.Get('png',"1")
    kml = cm.Get('kml',"2")
    
    print png 
    print kml 
    print cm.hits
    