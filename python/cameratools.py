from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import config 

class PiCameraHandler:
    def __init__(self, resolution=None, framerate=None, rotation=None, videoport=True):
        self.cam = PiCamera()
        self.cam.resolution = resolution or (1024,768)
        self.cam.framerate = framerate or 32
        self.cam.rotation = rotation or 0
        self.videoport = videoport
       
        # internal configuration parameters
        self.cam.awb_mode = 'off'
        self.cam.awb_gains = (1.4, 2.3)
        
        #self.cam.annotate_frame_num = True
        #self.cam.exposure_mode = 'sports'
        self.cam.shutter_speed = 1/400
        self.cam.iso = 400
        self.cam.contrast = 25
        self.cam.exposure_compensation = 24 # 1 step (1/6)
        time.sleep(config.CAMERA_WAIT_TIME)
        self.cam.exposure_mode = 'off'
        
        self.rawCapture = PiRGBArray(self.cam, size=self.cam.resolution)
        
        
        
    def read(self):
        #for frame in self.cam.capture_continuous(self.rawCapture, format="bgr", use_video_port=self.videoport):
        #    im = frame.array
        #    self.rawCapture.truncate(0)
        #    yield 1,im
        frame = self.cam.capture(self.rawCapture, format="bgr", use_video_port=self.videoport)
        im = self.rawCapture.array
        self.rawCapture.truncate(0)  
        return 1,im
