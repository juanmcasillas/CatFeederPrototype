#!/usr/bin/env python
import sys
import barcode
from barcode.writer import ImageWriter

EAN = barcode.get_barcode_class('ean8')
#ean = EAN(u'5901234123457',writer=ImageWriter())
ean = EAN(sys.argv[1],writer=ImageWriter())
ean.save(sys.argv[2])






