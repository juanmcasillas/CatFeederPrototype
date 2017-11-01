#!/usr/bin/env python

import sys
import os
import shutil
import os.path



def process(path, id):
    imagePaths=[os.path.join(path,f) for f in os.listdir(path)] 
    for i in imagePaths:
	fn,fe = os.path.splitext(i)
	dn = os.path.dirname(fn)
	bn = os.path.basename(fn)

	data = bn.split('-')
	n = data[0]
	s = data[1]

	tgt = "%s/%02d_%s-%02d%s" % (dn,int(id),n,int(s),fe)
	print "%s -> %s" % (i, tgt)
	os.rename(i,tgt)



if __name__ == "__main__":

	process(sys.argv[1], sys.argv[2])
