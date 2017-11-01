import db
from abstracttable import AbstractTable
import datetime
from ruletools import RuleManager


class Rule(AbstractTable):
    def __init__(self, id=None):
        AbstractTable.__init__(self)
        self.id = id
        self.name = ""
        self.rule = ""
        self.description = ""
        self.enabled = 0
        self.position = 0
        
        
    def sql_load_all(self):
        q = "select * from RULES order by position"
        return q, Rule
        
    def sql_load(self):
        q = "select * from RULES where id=%d" % int(self.id)
        return q, Rule

    def sql_insert(self):
        q = "INSERT INTO RULES (name,rule,description,enabled,position) VALUES ('%s','%s','%s',%d,%d)" % \
            (self.name, self.rule, self.description, self.enabled, self.position)
        return q

    def sql_update(self):
        q = "update RULES set name='%s', rule='%s', description='%s', enabled=%d, position=%d where id=%d" % \
            (self.name, self.rule, self.description, self.enabled, self.position, self.id)
        return q

    def sql_delete(self):
        q = "delete from RULES where id=%d" % self.id
        return q    
        
    def sql_delete_all(self):
        q = "delete from RULES"
        return q    



# implement the class logic here  
    
    
class RuleService():
    def __init__(self):
        pass
    
    def LoadAll(self):
        e = Rule()
        r = e.load_all(db.conn)
        return r
    
    def Load(self, id):
        r = Rule(id).load(db.conn)
        return r
    
    def Insert(self, obj):
        return obj.insert(db.conn)
    
    def Update(self, obj):
        return obj.update(db.conn)

    def Delete(self, obj):
        return obj.delete(db.conn)  
        
    def DeleteAll(self, obj):
        return obj.delete_all(db.conn)
    
    def CheckRules(self, cat):
        """check the rules with the cat detected"""

        import logging

        for r in self.LoadAll():
            if not r.enabled:
                continue
        
            logging.info("Ruling rule #%d %s [%s] for %s" % (r.id, r.name, r.rule, cat))
            rm = RuleManager( r.rule )    
            rm.SetEnvironment(locals = { 'PET_NAME': cat });
            
            ret = rm.Run()
            if ret != None and ret:
                return r.id
            
        return None
            