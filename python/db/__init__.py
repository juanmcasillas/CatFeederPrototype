import datetime
import time
import sqlite3
import config
from events import Event, EventService
from pets import Pet, PetService
from rules import Rule, RuleService
from weights import Weight, WeightService
from manager import Manager

#import pytz    # $ pip install pytz
#import tzlocal # $ pip install tzlocal
#LOCAL_TZ = tzlocal.get_localzone() # get pytz tzinfo
#ConvertDateTime = lambda x: datetime.datetime.strptime(x, '%Y-%m-%d %H:%M:%S').replace(tzinfo=pytz.utc).astimezone(LOCAL_TZ)
#ConvertDate = lambda x: datetime.datetime.strptime(x, '%Y-%m-%d').replace(tzinfo=pytz.utc).astimezone(LOCAL_TZ)



# function helpers
FormatDateTime = lambda x: datetime.datetime.strftime(x, '%Y-%m-%d %H:%M:%S')
ConvertDateTime = lambda x: datetime.datetime.strptime(x, '%Y-%m-%d %H:%M:%S')

FormatDate  = lambda x: datetime.datetime.strftime(x, '%Y-%m-%d')
ConvertDate = lambda x: datetime.datetime.strptime(x, '%Y-%m-%d')


def Time2HMS_String(duration):
    m, s = divmod(duration.days * 86400 + duration.seconds, 60)
    h, m = divmod(m, 60)             
    r = "%02d:%02d:%02d" % (h,m,s)
    return r

def PhotoPath(timestamp):
    path = datetime.datetime.strftime(datetime.datetime.fromtimestamp(timestamp), '%Y/%m/%d')
    path = "%s/%s/%s.png" % (config.photodir, path, timestamp)           
    return path


# database
dbfile = None
conn = None
Row = sqlite3.Row

def Close(): 
    global conn

    conn.close()

def Commit():
    global conn

    conn.commit()

def CloseAndCommit():
    global conn

    conn.commit()
    conn.close()

def Connect(dbfilearg):
    global conn
    global dbfile
    
    dbfile = dbfilearg
    conn = sqlite3.connect(dbfile, check_same_thread=False)
    # to handle unicode.
    # self.conn.text_factory = str

# dummy object
O = config.O



