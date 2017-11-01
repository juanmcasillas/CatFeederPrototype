import sys
import os.path
import os
import codecs
import re

class D:
    def __init__(self):
        pass

class Templater:
    def __init__(self, rootdir):
        self.basedir = "%s/tpl" % (rootdir)
        
        self.tplpart = 'template_%s_%s.html'
        self.tplpart_fragment = 'template_%s.html'
        self.tpl = 'template.html'


    def tpath(self, tag, extradir=None, Fragment=False):

        exdir = ''
        if extradir:
            exdir = extradir

        bd = self.basedir.split("/")
        if not Fragment:
            h = os.sep.join( bd + [ exdir,  self.tplpart % (tag,'head') ])
            b = os.sep.join( bd + [ exdir,  self.tplpart % (tag,'body') ])
            f = os.sep.join( bd + [ self.tpl ] )
        else:
            h = ""
            b = ""
            f = os.sep.join( bd + [ exdir,  self.tplpart_fragment % (tag) ])

            
        

        return(h,b,f)

    def readfile(self, f, encoding='utf-8'):

        f = codecs.open(f, 'r', encoding)
        data = f.read()
        f.close()
        return data


    def merge(self, ff, hf, bf):

        head = ""
        body = ""
        data = self.readfile(ff)
        
        if os.path.exists(hf):
            head = self.readfile(hf)
        
        if os.path.exists(bf):
            body = self.readfile(bf)


        data = data.replace('__HEAD__', head)
        data = data.replace('__BODY__', body)

        return data

    def xlate(self, data, xtable):

        for items in xtable:
            tag = items['tag']
            obj = items['obj']
            
            if type(obj) == dict:
                d_obj = obj
            else:
                d_obj = obj.__dict__

            for i in d_obj.keys():
                
                if type(d_obj[i]) == list:
                    # its an object ... do the work
                    p = 0
                    for k in d_obj[i]:
                        what = "__%s_" % tag.upper() + i.upper() + "[%d]" % p
                        #print "[L] %s" % what
                        
                        data = self.xlate(data, [ { 'tag': what, 'obj': k } ])
                          
                        p += 1    
                    
                    
                elif type(d_obj[i]) == object:
                    what = "__%s_" % tag.upper() + i.upper() + "__"
                    #print "[O] %s" % what
                    data = self.xlate(data, [ { 'tag': what, 'obj': d_obj[i] } ])
                    
                    
                else:
                    # plain one.
                    
                    what = "%s_" % tag.upper() + i.upper() + "__"
                    if not what.startswith("_"):
                        what = "__%s_" % tag.upper() + i.upper() + "__"
                    
                    #print "[G] %s (%s)"% (what,unicode(obj.__dict__[i]))
                    data = data.replace(what, unicode(d_obj[i]))

        return data

    def Generate(self, ftpl, xtable, opt=None, subdir=None):

        hf, bf, ff = self.tpath(ftpl,subdir)

        tpl = self.merge(ff, hf, bf)
        tpl = self.xlate(tpl, xtable)
        
    
        tpl = re.sub('(\r\n)+','\r\n',tpl, re.M|re.U)
        return tpl

    def GenerateFragment(self, ftpl, xtable, opt=None, subdir=None):

        hf, bf, ff = self.tpath(ftpl, Fragment=True, extradir=subdir)

        tpl = self.merge(ff, hf, bf)
        tpl = self.xlate(tpl, xtable)

        tpl = re.sub('(\r\n)+','\r\n',tpl, re.M|re.U)
        return tpl


if __name__ == "__main__":

    d = D()
    d.fname = "/Archive/Cartography/files/FENIX3/2016_gpx/2016-10-18-18-28-47 - [RUN,FENIX3,KANADIA] Navas - Pinar - M501 - Rampa - Antena NASA - Cortafuegos - Granja Cabras - Dehesa - Cementerio - Navas.gpx"
    d.id = 6
    d.kind = "RUN"
    d.device = "FENIX3"
    d.distance = 15000
    d.elevation = 496.07
    d.equipment = "KANADIA"
    d.description = "LOREM IPSUM DOLOR ... y mas cosas en minuscula por aqui <b>bonitas</b> bla bla bla aqui hay que meter muchas cosas para rellenar la caja y que se vean los datos bonitos esto deberia de ser editable, ademas"
    d.places = "<a href=''>Navas</a> | <a href=''>XXX</a> | <a href=''>YYY</a>"
    d.duration = "01:45:50"
    d.time_moving= "01:30:20"
    d.speed_avg = "18.3"

    g = D()
    g.title = "This is the title"
    g.body = "This is the body"

    t = Templater()
    #tpl = t.Generate("track", [ { 'tag': 'TRACK', 'obj': d } ])
    tpl = t.Generate("generic", [ { 'tag': 'GENERIC', 'obj': g } ])

    # full file.
    print tpl
