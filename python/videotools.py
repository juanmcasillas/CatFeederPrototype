#!/usr/bin/env python

import cv2

class VideoInfo:
    def __init__(self,stream,fname):
        self.fname = fname
        self.width =  int(stream.get(cv2.CAP_PROP_FRAME_WIDTH ))
        self.height = int(stream.get(cv2.CAP_PROP_FRAME_HEIGHT ))
        self.frames = int(stream.get(cv2.CAP_PROP_FRAME_COUNT ))
        self.fps    = int(stream.get(cv2.CAP_PROP_FPS ))
        self.length = (self.frames / float(self.fps))


    def PrintInfo(self):
        print "Video Information ------------------------------------------------- "
        print "File:\t%s" % self.fname
        print "WIDTH:\t%d" % self.width
        print "HEIGHT:\t%d" % self.height
        print "FRAMES:\t%d" % self.frames
        print "FPS:\t%d" % self.fps
        print "LENGTH:\t%3.2fs" % self.length
        print "Video Information ------------------------------------------------- "
        
def WaitForKeyToExit():
    
    key = cv2.waitKey(10)
    if key == 27 or key==ord('q'):
        return False
    
    return True
