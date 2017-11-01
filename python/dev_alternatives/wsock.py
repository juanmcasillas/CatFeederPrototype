
import logging
import thread
import threading
from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket

import wsockreceiver


class WSockHandler(WebSocket):
    
    def handleMessage(self):
        
        # can't send messages TO client. I don't know why. Try at home.
        try:
            wsockreceiver.HandleCommand(self.data, self)
            #model.MODEL.printdata()
            #on windows (work) this crashes
            #self.sendMessage(unicode("TwichDrone ready to rock!","utf-8"));
            
        except Exception, e:
            s = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime())
            logging.error("WEBSOCKET:handleMessage Exception %s " % (e))

    def handleConnected(self):
        logging.info("WEBSOCKET:handleConnected: %s:%d Connected" % (self.address[0], self.address[1]))
        

    def handleClose(self):
        logging.info("WEBSOCKET:handleClose: %s:%d Closed" % (self.address[0], self.address[1]))


        
def websocketserver_thread(host='',port=8000):
    server = SimpleWebSocketServer(host, port, WSockHandler)
    server.serveforever()
    
def websocketserver_start(host='',port=8000):
     thread.start_new_thread(websocketserver_thread , (host, port ))
     

if __name__ == "__main__":
    
    websocketserver_thread()