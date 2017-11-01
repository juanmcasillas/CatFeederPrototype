import sqlite3
import sys


class EmptyObject:
    def __init__(self):
        pass


class AbstractTable:
    def __init__(self):
        pass
    
    def load(self, conn, query=None, kind=None):
        
        if query and kind:
            q = query
            k = kind 
        else:
            q,k = self.sql_load()

        conn.row_factory = sqlite3.Row

        cursor = conn.cursor()
        cursor.execute(q)
        
        row = cursor.fetchone()
        if not row:
            return None
        
        d = k()
        for i in row.keys():
            setattr(d, i.lower(), row[i])
        d.after_load()
        
        return d
    
    
    def load_all(self, conn, query=None, kind=None):
        
        if query and kind:
            q = query
            k = kind 
        else:
            q,k = self.sql_load_all()
        
        t = []

        conn.row_factory = sqlite3.Row
        
        for row in conn.execute(q):
            d = k()
            for i in row.keys():
                setattr(d, i.lower(), row[i])

            d.after_load()
            t.append(d)
        return t

    def insert(self, conn, query=None):
        
        if query:
            q = query
        else:
            q = self.sql_insert()

        cursor = conn.cursor()
        cursor.execute(q)
        self.id = cursor.lastrowid

        # print s, self.id

    def update(self, conn, query=None):
        if query:
            q = query 
        else:
            q = self.sql_update()
        
        r = conn.execute(q)
        return r

    def delete(self, conn, query=None):
        if query:
            q = query 
        else:
            q = self.sql_delete()
        
        r = conn.execute(q)
        return r

    def delete_all(self, conn, query=None):
        if query:
            q = query 
        else:
            q = self.sql_delete_all()
      
        r = conn.execute(q)
        return r        

    def __str__(self):
        s = ""
        for i in self.__dict__.keys():
            s += "%s(%s) " % (i, self.__dict__[i])
            
        return s
        
        
        #s = "id(%d) start(%s) end(%s) petid(%d) allowed(%d) rule(%d)" % (self.id, self.start, self.end, self.petid, self.allowed, self.rule)
        #return s
        
        
    ## overload this
    def sql_load_all_q(self): return "",None
    def sql_load_q(self): return "",None
    def sql_insert(self): return ""
    def sql_update(self): return ""
    def sql_delete(self): return ""
    def after_load(self): pass
