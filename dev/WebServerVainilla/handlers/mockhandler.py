import os

class D:
    def __init__(self):
        pass

class MockRequest:
    def __init__(self):
        self.wfile = open(os.devnull, "wb+")
        self.wfile
        
    def Dispose(self):
        self.wfile.close()
        
    def send_response(self, code): pass
    def end_headers(self): pass
    def send_header(self, header, value): pass
    

    
class HandlerAdapter:
    """
    Useful to invoke handlers from outside the webserver (e.g. create things, and so on.)
    """
    
    def __init__(self, opts):
        "given args in a dict way, convert to required one."
        self.opts = opts
       
    def Invoke(self, handler, args):
        
        mockrequest = MockRequest()
       
        request_args = {}
        
        for k in args.keys():
            request_args[k] = [args[k]]
      
      
        handler.Dispatch(self.opts, mockrequest, request_args)

        mockrequest.Dispose()