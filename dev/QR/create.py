#!/usr/bin/env python

# usage: $0 text filename.png
# 499  pip install qrtools
#  500  pip install qrcode
#  502  pip install pyqrcode
# pip install pypng
# brew install zbar (mac)
# then pip install git+https://github.com/npinchot/zbar.git
# on raspy, apt-get install python-zbar
# crap
import pyqrcode
import sys
qr = pyqrcode.create(sys.argv[1],error='H',version=1)
qr.png(sys.argv[2],scale=6,quiet_zone=0)

