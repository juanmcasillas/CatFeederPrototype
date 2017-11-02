#!/usr/bin/env python
import cv2
import numpy as np
import time
import sys
import re
import os
# http://www.vision-ary.net/2015/03/boost-the-world-cat-faces/



class Recognizer:
    def __init__(self, trained_file=None, confidence=None, verbose=None):

        self.verbose = verbose or True
        #self.cascade_file = "cascades/lbp/lbpcascade_frontalcatface.xml"
        self.cascade_file = "cascades/visionary.net_cat_cascade_web_LBP.xml"
        #self.cascade_file = "cascades/orig/haarcascade_frontalcatface_extended.xml"



        self.trained_file = trained_file
        self.recognizer = cv2.face.createLBPHFaceRecognizer()
        #self.recognizer = cv2.face.createEigenFaceRecognizer() #require same size
        #self.recognizer = cv2.face.createFisherFaceRecognizer()#require same size

        if self.trained_file:
            self.recognizer.load(self.trained_file)

        self.detector_face = cv2.CascadeClassifier(self.cascade_file)

        #self.eye_cascade_file = "cascades/orig/haarcascade_eye.xml"
        #self.detector_eye =  cv2.CascadeClassifier(self.eye_cascade_file)

        self.default_font = cv2.FONT_HERSHEY_SIMPLEX
        self.scaleFactor=1.04
        self.minNeighbors=5
        self.minSize = (200,200)
        self.maxSize = (600,600) # not limit
        self.flags = cv2.CASCADE_SCALE_IMAGE
        #self.flags = cv2.CASCADE_FIND_BIGGEST_OBJECT | cv2.CASCADE_DO_ROUGH_SEARCH

        self.confidence = confidence or 30

        # for trainning
        self.face_samples=[]
        self.face_ids=[]


    def Configure(self, scaleFactor=None, minNeighbors=None, minSize=None, maxSize = None, flags=None):
        self.scaleFactor=scaleFactor or self.scaleFactor
        self.minNeighbors=minNeighbors or self.minNeighbors
        self.minSize = minSize or self.minSize
        self.maxSize = maxSize or self.maxSize
        self.flags = flags or self.flags

    def PrintConfig(self):
        print "scaleFactor: %3.2f" % self.scaleFactor
        print "minNeighbors: %d" % self.minNeighbors
        print "minSize: ", self.minSize
        print "maxSize: ", self.maxSize
        print "flags: ", self.flags


    def SetInputFile(self, t):
        self.input_file = t

    def SetConfidence(self, c):
        self.confidence = c

    def Crop(self, im, sz):
        tgt = im[0:sz[0], 0:sz[1]]
        return tgt


    def Detect(self, im):

        # set the minimum dinamically.
        #height, width = im.shape
        #min_percent = 30
        #min_percent_w = min_percent
        #min_percent_h = min_percent
        #minSize_calc = ( int(width * (min_percent_w/100)), int(height * (min_percent_h/100)) )

        faces=self.detector_face.detectMultiScale(im,
                    scaleFactor=self.scaleFactor,
                    minNeighbors=self.minNeighbors,
                    minSize= self.minSize,
                    #maxSize=self.maxSize,
                    flags = self.flags)

        # get the big one.

        tmp = []
        max_ptr = 0
        max_w = 0
        for i in range(len(faces)):
            (x,y,w,h) = faces[i]
            if w > max_w:
                max_ptr = i
                max_w = w

        if len(faces) > 0:
            faces = [ faces[max_ptr] ]

        return faces


    def ExtractFace(self,id, im, fname='-'):

        gray = cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)

        faces = self.Detect(gray)

        for (x,y,w,h) in faces:
            if self.verbose:
                print "(cat) Face Found at %s (id: %d)" % (fname, id)
            self.face_samples.append(gray[y:y+h,x:x+w])
            self.face_ids.append(id)
            
            annotated_im = im.copy()
            cv2.rectangle(annotated_im,(x,y),(x+w,y+h),(225,0,0),2)

        if len(faces) == 0:
            return []

        return annotated_im

    def TrainAndSave(self, output_file):

        if len(self.face_samples) == 0:
            return False

        self.recognizer.train(self.face_samples, np.array(self.face_ids))
        self.recognizer.save(output_file)
        return True


    def MatchFaces(self, im):
        """process the given image, try to detect faces"""
        gray=cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)

        #faces = self.Detect(gray)
        faces = self.Detect(gray)
        idmatch = ""

        for(x,y,w,h) in faces:
            cv2.rectangle(im,(x,y),(x+w,y+h),(225,0,0),2)
            id,confidence = self.recognizer.predict(gray[y:y+h,x:x+w])
            im,idmatch = self.ProcessMatch(im, id, confidence, (x,y,w,h))

        return im,idmatch


    def ProcessMatch(self, im, id, confidence, pos):
        "do the work with the given data in the image"

        x,y,w,h = pos
        idmatch = ""
        if self.verbose:
            print "Id: %d, Confidence: %3.2f" % (id,confidence)

        if(confidence<self.confidence):
            if(id==1):
                id="Eli %3.2f" % confidence
                idmatch = "eli"
            elif id==2:
                id="Firulais %3.2f" % confidence
                idmatch = "firulais"
            elif id==3:
                id="Neko %3.2f" % confidence
                idmatch = "neko"
            else:
                id="Unknown**"
                idmatch = "unknown"
            cv2.putText(im,str(id), (x,y+h),self.default_font, 1, (200,255,255),2,cv2.LINE_AA)

        else:
            id="Unknown %3.2f" % self.confidence


        return im, idmatch

    def ExtractData(self, fpath):

        # file naming format
        # 03_neko-01.jpg
        # ID_label-COUNTER.jpg

        #fn,fe = os.path.splitext(imagePath)
        #dn = os.path.dirname(fn)
        bn = os.path.basename(fpath)

        #data = bn.split('_')
        #id = int(data[0])

        r = re.match("(\d+)_(\w+)-(\d+)\.+",bn)
        if not r:
            return None

        return int(r.groups()[0]), r.groups()[1]


    #### dev functions
    #### until here
    

    def DetectCompound(self, im):

        #height, width = im.shape

        # set the minimum dinamically.
        #min_percent = 30
        #min_percent_w = min_percent
        #min_percent_h = min_percent
        #minSize_calc = ( int(width * (min_percent_w/100)), int(height * (min_percent_h/100)) )

        faces=self.detector_face.detectMultiScale(im,
                    scaleFactor=self.scaleFactor,
                    minNeighbors=self.minNeighbors,
                    minSize= self.minSize,
                    #maxSize=self.maxSize,
                    flags = self.flags)

        for faceRect in faces:
            face = Face()
            face.faceRect = faceRect
            x, y, w, h = faceRect
            # Seek an eye in the upper-left part of the face.
            searchRect = (x+w/9, y, w*2/4, int(h/1.5))
            
            cv2.rectangle(im,(x+(w/9),y),(x+(w*2/4),y+int(h/1.5)),(0,225,0),2)
            face.leftEyeRect = self._detectOneObject(self.detector_eye, im, searchRect, 64)
            cv2.imshow('im',im)
            cv2.waitKey(200) 
            if face.leftEyeRect:
                print "otra al bote"

        
        return faces

    def _detectOneObject(self, classifier, image, rect, imageSizeToMinSizeRatio):
        x, y, w, h = rect
        minSize = self._widthHeightDividedBy(image, imageSizeToMinSizeRatio)
        subImage = image[y:y+h, x:x+w]
        subRects = classifier.detectMultiScale(subImage, self.scaleFactor, self.minNeighbors, self.flags, minSize)
        if len(subRects) == 0:
            return None
        subX, subY, subW, subH = subRects[0]
        return (x+subX, y+subY, subW, subH)

    def _widthHeightDividedBy(self, image, divisor):
        """Return an image's dimensions, divided by a value."""
        h, w = image.shape[:2]
        return (w/divisor, h/divisor)


class Face(object):
    """Data on facial features: face, eyes, nose, mouth."""
    def __init__(self):
        self.faceRect = None
        self.leftEyeRect = None
        self.rightEyeRect = None
        self.noseRect = None
        self.mouthRect = None
