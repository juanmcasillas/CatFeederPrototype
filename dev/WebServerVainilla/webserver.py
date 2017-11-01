#!/usr/bin/env python


import sys
import logging
import www
import dbmanager
import os
import os.path
import codecs
import handlers
import cache
import argparse



if __name__ == '__main__':
    #main()  # this allows library functionality


    parser = argparse.ArgumentParser()

    parser.add_argument("-d", "--debug", help="Show debug info", action="store", default="info")
    parser.add_argument("-c", "--cachedir", help="Where the cache is stored", action="store", default="cache")
    parser.add_argument("database", help="DatabaseFile")


    args = parser.parse_args()

    opts = www.Opts()

    opts.host = 'localhost'
    opts.port = 8088
    opts.rootdir = 'www'
    opts.no_dirlist = False
    opts.level = args.debug
    opts.dbfile = args.database
    opts.nocache = False
    opts.cachedir = args.cachedir

    
    external_handlers = handlers.RegisterHandlers()

    # map some things (alias)

    #external_handlers["/"] = external_handlers["/demo"]

    for e in external_handlers.keys():
        print "Registered Handler(%s)" % e

    print "WWWRootDir: '%s'" % opts.rootdir
    print "CacheDir: '%s'" % opts.cachedir
    print "DBFile: '%s'" % opts.dbfile
    logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s', level=logging.INFO)
    www.httpd(opts, external_handlers)
