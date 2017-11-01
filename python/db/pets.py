import db
from abstracttable import AbstractTable
import datetime


class Pet(AbstractTable):
    def __init__(self, id=None):
        AbstractTable.__init__(self)
        self.id = id
        self.name = ""
        self.chipid = ""
        self.photo = ""
        self.color = ""
        self.shape = ""
        self.birthdate = 0
        
    def sql_load_all(self):
        q = "select * from PETS where id>=0"
        return q, Pet
        
    def sql_load(self):
        q = "select * from PETS where id=%d" % int(self.id)
        return q, Pet

    def sql_insert(self):
        q = "INSERT INTO PETS (name,chipid,photo,color,shape, birthdate) VALUES ('%s','%s','%s','%s','%s','%s')" % \
            (self.name, self.chipid, self.photo,self.color, shelf.shape, self.birthdate)
        return q

    def sql_update(self):
        q = "update PETS set name='%s', chipid='%s', photo='%s', self.color='%s', self.shape='%s', birthdate='%s' where id=%d" % \
            (self.name, self.chipid, self.photo, self.color, self.shape, self.birthdate, self.id)
        return q

    def sql_delete(self):
        q = "delete from PETS where id=%d" % self.id
        return q        
    
    def sql_delete_all(self):
        q = "delete from PETS"
        return q    

    
        
        

# implement the class logic here  
    
    
class PetService():
    
    def __init__(self):
        pass
    
    
    def LoadAll(self):
        e = Pet()
        r = e.load_all(db.conn)
        return r
    
    def Load(self, id):
        r = Pet(id).load(db.conn)
        return r

    def LoadByName(self, name):
        p = Pet()
        q = "select * from PETS where UPPER(name)= UPPER('%s')" % name
        return p.load(db.conn,q, Pet)
        
        return r
    
    def LoadByShape(self, shape):
        p = Pet()
        q = "select * from PETS where UPPER(shape)= UPPER('%s')" % shape
        return p.load(db.conn,q, Pet)
        
        return r
    
    def Insert(self, obj):
        return obj.insert(db.conn)

    def Update(self, obj):
        return obj.update(db.conn)

    def Delete(self, obj):
        return obj.delete(db.conn)  
           
    def DeleteAll(self, obj):
        return obj.delete_all(db.conn)
    