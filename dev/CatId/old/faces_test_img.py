#!/usr/bin/env python
import cv2
import numpy as np
import sys

recognizer = cv2.face.createLBPHFaceRecognizer()
recognizer.load('trained.yml')
cascadePath = "cascades/orig/haarcascade_frontalcatface_extended.xml"
faceCascade = cv2.CascadeClassifier(cascadePath);


font = cv2.FONT_HERSHEY_SIMPLEX
im = cv2.imread(sys.argv[1])
gray=cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)
gray = cv2.equalizeHist(gray)
faces=faceCascade.detectMultiScale(gray, 1.2,5,
	minSize=(300, 300),
    	flags = cv2.CASCADE_SCALE_IMAGE)
for(x,y,w,h) in faces:
    cv2.rectangle(im,(x,y),(x+w,y+h),(225,0,0),2)
    Id,conf = recognizer.predict(gray[y:y+h,x:x+w])
    print Id,conf
    if(conf<20):
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
cv2.imshow('im',im) 
while True:
    if cv2.waitKey(10) & 0xFF==ord('q'):
        break
cv2.destroyAllWindows()
