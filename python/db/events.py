import db
import config

from abstracttable import AbstractTable
import datetime


class Event(AbstractTable):
    def __init__(self, id=None):
        AbstractTable.__init__(self)
        self.id = id
        self.start = 0
        self.end = 0
        self.petid = 0
        self.allowed = 0
        self.rule = 0
        self.photo = None
        
        
    def sql_load_all(self):
        q = "select * from EVENTS"
        return q, Event
        
    def sql_load(self):
        q = "select * from EVENTS where id=%d" % int(self.id)
        return q, Event

    def sql_insert(self):
        q = "INSERT INTO EVENTS (start,end,petid, allowed, rule, photo) VALUES ('%s','%s',%d,%d,%d,'%s')" % \
            (self.start, self.end, self.petid, self.allowed, self.rule, self.photo)
        return q

    def sql_update(self):
        q = "update EVENTS set start='%s', end='%s', petid=%d, allowed=%d, rule=%d photo='%s' where id=%d" % \
            (self.start, self.end, self.petid, self.allowed, self.rule, self.photo, self.id)
        return q

    def sql_delete(self):
        q = "delete from EVENTS where id=%d" % self.id
        return q    
    
    def sql_delete_all(self):
        q = "delete from EVENTS"
        return q        
    
    def after_load(self):
        #'2017-09-10 20:21:22'
        self.start = db.ConvertDateTime(self.start)
        self.end = db.ConvertDateTime(self.end)

        duration = "N/A"
        if self.allowed:
            duration = self.end -self.start
            duration = db.Time2HMS_String(duration)
  
        self.duration = duration 



# implement the class logic here        

class EventService:
    
    def LoadAll(self):
        e = Event()
        r = e.load_all(db.conn)
        return r
    
    def Load(self, id):
        r = Event(id).load(db.conn)
        return r
    
    def Insert(self, obj):
        return obj.insert(db.conn)
    
    def Update(self, obj):
        return obj.update(db.conn)

    def Delete(self, obj):
        return obj.delete(db.conn)
    
    def DeleteAll(self, obj):
        return obj.delete_all(db.conn)
    
    def LoadInDataRange(self, start_date=None, end_date=None):
        e = Event()
        if start_date and end_date:
            q = "select * from EVENTS where start >= '%s' and end <= '%s'" % (start_date, end_date)
            
        else:
            q = e.sql_load_all() 
        
        conn = db.conn
        conn.row_factory = db.Row
        t = []
        
        # build a fullcalendarIO object
        #"0",
        #{
        #    "allDay": "",
        #    "title": "Test event",
        #    "id": "821",
        #    "end": "2011-06-06 14:00:00",
        #    "start": "2011-06-06 06:00:00"
        #},
            
        for row in conn.execute(q):
            o = db.O()
            o.allDay = ''
            
          
            
            
            pet = db.PetService().Load(row['petid'])
            
            
            o.imageurl = 'photos/icons/%s.png' % pet.photo
            o.url = '/events/view?id=%d' % row['id']
            
            o.id = row['id']
            o.start = row['start']
            o.end = row['end']
            # change colors in case of the status and the cat
            o.color = pet.color 
            if not row['allowed']:
                o.color = config.colors.event_not_allowed
            
            start = db.ConvertDateTime(o.start)
            end = db.ConvertDateTime(o.end)
            duration = "N/A"
            if row['allowed']:
                duration = end - start
                duration = db.Time2HMS_String(duration)
                o.title = pet.name + " (%s)" % duration
            else:
                o.title = pet.name
            
            t.append(o)
    
        return t        
        
        
 
    
        
    