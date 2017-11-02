#!/usr/bin/env python
import cv2
import numpy as np
import sys

from picamera.array import PiRGBArray
from picamera import PiCamera
import time

recognizer = cv2.face.createLBPHFaceRecognizer()
recognizer.load('trainner.yml')
cascadePath = "cascades/orig/haarcascade_frontalcatface_extended.xml"
faceCascade = cv2.CascadeClassifier(cascadePath);


cam = PiCamera()
cam.resolution = (800,608)
cam.framerate = 30
rawCapture = PiRGBArray(cam, size=(800,608))
time.sleep(0.1)

font = cv2.FONT_HERSHEY_SIMPLEX

for frame in cam.capture_continuous(rawCapture, format="bgr", use_video_port=True):

    im = frame.array
    gray=cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist(gray)
    faces=faceCascade.detectMultiScale(gray, 1.2,5,
        minSize=(250, 250),
        flags = cv2.CASCADE_SCALE_IMAGE)
    for(x,y,w,h) in faces:
        cv2.rectangle(im,(x,y),(x+w,y+h),(225,0,0),2)
        Id,conf = recognizer.predict(gray[y:y+h,x:x+w])
	print Id,conf
        if(conf<50):
            if(Id==1):
                Id="Eli %3.2f" % conf
            elif Id==2:
                Id="Firulais %3.2f" % conf
            elif Id==3:
                Id="Neko %3.2f" % conf
            else:
                Id="Unknown**"
        else:
            Id="Unknown"
        cv2.putText(im,str(Id), (x,y+h),font, 1, (200,255,255),2,cv2.LINE_AA)

    cv2.imshow("Image", im)
    if cv2.waitKey(10) & 0xFF==ord('q'):
        break
    rawCapture.truncate(0)
cv2.destroyAllWindows()
