#!/usr/bin/env bash

HOST=192.168.0.163
SERIAL=''
python catfeeder_server.py catfeeder.db --serial_port=$SERIAL --host=$HOST >/tmp/catfeeder.log 2>&1