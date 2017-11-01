
import re
from datetime import timedelta
from string import Formatter

#from check_pi import *

class O: 
    def __init__(self): pass
    
colors = O()
colors.event_not_allowed = 'red'

www = O()
www.generic_title = 'Cat Feeder: '
www.root = 'webserver/www'

photodir = '%s/snaps' % www.root # photos to store things.

last_image = '%s/last_image.png' % photodir # last stored image
test_image = 'testimage.png' # use for mock values

LOG_FILE = 'catfeeder.log'
LOG_FILE_MODE = "w+" # don't append, create new

TRAIN_MODE=True #let the door open

#
# timeout seconds in MANUAL MODE
#
SERVER_SLEEP = 1 #seconds
STATE_TIMEOUT = 30 # seconds
STATE_TIMEOUT = 10 # seconds (for test) MANUAL STATE.
WAIT_STATE_TIMEOUT  = 5 # seconds
WAIT_STATE_SLEEP = 1 # seconds
IDENTIFY_TIMEOUT = 10 # seconds
CAMERA_WAIT_TIME = 10 # seconds

# detector config

PERCENT_MATCH = 80
PERCENT_MATCH_THRESHOLD = 5
FRAMES_MATCH = 15



arduino = O()
arduino.detector_timeout  = 30 # seconds 
arduino.delay_pir_init    = 6 # seconds
arduino.light_max_power   = 200 # pwm
arduino.motor_max_power   = 200 # pwm

#
# database cats to load
#
CAT_DB_ITEMS = [ 'firulais','neko', 'eli' ]


# for foor loop arduino.motor_delay = 10
#if IsRaspberry():
#    arduino.motor_delay   = 45
 
arduino.motor_delay = 800 # ms    


pets = O()
pets.UNKNOWN_PET = -1 # the unknown pet (non identified)

def PathToURL(path):
    if not path:
        return None
    p = re.sub("^%s" % www.root ,"",path)
    return p
    
camera = O()
camera.width = 800
camera.height = 608
camera.fps = 30
camera.rotation = 180

def StrUptime():
    return strfdelta(timedelta(seconds = uptime()))

def uptime():  
    with open('/proc/uptime', 'r') as f:
        uptime_seconds = float(f.readline().split()[0])
        #uptime_string = str(timedelta(seconds = uptime_seconds))
        return uptime_seconds
    
    
#https://stackoverflow.com/questions/538666/python-format-timedelta-to-string
def strfdelta(tdelta, fmt='{D:02}d {H:02}h {M:02}m {S:02}s', inputtype='timedelta'):
    """Convert a datetime.timedelta object or a regular number to a custom-
    formatted string, just like the stftime() method does for datetime.datetime
    objects.

    The fmt argument allows custom formatting to be specified.  Fields can 
    include seconds, minutes, hours, days, and weeks.  Each field is optional.

    Some examples:
        '{D:02}d {H:02}h {M:02}m {S:02}s' --> '05d 08h 04m 02s' (default)
        '{W}w {D}d {H}:{M:02}:{S:02}'     --> '4w 5d 8:04:02'
        '{D:2}d {H:2}:{M:02}:{S:02}'      --> ' 5d  8:04:02'
        '{H}h {S}s'                       --> '72h 800s'

    The inputtype argument allows tdelta to be a regular number instead of the  
    default, which is a datetime.timedelta object.  Valid inputtype strings: 
        's', 'seconds', 
        'm', 'minutes', 
        'h', 'hours', 
        'd', 'days', 
        'w', 'weeks'
    """

    # Convert tdelta to integer seconds.
    if inputtype == 'timedelta':
        remainder = int(tdelta.total_seconds())
    elif inputtype in ['s', 'seconds']:
        remainder = int(tdelta)
    elif inputtype in ['m', 'minutes']:
        remainder = int(tdelta)*60
    elif inputtype in ['h', 'hours']:
        remainder = int(tdelta)*3600
    elif inputtype in ['d', 'days']:
        remainder = int(tdelta)*86400
    elif inputtype in ['w', 'weeks']:
        remainder = int(tdelta)*604800

    f = Formatter()
    desired_fields = [field_tuple[1] for field_tuple in f.parse(fmt)]
    possible_fields = ('W', 'D', 'H', 'M', 'S')
    constants = {'W': 604800, 'D': 86400, 'H': 3600, 'M': 60, 'S': 1}
    values = {}
    for field in possible_fields:
        if field in desired_fields and field in constants:
            values[field], remainder = divmod(remainder, constants[field])
    return f.format(fmt, **values)
