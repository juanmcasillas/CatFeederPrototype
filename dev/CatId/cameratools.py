from picamera.array import PiRGBArray
from picamera import PiCamera
import time

class PiCameraHandler:
    def __init__(self, resolution=None, framerate=None, rotation=None):
        self.cam = PiCamera()
        self.cam.resolution = resolution or (1024,768)
        self.cam.framerate = framerate or 32
        self.cam.rotation = rotation or 0

        self.rawCapture = PiRGBArray(self.cam, size=self.cam.resolution)
        time.sleep(1)
    
    def read(self, videoport=False):
        #for frame in self.cam.capture_continuous(self.rawCapture, format="bgr", use_video_port=False):
        #    im = frame.array
        #    self.rawCapture.truncate(0)
        #    yield 1,im
        frame = self.cam.capture(self.rawCapture, format="bgr", use_video_port=videport)
        im = self.rawCapture.array
        self.rawCapture.truncate(0)  
    	return 1,im
