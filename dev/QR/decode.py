#!/usr/bin/env python

# usage: $0 filename.png

import qrtools
import sys

qr = qrtools.QR()
qr.decode(sys.argv[1])
print qr.data


