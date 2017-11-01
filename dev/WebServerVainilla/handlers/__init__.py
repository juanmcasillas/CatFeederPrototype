
#import demo
import mockhandler

#from demo import Demo_Handler
from main import Main_Handler


def RegisterHandlers( handlers={} ):

    external_handlers = main.RegisterHandlers(handlers)
    return external_handlers
