#!/usr/bin/env python


import sys
import logging
import www
import os
import os.path
import codecs
import handlers
import cache
import argparse
import thread
import threading
import db


def start_www_server_standalone(opts):

    external_handlers = handlers.RegisterHandlers()
    #db.Connect(opts.dbfile)

    # map some things (alias)
    #external_handlers["/"] = external_handlers["/demo"]

    for e in external_handlers.keys():
        logging.info( "Registered Handler(%s)" % e)

    logging.info("WWWRootDir: '%s'" % opts.rootdir)
    #print "CacheDir: '%s'" % opts.cachedir
    #print "DBFile: '%s'" % opts.dbfile
    #logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s', level=logging.INFO)
    www.httpd(opts, external_handlers)    

def start_www_server_thread(opts):

    thread.start_new_thread(start_www_server_standalone , (opts,))


if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    #parser.add_argument("-d", "--debug", help="Show debug info", action="store", default="info")
    #parser.add_argument("-c", "--cachedir", help="Where the cache is stored", action="store", default="cache")
    #parser.add_argument("database", help="DatabaseFile")


    args = parser.parse_args()

    opts = www.Opts()

    opts.host = 'localhost'
    opts.port = 8088
    opts.rootdir = 'www'
    opts.no_dirlist = False
    #opts.level = args.debug
    #opts.nocache = False
    #opts.dbfile = args.database
    #opts.cachedir = args.cachedir
    
    start_www_server_standalone(opts)
