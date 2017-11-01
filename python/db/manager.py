import sqlite3
from events import Event, EventService
from pets import Pet, PetService
from rules import Rule, RuleService
from weights import Weight, WeightService

import db

class Manager:
    def __init__(self, dbfile=None):
        self.conn = None
        self.dbfile = dbfile
        
        if dbfile:
            self.Connect(dbfile)

        self.EventService = EventService()
        self.PetService = PetService()
        self.RuleService = RuleService()
        self.WeightService = WeightService()

    def Close(self):
        self.conn.close()

    def CloseAndCommit(self):
        self.conn.commit()
        self.conn.close()

    def Connect(self, dbfile):
        self.dbfile = dbfile
        db.conn = sqlite3.connect(self.dbfile)
        self.conn = db.conn
        # to handle unicode.
        # self.conn.text_factory = str
        
        
    #####################################################################
    

    
    #####################################################################
    
  

    #####################################################################
    
  


    #####################################################################
 
