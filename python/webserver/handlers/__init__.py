
#import demo
import mockhandler

#from demo import Demo_Handler
from main import Main_Handler
from generic import Generic_Handler
from events import EventsJSON_Handler
from pets import PetList_Handler
from rules import RuleList_Handler

from control import ControlView_Handler


def RegisterHandlers( handlers={} ):

    external_handlers = main.RegisterHandlers(handlers)
    external_handlers = generic.RegisterHandlers(external_handlers)
    external_handlers = events.RegisterHandlers(external_handlers)
    external_handlers = pets.RegisterHandlers(external_handlers)
    external_handlers = rules.RegisterHandlers(external_handlers)
    external_handlers = control.RegisterHandlers(external_handlers)
   
    return external_handlers
