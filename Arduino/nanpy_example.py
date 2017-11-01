#!/usr/bin/env python

from nanpy import (ArduinoApi, SerialManager)
from time import sleep

# for mac
connection = SerialManager(device='/dev/cu.wchusbserial1a1130')

# for raspy
#connection = SerialManager()

a = ArduinoApi(connection=connection)

a.pinMode(13, a.OUTPUT)

for i in range(10000):
    a.digitalWrite(13, (i + 1) % 2)
    sleep(0.2)