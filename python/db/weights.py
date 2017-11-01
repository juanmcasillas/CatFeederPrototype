import db
from abstracttable import AbstractTable
import datetime


class Weight(AbstractTable):
    def __init__(self, id=None):
        AbstractTable.__init__(self)
        self.id = id
        self.petid = ""
        self.stamp = 0
        self.weight = 0.0
        self.description = ""
        
        
    def sql_load_all(self):
        q = "select * from WEIGHTS"
        return q, Weight
        
    def sql_load(self):
        q = "select * from WEIGHTS where id=%d" % int(self.id)
        return q, Weight

    def sql_insert(self):
        q = "INSERT INTO WEIGHTS (petid,stamp,weight,description) VALUES (%d,'%s',%d,'%s')" % \
            (self.petid, self.stamp, self.weight, self.description)
        return q

    def sql_update(self):
        q = "update WEIGHTS set petid=%d, stamp='%s', weight=%f, description='%s' where id=%d" % \
            (self.petid, self.stamp, self.weight, self.description, self.id)
        return q

    def sql_delete(self):
        q = "delete from WEIGHTS where id=%d" % self.id
        return q      

    def sql_delete_all(self):
        q = "delete from WEIGHTS"
        return q     
    
    def after_load(self):
        #'2017-09-10 20:21:22'
        self.stamp = db.ConvertDateTime(self.stamp)





# implement the class logic here  

        
class WeightService():
    def __init__(self):
        pass
    
    
    def LoadAll(self):
        e = Weight()
        r = e.load_all(db.conn)
        return r
    
    def Load(self, id):
        r = Weight(id).load(db.conn)
        return r
    
    def Insert(self, obj):
        return obj.insert(db.conn)
    
    def Update(self, obj):
        return obj.update(db.conn)

    def Delete(self, obj):
        return obj.delete(db.conn)   
    
    def DeleteAll(self, obj):
        return obj.delete_all(db.conn)