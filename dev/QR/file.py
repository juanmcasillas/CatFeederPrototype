#!/usr/bin/env python

import sys
import os.path

from PIL import  Image
import zbar

if __name__ == "__main__":

    scanner = zbar.ImageScanner()
    scanner.parse_config('enable')
    pil = Image.open(sys.argv[1])
    width, height = pil.size
    raw = pil.convert('L').tostring()
    print pil.format

    image = zbar.Image(width,height,'Y800',raw)
    scanner.scan(image)

    for symbol in image:
       print 'decoded', symbol.type, 'symbol', '"%s"' % symbol.data
    del(image)

    
