#!/usr/bin/env python

# python dbmanager.py -c trackdb.db
# python dbmanager.py -vv -l "samples\Archive\Cartography\files\MTB\2015\2015-06-18-16-37-58 - [MTB,ETREX30,CANYON_CF] Navas - Robledo (Antena) - GR10 - Puerto Navas.gpx" trackdb.db -d "Sample route to insert into DB"

#sqlite3 yourdb .dump > /tmp/db.txt
#edit /tmp/db.txt change column name in Create line
#sqlite2 yourdb2 < /tmp/db.txt
#mv/move yourdb2 yourdb
# moved to git

import sqlite3
import sys



sys.path.insert(1, '..')
sys.path.append("..")

import os
import os.path
import shutil
import argparse
import glob
import pytz
import tzlocal
import re



import WebServer.handlers

# pip install pytz
# pip install tzlocal

class D:
    def __init__(self):
        pass

class BaseDB:
    def __init__(self):
        pass

    @staticmethod
    def sql_create_script(): return ""

    @staticmethod
    def sql_insert_script(): return ""

    def sql_load_script(self): return ""


    def insert(self, conn):
        s = self.sql_insert_script()

        cursor = conn.cursor()
        cursor.execute(s)
        self.id = cursor.lastrowid

        # print s, self.id

    def load(self, conn):
        s = self.sql_load_script()

        cursor = conn.cursor()
        cursor.execute(s)
        # do specific things here for each class
        return cursor.fetchone()


class Track(BaseDB):

    def __init__(self, kind, device, equipment, description=None, gpx=None, fname=""):

        BaseDB.__init__(self)

        self.id = None
        self.fname = fname
        self.gpx = ""
        self.kml = ""
        self.distance = 0.0
        self.elevation = 0.0
        self.time_moving = 0  # time
        self.duration = 0
        self.start_stamp = 0.0
        self.speed_avg = 0.0
        self.kind = kind
        self.device = device
        self.equipment = equipment
        self.description = description
        self.rating = 0
        self.fextension = None
        self.places = None
        # use FNAME by default.
        self.title = fname
        self.circular = 1
        self.SW_lat = 0.0
        self.SW_lon = 0.0
        self.NE_lat = 0.0
        self.NE_lon = 0.0
        self.cloned = 0
        self.numpoints = 0
        # stats
        self.score = 0
        self.uphill_distance = 0.0
        self.level_distance = 0.0
        self.downhill_distance = 0.0
        self.uphill_elevation = 0.0
        self.level_elevation = 0.0
        self.downhill_elevation = 0.0
        self.uphill_avg_slope = 0.0
        self.level_avg_slope = 0.0
        self.downhill_avg_slope = 0.0
        self.uphill_p_distance = 0.0
        self.level_p_distance = 0.0
        self.downhill_p_distance = 0.0
        # speed stats

        self.uphill_speed = 0.0
        self.level_speed = 0.0
        self.downhill_speed = 0.0

        self.uphill_time = 0.0
        self.level_time = 0.0
        self.downhill_time = 0.0

        self.uphill_p_time = 0.0
        self.level_p_time = 0.0
        self.downhill_p_time = 0.0

        self.center_lat = 0.0
        self.center_lon = 0.0
        self.clockwise = 0

        self.uphill_slope_ranges_distance = []
        self.downhill_slope_ranges_distance = []
        self.uphill_slope_ranges_time = []
        self.downhill_slope_ranges_time = []
        self.max_altitude = 0.0
        self.min_altitude = 0.0
        self.quality = 0.0


        if gpx:
            self.LoadGPXData(gpx)

        # if we have name, look metadata, use it from name
        if self.fname != "":
            stamp, tags, places, fextension = self.ParseFileName(os.path.basename(self.fname))

            _kind = None
            _device = None
            _equipment = None

            if tags:
                if len(tags) == 1:
                    _kind = tags[0]

                if len(tags) == 2:
                    _kind, _device = tags
                if len(tags) == 3:
                    _kind, _device, _equipment = tags

            if stamp: self.start_stamp = stamp
            if places: self.places = places

            self.fextension = fextension

            # if passed, override some things

            if not self.kind and _kind: self.kind = _kind
            if not self.device and _device: self.device = _device
            if not self.equipment and _equipment: self.equipment = _equipment


    @staticmethod
    def sql_create_script():
        s = """
            CREATE TABLE TRACKS (
                ID          INTEGER PRIMARY KEY AUTOINCREMENT,
                FNAME       TEXT DEFAULT "",
                GPX         BLOB,
                KML         BLOB,

                DISTANCE    REAL DEFAULT 0.0,
                ELEVATION   REAL DEFAULT 0.0,
                -- TIME_MOVING DATETIME DEFAULT (STRFTIME('%Y-%m-%d %H:%M:%f', 0)),
                -- DURATION    DATETIME DEFAULT (STRFTIME('%Y-%m-%d %H:%M:%f', 0)),
                -- START_STAMP DATETIME DEFAULT (STRFTIME('%Y-%m-%d %H:%M:%f', 0)),
                TIME_MOVING INTEGER DEFAULT 0,
                DURATION    INTEGER DEFAULT 0,
                START_STAMP INTEGER DEFAULT 0,
                SPEED_AVG   REAL DEFAULT 0.0,

                KIND        TEXT DEFAULT "",
                DEVICE      TEXT DEFAULT "",
                EQUIPMENT   TEXT DEFAULT "",
                DESCRIPTION TEXT DEFAULT "",
                RATING      INTEGER DEFAULT 0,
                TITLE       TEXT DEFAULT "",
                CIRCULAR    INTEGER DEFAULT 1,

                -- bound information
                SW_LAT      REAL DEFAULT 0.0,
                SW_LON      REAL DEFAULT 0.0,
                NE_LAT      REAL DEFAULT 0.0,
                NE_LON      REAL DEFAULT 0.0,
                CLONED      INTEGER DEFAULT 0,
                NUMPOINTS   INTEGER DEFAULT 0,

                -- stats
                SCORE               REAL DEFAULT 0,
                UPHILL_DISTANCE     REAL DEFAULT 0,
                LEVEL_DISTANCE      REAL DEFAULT 0,
                DOWNHILL_DISTANCE   REAL DEFAULT 0,
                UPHILL_ELEVATION    REAL DEFAULT 0,
                LEVEL_ELEVATION     REAL DEFAULT 0,
                DOWNHILL_ELEVATION  REAL DEFAULT 0,
                UPHILL_AVG_SLOPE    REAL DEFAULT 0,
                LEVEL_AVG_SLOPE     REAL DEFAULT 0,
                DOWNHILL_AVG_SLOPE  REAL DEFAULT 0,
                UPHILL_P_DISTANCE   REAL DEFAULT 0,
                LEVEL_P_DISTANCE    REAL DEFAULT 0,
                DOWNHILL_P_DISTANCE REAL DEFAULT 0,

                --speed
                UPHILL_SPEED        REAL DEFAULT 0,
                LEVEL_SPEED         REAL DEFAULT 0,
                DOWNHILL_SPEED      REAL DEFAULT 0,
                UPHILL_TIME         INTEGER DEFAULT 0,
                LEVEL_TIME          INTEGER DEFAULT 0,
                DOWNHILL_TIME       INTEGER DEFAULT 0,
                UPHILL_P_TIME       REAL DEFAULT 0,
                LEVEL_P_TIME        REAL DEFAULT 0,
                DOWNHILL_P_TIME     REAL DEFAULT 0,
                CENTER_LAT          REAL DEFAULT 0.0,
                CENTER_LON          REAL DEFAULT 0.0,
                CLOCKWISE           INTEGER DEFAULT 0,  -- 0 means clockwise route
                UPHILL_SLOPE_RANGE_DISTANCE     TEXT DEFAULT "",
                DOWNHILL_SLOPE_RANGE_DISTANCE   TEXT DEFAULT "",
                UPHILL_SLOPE_RANGE_TIME         TEXT DEFAULT "",
                DOWNHILL_SLOPE_RANGE_TIME       TEXT DEFAULT "",
                MAX_ALTITUDE         REAL DEFAULT 0.0,
                MIN_ALTITUDE         REAL DEFAULT 0.0,
                QUALITY              REAL DEFAULT 0.0

             );
        """
        return s

    def sql_insert_script(self):
        # print type(self.time_moving)
        # print type(self.duration)
        # print type(self.start_stamp)


        s = "insert into TRACKS values(NULL,'%s','%s','%s',%f,%f,%d,%d,%d,%f,'%s','%s','%s','%s','%d','%s', '%d', '%f', '%f', '%f', '%f', '%d', '%d'," + \
            "'%f','%f','%f','%f','%f','%f','%f','%f','%f','%f','%f','%f','%f'," + \
            "'%f','%f','%f','%d','%d','%d','%f','%f','%f'," + \
            "'%f','%f','%d'," + \
            "'%s','%s','%s','%s'," +\
            "'%f','%f','%f'" +\
            ")"

        s = s % (self.fname,
                    self.gpx,
                    self.kml,
                    self.distance,
                    self.elevation,
                    self.time_moving,
                    self.duration,
                    self.start_stamp,
                    self.speed_avg,
                    self.kind,
                    self.device,
                    self.equipment,
                    self.description,
                    self.rating,
                    self.title,
                    self.circular,
                    self.SW_lat,
                    self.SW_lon,
                    self.NE_lat,
                    self.NE_lon,
                    self.cloned,
                    self.numpoints,
                    self.score,
                    self.uphill_distance, self.level_distance, self.downhill_distance,
                    self.uphill_elevation, self.level_elevation, self.downhill_elevation,
                    self.uphill_avg_slope, self.level_avg_slope, self.downhill_avg_slope,
                    self.uphill_p_distance, self.level_p_distance, self.downhill_p_distance,

                    self.uphill_speed, self.level_speed, self.downhill_speed,
                    self.uphill_time, self.level_time, self.downhill_time,
                    self.uphill_p_time, self.level_p_time, self.downhill_p_time,

                    self.center_lat, self.center_lon, self.clockwise,
                    self.uphill_slope_ranges_distance, self.downhill_slope_ranges_distance, self.uphill_slope_ranges_time, self.downhill_slope_ranges_time,
                    self.max_altitude, self.min_altitude,
                    self.quality
                    )

        return s

    def sql_select_id_from_name(self):
        s = "select id from TRACKS where fname = '%s'" % self.fname
        return s

    def sql_load_script(self):
        s = "select * from TRACKS where id=%d" % int(self.id)
        return s

    def LoadGPXFromFile(self):
        fd = open(self.fname, "rb")
        self.gpx = fd.read()
        fd.close()


    def ExistsInDB(self, conn):
        q = self.sql_select_id_from_name()

        cursor = conn.cursor()
        cursor.execute(q)
        data = cursor.fetchone()
        if not data:
            return False

        return True

    def load(self, conn):
        s = self.sql_load_script()

        cursor = conn.cursor()
        cursor.execute(s)
        data = cursor.fetchone()

        if not data:
            return False


        self.fname = data[1]
        self.gpx = data[2]
        self.kml = data[3]
        self.distance = data[4]
        self.elevation = data[5]
        self.time_moving = data[6]
        self.duration = data[7]
        self.start_stamp = data[8]
        self.speed_avg = data[9]
        self.kind = data[10]
        self.device = data[11]
        self.equipment = data[12]
        self.description = data[13]
        self.rating = data[14]
        self.title = data[15]
        self.circular = data[16]
        self.SW_lat = data[17]
        self.SW_lon = data[18]
        self.NE_lat = data[19]
        self.NE_lon = data[20]
        self.cloned = data[21]
        self.numpoints = data[22]
        # stats
        self.score = data[23]
        self.uphill_distance = data[24]
        self.level_distance = data[25]
        self.downhill_distance = data[26]
        self.uphill_elevation = data[27]
        self.level_elevation = data[28]
        self.downhill_elevation = data[29]
        self.uphill_avg_slope = data[30]
        self.level_avg_slope = data[31]
        self.downhill_avg_slope = data[32]
        self.uphill_p_distance = data[33]
        self.level_p_distance = data[34]
        self.downhill_p_distance = data[35]
        # speed
        self.uphill_speed = data[36]
        self.level_speed = data[37]
        self.downhill_speed = data[38]
        self.uphill_time = data[39]
        self.level_time = data[40]
        self.downhill_time = data[41]
        self.uphill_p_time = data[42]
        self.level_p_time = data[43]
        self.downhill_p_time = data[44]
        # center
        self.center_lat = data[45]
        self.center_lon = data[46]
        self.clockwise = data[47]

        self.uphill_slope_ranges_distance = data[48]
        self.downhill_slope_ranges_distance = data[49]
        self.uphill_slope_ranges_time = data[50]
        self.downhill_slope_ranges_time = data[51]

        self.max_altitude = data[52]
        self.min_altitude = data[53]
        self.quality = data[54]

        _, self.fextension = os.path.splitext(self.fname)
        self.places = []
        # get the places

        q_places = 'select p.id,p.name,p.latitude,p.longitude,p.elevation,p.description from track_in_places tt, places p where tt.id_place = p.id and tt.id_track=%d' % int(self.id)
        for row in cursor.execute(q_places):
            p = Place()
            p.id = int(row[0])
            p.name = row[1]
            p.latitude = row[2]
            p.longitude = row[3]
            p.elevation = row[4]
            p.description = row[5]
            self.places.append({'name': p.name, 'id': p.id })  # just name, json power.

        # print self.Print()
        return True

    def SetStats(self, stats):

        self.score = float(stats.score)
        self.uphill_distance = float(stats.up_slope.distance)
        self.level_distance = float(stats.level_slope.distance)
        self.downhill_distance = float(stats.down_slope.distance)
        self.uphill_elevation = float(stats.up_slope.elevation)
        self.level_elevation = float(stats.level_slope.elevation)
        self.downhill_elevation = float(stats.down_slope.elevation)
        self.uphill_avg_slope = float(stats.up_slope.avg)
        self.level_avg_slope = float(stats.level_slope.avg)
        self.downhill_avg_slope = float(stats.down_slope.avg)
        self.uphill_p_distance = float(stats.up_slope.p_distance)
        self.level_p_distance = float(stats.level_slope.p_distance)
        self.downhill_p_distance = float(stats.down_slope.p_distance)

        self.uphill_speed = float(stats.up_slope.speed)
        self.level_speed = float(stats.level_slope.speed)
        self.downhill_speed = float(stats.down_slope.speed)

        self.uphill_time = int(stats.up_slope.time)
        self.level_time = int(stats.level_slope.time)
        self.downhill_time = int(stats.down_slope.time)

        self.uphill_p_time = float(stats.up_slope.p_time)
        self.level_p_time = float(stats.level_slope.p_time)
        self.downhill_p_time = float(stats.down_slope.p_time)

        # for low slopes, this is not accurate.
        #self.elevation = float(stats.up_slope.elevation)
        self.elevation = float(stats.uphill)
        self.distance = float(stats.length)

        self.center_lat = stats.center_latitude
        self.center_lon = stats.center_longitude

        #0   -> not clockwise (default, stats)
        #1   -> clockwise (default, stats)
        #2   -> not clockwise (WEB)
        #3   -> clockwise (WEB)

        if self.clockwise <= 1:
            self.clockwise = stats.clockwise

        self.numpoints = int(stats.numpoints)

        # attributes from CALCULATED

        self.duration = int(stats.duration)
        self.speed_avg = float(stats.speed_avg)

        self.uphill_slope_ranges_distance = ";".join( map(lambda x: "%s" % x, stats.up_slope.range_distance))
        self.downhill_slope_ranges_distance = ";".join( map(lambda x: "%s" % x,stats.down_slope.range_distance))

        self.uphill_slope_ranges_time = ";".join(map(lambda x: "%s" % x, stats.up_slope.range_time))
        self.downhill_slope_ranges_time = ";".join(map(lambda x: "%s" % x, stats.down_slope.range_time))

        self.max_altitude = float(stats.max_altitude)
        self.min_altitude = float(stats.min_altitude)
        self.quality      = float(stats.quality)


        #self.speed_avg = 0.0

    def ParseGPX(self):
        "Open the GPX file, parse it, and return the GPX data (points)"
        gpx = GPXItem()
        try:
            gpx.Load(self.fname)
            gpx.MergeAll()
        except Exception, e:
            print "Error parsing file: %s: %s" % (self.fname, e)
            sys.exit(0)

        return gpx

    def LoadGPXData(self, gpx):
        "Open the GPX file, and load the info from it"
        self.fname = gpx.gpx_fname

        # read the input from HERE (just data)
        # 21/10/2016 - For perfomance reasons, don't store the gpx inside the db
        # gpx_f = open(self.fname, 'r')
        # self.gpx = gpx_f.read()
        # gpx_f.close()
        self.gpx = ''
        # create the KML on the fly, here
        # self.kml = kml.GPX2KMLString( gpx.gpx_fname, gpx, optimize=False)
        # generated on the fly.
        self.kml = ''


        self.start_stamp = 0
        if gpx.gpx and gpx.gpx.tracks and gpx.gpx.tracks[0].segments and gpx.gpx.tracks[0].segments[0] and gpx.gpx.tracks[0].segments[0].points and gpx.gpx.tracks[0].segments[0].points[0].time:

            self.start_stamp = time.mktime(gpx.gpx.tracks[0].segments[0].points[0].time.timetuple())  # UTC time, store in seconds.
            self.time_moving = gpx.gpx.tracks[0].get_moving_data().moving_time  # seconds

            #self.duration = gpx.gpx.tracks[0].get_duration()  # seconds
            #self.distance = gpx.gpx.tracks[0].length_2d()  # meters
            #self.elevation = gpx.gpx.tracks[0].get_uphill_downhill().uphill  # meters
            #self.speed_avg = gpx.gpx.tracks[0].get_average_speed()[0] * 3.6  # km/h
        else:
            print "Warning: %s has no GPX point info (maybe waypoints?)" % self.fname

        # fix some values
        if self.duration == None:
            print "Warning, track '%s' has invalid duration (teoric?)" % self.fname
            self.duration = 0.0


    def ParseFileName(self, str=None):

        stamp = None
        tags = None
        places = None
        extension = None

        # regstr = re.match("(\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2})?\s*(-+)?\s*(\[.+\])?\s*(.+)\.(.+)", str or self.fname, re.I)

        regstr = re.match("(\d{4}-\d{2}-\d{2}-\w{2}-\w{2}-\w{2}|\d{10}|\d{8})?\s*(-+)?\s*(\[.+\])*\s*(.+)\.(.+)", str or os.path.basename(self.fname), re.I)

        if regstr:

            if regstr.group(1):
                stamp = regstr.group(1)
                if len(stamp) == 8 or len(stamp) == 10:
                    # YYYYMMDD or YYMMDD0X
                    # print "S", stamp
                    # stamp = "%s-%s-%s-00-00-00" % (stamp[0:4], stamp[4:6], stamp[6:8])
                    # print stamp
                    # sys.exit(0)
                    gpx = GPXItem()
                    try:
                        gpx.Load(self.fname)
                        gpx.MergeAll()
                    except Exception, e:
                        print "Exception: parsing GPX data: %s" % self.fname

                    self.LoadGPXData(gpx)
                    # stamp = time.strftime("%Y-%m-%d-%H-%M-%S",time.localtime(self.UTC2Local(self.start_stamp)))
                else:
                    # its a full featured date & time, so parse it.
                    # seconds from the epoch, you know.
                    stamp = stamp.upper().replace('X', '0')  # to manage UNKNOWN dates (from creation)
                    stamp = time.mktime(datetime.strptime(stamp, "%Y-%m-%d-%H-%M-%S").timetuple())

            if regstr.group(3):
                tags = regstr.group(3)
                tags = re.sub('\]\s*\[', ',', tags)
                tags = re.sub('[\[\]]', '', tags)
                tags = tags.split(',')
                tags = filter(lambda x: x.strip(), tags)

            if regstr.group(4):

                places = regstr.group(4)
                places = re.split("\s*[-_]+\s*", places)
                places = filter(lambda x: x.strip(), places)

            if regstr.group(5):
                extension = regstr.group(5).lower()

        return stamp, tags, places, extension

    def GetTags(self):
        r = []
        if self.kind: r.append(self.kind)
        if self.device: r.append(self.device)
        if self.equipment: r.append(self.equipment)
        return r
        # return map(lambda x: str(x), [ self.kind, self.device, self.equipment ])

    def SetTags(self, tags):

        if len(tags) == 3:
            self.kind, self.device, self.equipment = tags
        if len(tags) == 2:
            self.kind, self.device = tags
        if len(tags) == 1:
            self.kind = tags[0]

    def StampAsString(self):
        return time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime(self.start_stamp))

    def IsGPX(self):
        if self.fextension.lower() != "gpx":
            return False
        return True

    def IsFIT(self):
        if self.fextension.lower() == "fit":
            return True
        return False


    def UTC2Local(self, t):
        local_timezone = tzlocal.get_localzone()  # get pytz tzinfo
        utc_time = datetime.fromtimestamp(t)
        local_time = utc_time.replace(tzinfo=pytz.utc).astimezone(local_timezone)
        return time.mktime(local_time.timetuple())

    def Print(self):
        s = ""
        for i in self.__dict__.keys():
            if i not in ["gpx", 'kml']:

                if i == "start_stamp":
                    # s += "%s:\t%s\n" % (i, time.strftime("%Y/%m/%d %H:%M:%S",time.localtime(self.UTC2Local(self.start_stamp))))
                    s += "%s:\t%s\n" % (i, time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(self.start_stamp)))
                    continue
                if i in ["time_moving", "duration"]:
                    s += "%s:\t%s\n" % (i, time.strftime("%H:%M:%S", time.gmtime(self.__dict__[i])))
                    continue

                s += "%s:\t%s\n" % (i, self.__dict__[i])

        return s

    def ToReadable(self):
        """format the fields to be human readable. THis DESTROY de object"""


        def time_str(seconds):
            m, s = divmod(seconds, 60)
            h, m = divmod(m, 60)
            return "%02d:%02d:%02d" % (h, m, s)

        # self.start_stamp = time.strftime("%Y/%m/%d %H:%M:%S",time.localtime(self.UTC2Local(self.start_stamp)))
        self.start_stamp = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(self.start_stamp))
        # self.time_moving = time.strftime("%H:%M:%S",time.gmtime(self.time_moving))
        # self.duration = time.strftime("%H:%M:%S",time.gmtime(self.duration))
        self.time_moving = time_str(self.time_moving)
        self.duration = time_str(self.duration)


        self.distance = "%3.2f" % (self.distance / 1000.0)  # in KM)
        self.elevation = "%3.2f" % self.elevation

        # self.fname, _ = os.path.splitext(os.path.basename(self.fname))
        # self.fname = self.fname[self.fname.index(']')+1:].strip()
        # places??
        # support circular state.

        self.uphill_avg_slope = "%3.2f" % self.uphill_avg_slope
        self.level_avg_slope = "%3.2f" % self.level_avg_slope
        self.downhill_avg_slope = "%3.2f" % self.downhill_avg_slope

        self.uphill_distance = "%3.2f Km" % (self.uphill_distance / 1000.0)
        self.level_distance = "%3.2f Km" % (self.level_distance / 1000.0)
        self.downhill_distance = "%3.2f Km" % (self.downhill_distance / 1000.0)

        self.uphill_p_distance = "%3.2f" % self.uphill_p_distance
        self.level_p_distance = "%3.2f" % self.level_p_distance
        self.downhill_p_distance = "%3.2f" % self.downhill_p_distance

        self.uphill_elevation = "%3.2f m" % self.uphill_elevation
        self.level_elevation = "%3.2f m" % self.level_elevation
        self.downhill_elevation = "%3.2f m" % self.downhill_elevation
        self.quality = "%3.2f %%" % self.quality

        #speeds

        def km_tomin(v):
            # from
            # https://joan16v.wordpress.com/2011/09/28/como-pasar-de-velocidad-en-kmh-a-minkm-ritmo/

            if v == 0:
                return "0:00"

            v = (3600.0 / v) / 60.0
            a = int(v)
            b = v - a
            #return a + b * 60.0
            return "%d:%02d" % (a, int(b*60))

        if self.kind == 'RUN':
            self.speed_avg = "%s min/Km" % km_tomin( self.speed_avg * 3.6 )
            self.uphill_speed = "%s min/Km" % km_tomin(self.uphill_speed*3.6)
            self.level_speed = "%s min/Km" % km_tomin(self.level_speed*3.6)
            self.downhill_speed = "%s min/Km" % km_tomin(self.downhill_speed*3.6)
        else:
            self.speed_avg = "%3.2f Km/h" % (self.speed_avg *3.6)
            self.uphill_speed = "%3.2f Km/h" % (self.uphill_speed * 3.6)
            self.level_speed = "%3.2f Km/h" % (self.level_speed * 3.6)
            self.downhill_speed = "%3.2f Km/h" % (self.downhill_speed * 3.6)



        self.uphill_time = datetime.utcfromtimestamp(self.uphill_time).strftime("%H:%M:%S")
        self.level_time = datetime.utcfromtimestamp(self.level_time).strftime("%H:%M:%S")
        self.downhill_time = datetime.utcfromtimestamp(self.downhill_time).strftime("%H:%M:%S")

        self.uphill_p_time = "%3.2f" % self.uphill_p_time
        self.level_p_time = "%3.2f" % self.level_p_time
        self.downhill_p_time = "%3.2f" % self.downhill_p_time

        self.score = "%3.2f" % self.score

        self.circularchecked = ""
        if self.circular == 1:
            self.circularchecked = "checked"



        #0   -> not clockwise (default, stats)
        #1   -> clockwise (default, stats)
        #2   -> not clockwise (WEB)
        #3   -> clockwise (WEB)
        self.clockwisechecked = ""
        if self.clockwise == 1 or self.clockwise == 3:
            self.clockwisechecked = "checked"
        return self


    def Filter(self, l):
        #
        # filter and convert everything
        #


        xlate = {}
        xlate['ROA_R'] = 'ROAD'
        xlate['MTB_R'] = 'MTB'
        xlate['ROA'] = 'ROAD'
        xlate['TRK_R'] = 'TREKKING'
        xlate['TRK'] = 'TREKKING'

        t = []
        for i in l:
            if i.upper() in xlate:
                t.append(xlate[i])
            else:
                t.append(i.upper())

        return t

    def CalculateName(self):

        """
        FILE FORMAT
            YYYY-MM-DD-HH-mm-SS --- [Kind,Device,Equipment] Place1-Place2-Place3-Place4.gpx
            2016-10-12-18-33-11 --- [MTB,EDGE1000,SANTACRUZ] Navas-Almenara-Robledo-San Antonio-Fresnedillas-Navalagamella-Colmenar-NASA-Navas.gpx
        """

        # parse name, and get some data about it
        stamp, tags, places, fextension = self.ParseFileName(os.path.basename(self.fname))
        # print "Stamp:  ", stamp
        # print "tags:   ", tags
        # print "places: ", places
        # print "ext:    ", fextension



        # build name from stored data

        if self.start_stamp > 0:
            # datef = time.strftime("%Y-%m-%d-%H-%M-%S",time.localtime(self.UTC2Local(self.start_stamp)))
            datef = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime(self.start_stamp))
        else:
            # watch OLD Format
            if stamp == None and self.IsGPX():
                # read the GPX file, and process the input :/
                gpx = GPXItem()
                gpx.Load(self.fname)
                gpx.MergeAll()
                self.LoadGPXData(gpx)
                datef = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime(self.UTC2Local(self.start_stamp)))
            else:
                datef = stamp

        if not tags:
            tags = []
            if self.kind: tags.append(self.kind.upper())
            if self.device: tags.append(self.device.upper())
            if self.equipment: tags.append(self.equipment.upper())




        # map extensions if we need to remap it.

        # old RCX5-RC3 files (From PolarProTrainer download)
        if fextension == "xml": self.fextension = "gpx"
        if fextension == "gpxx": self.fextension = "gpx"

        return self.GenerateFileName()


    def GenerateFileName(self):

        fformat = "%s - %s %s.%s"
        tagsformat = "[%s]"
        # s = fformat % (datef, ",".join(tags), " - ".join(places), fextension )

        # print self.StampAsString(), self.GetTags()

        self.SetTags(self.Filter(self.GetTags()))

        tags = self.GetTags()
        TAGS = ""
        if len(tags) == 3:
            TAGS = ",".join(self.GetTags())

        if len(tags) == 1:
            TAGS = tags[0]  # just only exists (KIND,DEVICE,EQUIPMENT)

        TAGS = tagsformat % TAGS
        if TAGS == '[]':
            TAGS = ''

        tgtname = fformat % (self.StampAsString(), TAGS, " - ".join(self.places), self.fextension)
        self.fname = os.path.sep.join([os.path.dirname(self.fname), tgtname])

        return self.fname


class Place(BaseDB):
    def __init__(self, name=""):
        BaseDB.__init__(self)
        self.id = None
        self.name = name
        self.latitude = 0.0
        self.longitude = 0.0
        self.elevation = 0.0
        self.description = None

    @staticmethod
    def sql_create_script():
        s = """
            CREATE TABLE PLACES (
                ID           INTEGER PRIMARY KEY AUTOINCREMENT,
                NAME         TEXT DEFAULT "",
                LATITUDE     REAL DEFAULT 0.0,
                LONGITUDE    REAL DEFAULT 0.0,
                ELEVATION    REAL DEFAULT 0.0,
                DESCRIPTION  TEXT DEFAULT NULL
            );
        """
        return s

    def sql_insert_script(self):


        s = "insert into PLACES values(NULL,'%s','%f','%f','%f','%s')" % (self.name.lower(),
                                                                      self.latitude,
                                                                      self.longitude,
                                                                      self.elevation,
                                                                      self.description
                                                                     )
        return s

    def sql_select_id_from_name(self):
        s = "select p.id,p.name,p.latitude,p.longitude,p.elevation,p.description from PLACES p where name = '%s'" % self.name.lower()
        return s

    def sql_load_script(self):
        s = "select * from PLACES where id=%d" % int(self.id)
        return s

    def load(self, conn):
        s = self.sql_load_script()

        cursor = conn.cursor()
        cursor.execute(s)
        data = cursor.fetchone()

        if not data:
            return False

        self.name = data[1]
        self.latitude = data[2]
        self.longitude = data[3]
        self.elevation = data[4]
        self.description = data[5]

        return True

    def ToReadable(self):
        """format the fields to be human readable. THis DESTROY de object"""
        self.name = self.name.capitalize()
        return self

    def ExistsInDB(self, conn):
        q = self.sql_select_id_from_name()

        cursor = conn.cursor()
        cursor.execute(q)
        data = cursor.fetchone()

        if not data:
            return False

        self.id = data[0]
        self.name = data[1]
        self.latitude = data[2]
        self.longitude = data[3]
        self.elevation = data[4]
        self.description = data[5]
        return True


class TrackInPlaces(BaseDB):

    @staticmethod
    def sql_create_script():
        s = """
            CREATE TABLE TRACK_IN_PLACES (
                ID_TRACK    INTEGER,
                ID_PLACE    INTEGER,
                FOREIGN KEY(ID_TRACK) REFERENCES TRACKS(ID),
                FOREIGN KEY(ID_PLACE) REFERENCES PLACES(ID)
            );

        """
        return s

    def sql_insert_script(self):
        s = "insert into TRACK_IN_PLACES values(%d,%d)" % (self.id_track, self.id_place)
        return s

    def sql_exists_on_db(self):
        s = "select id_track, id_place from TRACK_IN_PLACES where id_track=%d and id_place=%d" % (self.id_track, self.id_place)
        return s

    def __init__(self, id_track, id_place):
        self.id_track = id_track
        self.id_place = id_place

    def ExistsInDB(self, conn):
        q = self.sql_exists_on_db()

        cursor = conn.cursor()
        cursor.execute(q)
        data = cursor.fetchone()

        if not data:
            return False
        return True

class TracksDeleted(BaseDB):

    @staticmethod
    def sql_create_script():
        s = """
            CREATE TABLE TRACKS_DELETED (
                ID          INTEGER PRIMARY KEY AUTOINCREMENT,
                FNAME       TEXT DEFAULT ""
            );

        """
        return s

    def sql_insert_script(self):
        s = "insert into TRACKS_DELETED values(NULL,'%s')" % (self.fname)
        return s

    def sql_exists_on_db(self):
        s = "select id from TRACKS_DELETED where fname='%s'" % (self.fname)
        return s

    def __init__(self, fname):
        self.fname = fname

    def ExistsInDB(self, conn):
        q = self.sql_exists_on_db()

        cursor = conn.cursor()
        cursor.execute(q)
        data = cursor.fetchone()

        if not data:
            return False
        return True

class DBManager:
    def __init__(self):
        self.conn = None
        self.verbose = 0
        self.slope_distance_gap = 10

    def Close(self):
        self.conn.close()

    def CloseAndCommit(self):
        self.conn.commit()
        self.conn.close()

    def Connect(self, dbfile):
        self.dbfile = dbfile
        self.conn = sqlite3.connect(self.dbfile)
        # to handle unicode.
        # self.conn.text_factory = str



    def CreateDB(self, dbfile):

        create_script = [ Track.sql_create_script(), Place.sql_create_script(), TrackInPlaces.sql_create_script(), TracksDeleted.sql_create_script() ]

        if os.path.exists(dbfile):
            os.remove(dbfile)

        self.Connect(dbfile)
        for script in create_script:
            print "Creating DB:Tables: ", script
            self.conn.execute(script)

        self.CloseAndCommit()

    def InsertWayPointGPXIntoDB(self, gpxfile, description=None, opts=None):
        try:
            gpxfile_xlated = gpxfile.decode('utf-8')
            # this works. don't do anything more.
        except (UnicodeEncodeError, UnicodeDecodeError):
            try:
                gpxfile_xlated = gpxfile.decode('cp1252')
                print "\tWarning: CP1252-Encoded Name. Please change name to UTF-8. Bailing out (%s)" % gpxfile
                return False
            except (UnicodeEncodeError, UnicodeDecodeError):
                pass

        gpx = GPXItem()
        gpx.Load(gpxfile)
        gpx.MergeAll()

        for wp in gpx.gpx.waypoints:

            if wp.description == None:
                wp.description = ""


            p = Place(name=wp.name.encode('utf-8'))
            p.latitude = wp.latitude
            p.longitude = wp.longitude
            p.description = wp.description.encode('utf-8')
            p.elevation = wp.elevation
            if not p.elevation:
                p.elevation = 0.0

            if not p.ExistsInDB(self.conn):
                p.insert(self.conn)
                print "WPT->Place Inserted: name:%s lat:%3.2f lon:%3.2f elev:%3.2f" % (p.name, p.latitude, p.longitude, p.elevation)
                self.conn.commit()

        return True



    def InsertGPXIntoDB(self, gpxfile, description=None, opts=None):


        try:
            gpxfile_xlated = gpxfile.decode('utf-8')
            # this works. don't do anything more.
        except (UnicodeEncodeError, UnicodeDecodeError):
            try:
                gpxfile_xlated = gpxfile.decode('cp1252')
                print "\tWarning: CP1252-Encoded Name. Please change name to UTF-8. Bailing out (%s)" % gpxfile
                return False
            except (UnicodeEncodeError, UnicodeDecodeError):
                pass


        # skip duplicate entries
        track = Track(None, None, None)
        track.fname = gpxfile

        if track.ExistsInDB(self.conn):
            # based on fname, of course
            print "\tSkipping '%s': Duplicate entry." % track.fname
            return False
        dtrack = TracksDeleted(track.fname)
        if dtrack.ExistsInDB(self.conn):
            # based on fname, of course
            print "\tSkipping '%s': Deleted entry." % track.fname
            return False


        # else, do the work.

        gpx = GPXItem()
        gpx.Load(gpxfile)
        gpx.MergeAll()

        if self.verbose >= 2:
            print gpx.Print()

        track = Track(None, None, None, description, gpx=gpx)

        if self.verbose >= 1:
            print track.Print()

        # calculate bounds, but filter lat=0 || lon=0 points

        gpx.gpx.tracks[0].segments[0].points = filter(lambda x: x.latitude != 0.0 and x.longitude != 0.0, gpx.gpx.tracks[0].segments[0].points)

        stats = gpxstats.CalculateStats(gpx.gpx.tracks[0].segments[0].points , distance=self.slope_distance_gap, hint=track.kind)
        track.SetStats(stats)

        print ""
        print "[*File: %s]" % track.fname

        stats.PrintStats()

        optmizer = GPXOptimizer()
        opt_points = optmizer.Optimize(gpx.gpx.tracks[0].segments[0].points)
        optmizer.Print_stats()
        track.numpoints = len(opt_points)

        bounds = gpx.Bounds()

        track.SW_lat = bounds.min_latitude or 0.0
        track.SW_lon = bounds.min_longitude or 0.0
        track.NE_lat = bounds.max_latitude or 0.0
        track.NE_lon = bounds.max_longitude or 0.0

        # track.numpoints in updated when KML is created (optimizer length)
        # insert data into TABLES.




        places_list = []
        # remove DUPLICATES, e.g. navas - m501 - NASA - navas / navas - m501 - NASA
        for place in list(set(track.places)):

            p = Place(name=place)
            if not p.ExistsInDB(self.conn):
                # if found, p is loaded with the data
                p.insert(self.conn)
            places_list.append(p)  # for the IDS.

        # by default, use only the places to generate a title for the Track
        # later can be changed.
        track.title, _ = os.path.splitext(os.path.basename(track.fname))
        track.title = track.title[track.title.index(']') + 1:].strip()

        # to mark new adds
        track.title = "* " + track.title
        # windows ugly issue with the file paths.
        track.fname = track.fname.replace("\\", "/")
        track.fname = track.fname.replace("//", "/")

        # for f in track.__dict__.keys():
        #    print "%s->%s" % (f, track.__dict__[f])

        track.insert(self.conn) ## get the id

        # 07/06/2017 - Old version: uses the names in the Track Name to generate the Title.
        # New version: Explores the track, and check the DB to see what are the nearest
        # places and add it to the title. Problem: if no place in DB, we lose the info
        # in the track title. So better mantain the name, and change the Places. So the
        # user can manage it, or generate the title.
        # compute the new track in places based on AutoCheck.

        places_list_new = dbmanager.GetPlacesByLocation(track.id, opts.distance_to_place,gpx_points=opt_points)

        if len(places_list_new) > 0:
            places_list = places_list_new


        for place in places_list:
            track_in_places = TrackInPlaces(track.id, place.id)
            track_in_places.insert(self.conn)

        places = map(lambda x: x.name.capitalize(), places_list)

        # rewrite the title.

        track.title = "* " + " - ".join(places)
        self.SaveTrackTitle(track.id, track.title)

        # commit it, so we can use the DB in the handlers.

        self.conn.commit()

        # being creative, create previews and so on XD

        lopts = wwwhandlers.mockhandler.D()
        lopts.dbfile = self.dbfile
        lopts.nocache = True
        lopts.slope_distance_gap = self.slope_distance_gap
        lopts.cachedir = opts.cachedir


        mockh = wwwhandlers.mockhandler.HandlerAdapter(lopts)

        preview_h = wwwhandlers.converters.TRACKPREVIEW_Handler()
        kml_h = wwwhandlers.converters.TRACK2KML_Handler()
        alt_h = wwwhandlers.converters.ElevationPNG_Handler()
        # use the same configuration that in the pagination_tracks.js

        args = { 'id': track.id, 'sz': "200x100" }
        print "Creating PNG preview for track.id=%d, %sz" % (args['id'], args['sz'])
        mockh.Invoke(preview_h, args)

        args = { 'id': track.id, 'sz': "600x600" }
        print "Creating PNG preview for track.id=%d, %sz" % (args['id'], args['sz'])
        mockh.Invoke(preview_h, args)

        print "Creating KML preview for track.id=%d" % (args['id'])
        mockh.Invoke(kml_h, args)

        args['sz'] = "202x100"
        print "Creating PNG Altitude for track.id=%d, %sz" % (args['id'], args['sz'])
        mockh.Invoke(alt_h, args)

        return True


    def FixDeletedIntoDB(self, gpxfile, description=None):


        try:
            gpxfile_xlated = gpxfile.decode('utf-8')
            # this works. don't do anything more.
        except (UnicodeEncodeError, UnicodeDecodeError):
            try:
                gpxfile_xlated = gpxfile.decode('cp1252')
                print "\tWarning: CP1252-Encoded Name. Please change name to UTF-8. Bailing out (%s)" % gpxfile
                return False
            except (UnicodeEncodeError, UnicodeDecodeError):
                pass


        # skip duplicate entries
        track = Track(None, None, None)
        track.fname = gpxfile

        if track.ExistsInDB(self.conn):
            # based on fname, of course
            print "\tSkipping '%s': Duplicate entry." % track.fname
            return False
        dtrack = TracksDeleted(track.fname)
        if dtrack.ExistsInDB(self.conn):
            # based on fname, of course
            print "\tSkipping '%s': Deleted entry." % track.fname
            return False

        # else, do the work.

        gpx = GPXItem()
        gpx.Load(gpxfile)
        gpx.MergeAll()

        if self.verbose >= 2:
            print gpx.Print()

        track = Track(None, None, None, description, gpx=gpx)

        if self.verbose >= 1:
            print track.Print()

        # calculate bounds, but filter lat=0 || lon=0 points

        gpx.gpx.tracks[0].segments[0].points = filter(lambda x: x.latitude != 0.0 and x.longitude != 0.0, gpx.gpx.tracks[0].segments[0].points)

        stats = gpxstats.CalculateStats(gpx.gpx.tracks[0].segments[0].points , distance=self.slope_distance_gap, hint=track.kind)

        track.SetStats(stats)

        print ""
        print "[*%d Title: %s]" % (track.id, track.title)
        print "[*File: %s]" % track.fname
        stats.PrintStats()

        # windows ugly issue with the file paths.
        track.fname = track.fname.replace("\\", "/")
        track.fname = track.fname.replace("//", "/")

        if track.kind == "RODILLO" or track.kind.ends_with("_T") or tracks.score == 0 or tracks.duration == 0:
            # its a "Rodillo or theoric track. Preload to the table"
            # print "[I] Track '%s' is selected to Tracks_Deleted. Inserting" % track.fname
            track_d = TracksDeleted(track.fname)
            q = track_d.sql_insert_script()
            self.conn.execute(q)
            self.conn.commit()
            return True

        return False

    def LoadTrackFromDB(self, trackid):

        track = Track(None, None, None)
        track.id = trackid
        track.load(self.conn)
        return track

    def LoadAllTracks(self, limit=-1, cloned=0):

        # q = "select id,fname from TRACKS  order by start_stamp desc limit %d" % limit
        if cloned:
            q = "select id,fname from TRACKS order by start_stamp desc limit %d" % (limit)
        else:
            q = "select id,fname from TRACKS where cloned=0 order by start_stamp desc limit %d" % (limit)


        t = []
        for row in self.conn.execute(q):
            d = D()
            d.id = row[0]
            d.fname = row[1]
            t.append(d)
        return t

    def LoadAllPlaces(self, limit=-1, bounds=None):

        b = ""
        if bounds:
            b = "and p.longitude >= {w_lon} and p.longitude <= {e_lon} and p.latitude <= {n_lat} and p.latitude >= {s_lat}"
            b = b.format(w_lon=bounds['SW']['lon'],
                          e_lon=bounds['NE']['lon'],
                          n_lat=bounds['NE']['lat'],
                          s_lat=bounds['SW']['lat'])

        q = "select p.id, p.name, count(*) as ntracks, p.longitude, p.latitude, p.elevation, p.description from track_in_places tp, places p where p.id = tp.id_place %s group by tp.id_place order by ntracks desc limit %d" % (b, limit)
        t = []

        for row in self.conn.execute(q):
            d = D()
            d.id = row[0]
            d.name = row[1]
            d.ntracks = row[2]
            d.longitude = row[3]
            d.latitude = row[4]
            d.elevation = row[5]
            d.description = row[6]

            t.append(d)


        # load also orphan places (new places)
        q = "select p.id, p.name,  0 as ntracks, p.longitude, p.latitude, p.elevation, p.description from places p where p.id not in (select id_place from track_in_places) %s order by name asc limit %d" % (b, limit)

        for row in self.conn.execute(q):
            d = D()
            d.id = row[0]
            d.name = row[1]
            d.ntracks = row[2]
            d.longitude = row[3]
            d.latitude = row[4]
            d.elevation = row[5]
            d.description = row[6]
            t.append(d)

        return t

    def LoadPlacesByBounds(self, limit=-1, bounds=None):

        b = ""
        if bounds:
            b = "p.longitude >= {w_lon} and p.longitude <= {e_lon} and p.latitude <= {n_lat} and p.latitude >= {s_lat}"
            b = b.format(w_lon=bounds['SW']['lon'],
                          e_lon=bounds['NE']['lon'],
                          n_lat=bounds['NE']['lat'],
                          s_lat=bounds['SW']['lat'])

        q = "select p.id, p.name, p.longitude, p.latitude, p.elevation, p.description from places p where %s limit %d" % (b,limit)
        t = []

        for row in self.conn.execute(q):
            d = D()
            d.id = row[0]
            d.name = row[1]
            d.longitude = row[2]
            d.latitude = row[3]
            d.elevation = row[4]
            d.description = row[5]

            t.append(d)

        return t


    def LoadFavorites(self, limit=-1):

        q = "select id,fname from TRACKS  where rating > 0  order by rating desc, start_stamp desc limit %d" % limit

        t = []
        for row in self.conn.execute(q):
            d = D()
            d.id = row[0]
            d.fname = row[1]
            t.append(d)
        return t

    def Search(self, query, limit=-1):

        # megafix

        qp = qparser.QueryParser(self.conn)
        resultq = qp.Parse(query)

        # i = "%" +query + "%"
        # q = "select id,fname from TRACKS where fname like '%s' or kind like '%s' order by start_stamp desc limit %d" % (i,i,limit)
        q = resultq['query']
        if resultq['query'].lower().find("limit") == -1:
            q = "%s limit %d" % (resultq['query'], limit)

        ##print "query [%s]" % q
        t = []
        try:
            for row in self.conn.execute(q):
                d = D()
                d.id = row[0]
                # d.fname = row[1]
                # d.fname = "-"
                t.append(d)
        except:
            pass

        return { 'type': resultq['type'], 'ids': t }

    def SearchByPlace(self, placeid, limit=-1):

        q = "select t.id, t.fname from track_in_places tp, places p, tracks t where tp.id_place = p.id and p.id = %d and tp.id_track = t.id order by start_stamp desc limit %d" % (placeid, limit)
        t = []
        for row in self.conn.execute(q):
            d = D()
            d.id = row[0]
            d.fname = row[1]
            t.append(d)
        return t

    def SearchSimilarTrack(self, trackid, limit=-1, distance_delta=1500, elevation_delta=100, latitude_delta=0.001, longitude_delta=0.01, numpoints_delta=100):  # 0.0008, 0.008 0.005, 0.01

        #latitude_delta=0.008, longitude_delta=0.017
        q = "select id, distance, elevation,SW_LAT,SW_LON,NE_LAT,NE_LON, kind, numpoints, CENTER_LAT, CENTER_LON, clockwise from tracks where id=%d" % trackid
        for row in self.conn.execute(q):
            t = D()
            t.id = row[0]
            t.distance = float(row[1])
            t.elevation = float(row[2])
            t.SW_LAT = float(row[3])
            t.SW_LON = float(row[4])
            t.NE_LAT = float(row[5])
            t.NE_LON = float(row[6])
            t.kind = row[7]
            t.numpoints = int(row[8])
            t.CENTER_LAT = float(row[9])
            t.CENTER_LON = float(row[10])
            t.clockwise = int(row[11])

        # http://diferenciaentre.info/wp-content/uploads/2015/08/longitud.png
        # LATITUDE (Y) from  SOUTH POLE TO NORTHPOLE,  INCREASES.
        # LONGITUDE (X)  FROM 0 MERIDIAN (GMT) TO RIGHT (ITALY) INCREASES.
        # lat="40.327187217772007" lon="-3.760281018912792">
        #        LATITUDE                                 LONGITUDE
        #
        #       NORTH POLE +90                                    <- 180 (behind greenwitch)
        #  ^                                                   |
        #  | increases                                         |
        #     -----equator-----0                    center (north pole top)
        #                                                      |
        #                                                      |
        #        SOUTH POLE -90   <- DECREASES       Greenwitch Meridian (0) -> INCREASES
        #

        # deprecate elevation check, because all the tracks with the RCX5 are bad.

        q = """
            select id, fname from tracks where
                -- (numpoints <= {numpoints_high} and numpoints >= {numpoints_low}) AND
                (distance  <= {distance_high}  and distance >=  {distance_low}) AND
                -- (elevation <= {elevation_high} and elevation >= {elevation_low}) AND
                (SW_LON >= {sw_lon} and NE_LON <= {ne_lon} AND SW_LAT >= {sw_lat} and NE_LAT <= {ne_lat}) AND
                id != {trackid} AND
                kind = '{kind}'
                 limit {limit}
            """
        # lat_delta = 0.002
        # lon_delta = 0.005

        # NW = geo.Location(bounds.max_latitude+lat_delta, bounds.min_longitude-lon_delta)
        # SE = geo.Location(bounds.min_latitude-lat_delta, bounds.max_longitude+lon_delta)

        # SW = geo.Location(bounds.min_latitude-lat_delta, bounds.min_longitude-lon_delta)
        # NE = geo.Location(bounds.max_latitude+lat_delta, bounds.max_longitude+lon_delta)

        # based on center and boxed.

        q = """
            select id, fname from tracks where
                -- (elevation <= {elevation_high} and elevation >= {elevation_low}) AND
                   (distance  <= {distance_high}  and distance >=  {distance_low}) AND
                    CENTER_LON >= {sw_center_lon} and CENTER_LON <= {ne_center_lon} AND
                    CENTER_LAT >= {sw_center_lat} and CENTER_LAT <= {ne_center_lat} AND
                id != {trackid} AND clockwise={clockwise} AND
                kind = '{kind}'
                 limit {limit}
            """

        q = q.format(numpoints_high=t.numpoints + numpoints_delta, numpoints_low=t.numpoints - numpoints_delta,
                     distance_high=t.distance + distance_delta, distance_low=t.distance - distance_delta,
                     elevation_high=t.elevation + elevation_delta, elevation_low=t.elevation - elevation_delta,

                     sw_center_lon=t.CENTER_LON - longitude_delta,
                     ne_center_lon=t.CENTER_LON + longitude_delta,
                     sw_center_lat=t.CENTER_LAT - latitude_delta,
                     ne_center_lat=t.CENTER_LAT + latitude_delta,

                     clockwise=t.clockwise,

                     trackid=t.id, kind=t.kind, limit=limit)
        

        # use the center method, with a little box

        t = []
        c = 0
        for row in self.conn.execute(q):
            d = D()
            d.id = row[0]
            d.fname = row[1]
            t.append(d)
            c+=1
        
        #analize similar
        #print "%d, %s" % (c, q)
        return t


    #

    def LoadPlacesFromTrack(self, trackid, limit=-1):
        "return the current Places for a track, and the available ones. Build a JSON object to do the trick."

        # q = "select tp.id_place, p.name from track_in_places tp, places p where tp.id_track=%d and tp.id_place = p.id order by p.name limit %d" % (trackid, limit)
        # no order to reflect the insertion
        q = "select tp.id_place, p.name, p.latitude, p.longitude, p.elevation from track_in_places tp, places p where tp.id_track=%d and tp.id_place = p.id limit %d" % (trackid, limit)
        pin = []
        pout = []
        for row in self.conn.execute(q):
            lat = float(row[2])
            lon = float(row[3])
            ele = float(row[4])

            hascoords = 0
            if lat != 0.0 and lon != 0.0:
                hascoords = 1
                if ele != 0.0:
                    hascoords = 2

            d = { 'id': row[0], 'name': row[1], 'hascoords': hascoords }
            pin.append(d)


        q = "select id,name from places where id not in (select id_place from track_in_places where id_track=%d) order by name limit %d" % (trackid, limit)

        # q = "select tp.id_place, p.name from track_in_places tp, places p where tp.id_place not in " +\
        #    "(select tp.id_place from track_in_places tp where tp.id_track = %d) and p.id = tp.id_place order by id_place limit %d" % (trackid, limit)

        for row in self.conn.execute(q):
            d = { 'id': row[0], 'name': row[1] }
            pout.append(d)

        # add orphans in the pout container.

        q = "select p.id, p.name from places p LEFT JOIN track_in_places tp on p.id = tp.id_place WHERE tp.id_place IS NULL limit %d" % limit

        for row in self.conn.execute(q):
            d = { 'id': row[0], 'name': row[1] }
            pout.append(d)


        t = { 'id': trackid, 'in': pin, 'out': pout}
        return t

    #def UpdateTrackNumPoints(self, trackid, numpoints):
    #    q = "update TRACKS set numpoints=%d where id=%d" % (numpoints, trackid)
    #    self.conn.execute(q)
    #    d = D()
    #    d.id = trackid
    #    d.numpoints = numpoints
    #    return d

    def SaveTrackPlace(self, trackid, placeid):
        track_in_places = TrackInPlaces(trackid, placeid)

        if not track_in_places.ExistsInDB(self.conn):
            track_in_places.insert(self.conn)
        d = D()
        d.tid = trackid
        d.pid = placeid
        return d


    def SaveTrackTitle(self, trackid, title):
        q = "update TRACKS set title='%s' where id=%d" % (title, trackid)
        self.conn.execute(q)
        d = D()
        d.id = trackid
        d.title = title

        return d

    def SaveTrackDescription(self, trackid, description):
        q = "update TRACKS set description='%s' where id=%d" % (description, trackid)
        self.conn.execute(q)
        d = D()
        d.id = trackid
        d.description = description

        return d

    def SaveTrackCircular(self, trackid, circular):
        q = "update TRACKS set circular=%d where id=%d" % (int(circular), trackid)
        self.conn.execute(q)
        d = D()
        d.id = trackid
        d.circular = circular

        return d

    def SaveTrackClockWise(self, trackid, clockwise, opts):

        #0   -> not clockwise (default, stats)
        #1   -> clockwise (default, stats)
        #2   -> not clockwise (WEB)
        #3   -> clockwise (WEB)

        cw = int(clockwise)
        if cw == 0: cw = 2
        if cw == 1: cw = 3

        q = "update TRACKS set clockwise=%d where id=%d" % (int(cw), trackid)

        self.conn.execute(q)
        d = D()
        d.id = trackid
        d.clockwise = cw
        self.conn.commit()
        self.RegenerateCache(opts, "%s" % trackid, fullmode=False)

        return d

    def SaveTrackRating(self, trackid, rating):
        q = "update TRACKS set rating=%d where id=%d" % (rating, trackid)
        self.conn.execute(q)
        d = D()
        d.id = trackid
        d.rating = rating

        return d

    def SavePlaceName(self, placeid, name):
        q = "update PLACES set name='%s' where id=%d" % (name, placeid)
        self.conn.execute(q)
        d = D()
        d.id = placeid
        d.name = name

        return d

    def CreatePlace(self, name, lat=0.0, lon=0.0):

        place = Place()
        place.name = name;
        place.latitude = lat;
        place.longitude = lon;

        if place.ExistsInDB(self.conn):
            return { 'id': place.id }

        cursor = self.conn.cursor()
        cursor.execute(place.sql_insert_script());
        place.id = cursor.lastrowid
        return { 'id': place.id }


    def DeleteTrack(self, trackid):

        # get fname
        q = "select fname from TRACKS where id=%d" % (trackid)
        r = self.conn.execute(q)
        if not r:
            return False

        fname = r.fetchone()[0]

        # delete
        q = "delete from TRACK_IN_PLACES where id_track=%d" % (trackid)
        r = self.conn.execute(q)
        if not r:
            return False

        q = "delete from TRACKS where id=%d" % (trackid)
        self.conn.execute(q)

        # insert into deleted tracks
        td = TracksDeleted(fname)
        self.conn.execute(td.sql_insert_script())
        return True

    def DeletePlaceFromTrack(self, trackid, placeid):
        q = "delete from TRACK_IN_PLACES where id_track=%d and id_place=%d" % (trackid, placeid)
        r = self.conn.execute(q)
        if not r:
            return False
        return True

    def DeleteAllPlacesFromTrack(self, trackid):
        q = "delete from TRACK_IN_PLACES where id_track=%d" % (trackid)
        r = self.conn.execute(q)
        if not r:
            return False
        return True

    def DeletePlace(self, placeid):
        q = "delete from TRACK_IN_PLACES where id_place=%d" % (placeid)
        r = self.conn.execute(q)
        if not r:
            return False

        q = "delete from PLACES where id=%d" % (placeid)
        self.conn.execute(q)
        return True



    def SavePlaceDescription(self, placeid, description):
        q = "update PLACES set description='%s' where id=%d" % (description, placeid)
        self.conn.execute(q)
        d = D()
        d.id = placeid
        d.description = description

        return d

    def SavePlaceLatLonElev(self, placeid, lat, lon, ele):
        q = "update PLACES set latitude=%f,longitude=%f,elevation=%f where id=%d" % (lat, lon, ele, placeid)
        self.conn.execute(q)

        d = D()
        d.id = placeid
        d.lat = lat
        d.lon = lon
        d.ele = ele

        return d

    def CreateAltitudePNG(self, trackid):

        track = Track(None, None, None)
        track.id = trackid
        track.load(self.conn)
        # I get the track, and gpx info, so build the PNG.

        factory = altitude.PNGFactory()
        png = factory.CreatePNG(track.gpx)

        f = open("altitude.png", "wb+")
        png.save(f, "PNG")
        f.close()

    def GetStatsFromDB(self, include_cloned=True):
        """
        select count(*) from tracks;
        select count(*) from places;
        select sum(distance) from tracks;
        select sum(elevation) from tracks;

        select sum(elevation), kind from tracks group by kind;
        select sum(distance), kind from tracks group by kind;

        select sum(elevation), equipment from tracks group by equipment;
        select sum(distance), equipment from tracks group by equipment;

        """
        cloned_filter = "where cloned=0"
        if include_cloned: cloned_filter = ""


        # number_of_places = self.conn.execute("")[0]
        s = {}
        s['number_of_tracks'] = self.conn.execute("select count(*) from tracks where cloned=0 ").fetchone()[0]
        s['number_of_total_tracks'] = self.conn.execute("select count(*) from tracks").fetchone()[0]
        s['number_of_places'] = self.conn.execute("select count(*) from places").fetchone()[0]
        s['number_of_places_with_info'] = self.conn.execute("select count(*) from places where latitude!=0 and longitude!=0").fetchone()[0]
        s['total_distance'] = self.conn.execute("select sum(distance) from tracks %s " % cloned_filter).fetchone()[0]
        s['total_elevation'] = self.conn.execute("select sum(elevation) from tracks %s " % cloned_filter).fetchone()[0]


        s['by_kind'] = []
        for row in self.conn.execute("select sum(elevation),sum(distance),count(*),kind from tracks %s group by kind" % cloned_filter):
            d = {}
            d['elevation'] = row[0]
            d['distance'] = row[1]
            d['number'] = row[2]
            d['kind'] = row[3]

            if row[3].endswith("_T"):
                continue


            s['by_kind'].append(d)

        s['by_equipment'] = []
        for row in self.conn.execute("select sum(elevation),sum(distance),count(*),kind,equipment from tracks %s  group by kind, equipment" % cloned_filter):
            d = {}
            d['elevation'] = row[0]
            d['distance'] = row[1]
            d['number'] = row[2]
            d['kind'] = row[3]
            d['equipment'] = row[4]

            s['by_equipment'].append(d)


        s['kinds'] = self.conn.execute("select distinct kind from tracks order by kind ").fetchall()

        s['years'] = []
        for row in self.conn.execute("SELECT strftime('%%Y', datetime(start_stamp, 'unixepoch')) as year, sum(elevation),sum(distance),count(*) FROM TRACKS %s group by year" % cloned_filter):
            d = {}
            d['year'] = row[0]
            d['elevation'] = row[1]
            d['distance'] = row[2]
            d['number'] = row[3]
            s['years'].append(d)

        s['by_equipment_and_year'] = {}
        for y in s['years']:
            s['by_equipment_and_year'][y['year']] = []
            local_cloned_filter = cloned_filter
            if local_cloned_filter: local_cloned_filter = "and cloned=0"
            for row in self.conn.execute("select sum(elevation),sum(distance),count(*),kind,equipment,strftime('%%Y', datetime(start_stamp, 'unixepoch')) as year from tracks where year='%s' %s group by kind, equipment" % (y['year'],local_cloned_filter)):
                d = {}
                d['elevation'] = row[0]
                d['distance'] = row[1]
                d['number'] = row[2]
                d['kind'] = row[3]
                d['equipment'] = row[4]
                d['year'] = row[5]

                s['by_equipment_and_year'][y['year']].append(d)

        return s

    def RegenerateCache(self, opts, trackid=None, fullmode=True):

        q = "select ID from TRACKS"
        if trackid:
            # support for -T 352, and -T '>=352' (to continue)
            if trackid[0].isdigit():
                tid = "=%s" % trackid
            else:
                tid = "%s" % trackid
            q = q + " where id %s" % tid

        lopts = wwwhandlers.mockhandler.D()
        lopts.dbfile = opts.dbfile
        lopts.nocache = True
        lopts.slope_distance_gap = self.slope_distance_gap
        lopts.cachedir = opts.cachedir

        mockh = wwwhandlers.mockhandler.HandlerAdapter(lopts)
        preview_h = wwwhandlers.converters.TRACKPREVIEW_Handler()
        kml_h = wwwhandlers.converters.TRACK2KML_Handler()
        alt_h = wwwhandlers.converters.ElevationPNG_Handler()


        for row in self.conn.execute(q):

            id = int(row[0])
            track = Track(None, None, None)
            track.id = id
            track.load(self.conn)
            track.ToReadable()

            if fullmode:
                gpx = GPXItem()
                gpx.Load(track.fname)
                gpx.MergeAll()
                gpx.gpx.tracks[0].segments[0].points = filter(lambda x: x.latitude != 0.0 and x.longitude != 0.0, gpx.gpx.tracks[0].segments[0].points)

                stats = gpxstats.CalculateStats(gpx.gpx.tracks[0].segments[0].points , distance=self.slope_distance_gap, hint=track.kind)

                gpx_optmizer = GPXOptimizer()
                opt_points = gpx_optmizer.Optimize(gpx.gpx.tracks[0].segments[0].points)
                #print "Regenerating NumPoints for track.id=%d" % track.id
                #self.UpdateTrackNumPoints(track.id, len(opt_points))

                gpx_optmizer.Print_stats()

                # future: regenerating slope
                track.SetStats(stats)
                self.UpdateTrackStats(track)
                print ""
                print "[*%d Title: %s]" % (track.id, track.title)
                print "[*File: %s]" % track.fname
                stats.PrintStats()
                self.conn.commit()

            args = { 'id': track.id, 'sz': "200x100" }
            print "Regenerating PNG preview for track.id=%d, %s" % (args['id'], args['sz'])
            mockh.Invoke(preview_h, args)

            args = { 'id': track.id, 'sz': "700x700" }
            print "Regenerating PNG preview for track.id=%d, %s" % (args['id'], args['sz'])
            mockh.Invoke(preview_h, args)

            args['sz'] = "700x150"
            args['mode'] = "full"
            print "Regenerating PNG Altitude for track.id=%d, %s" % (args['id'], args['sz'])
            mockh.Invoke(alt_h, args)

            if fullmode:
                print "Regenerating KML preview for track.id=%d" % (args['id'])
                mockh.Invoke(kml_h, args)

                args['sz'] = "202x40"
                args['mode'] = 'simple'
                print "Regenerating PNG Altitude for track.id=%d, %s" % (args['id'], args['sz'])
                mockh.Invoke(alt_h, args)

                args['sz'] = "700x150"
                args['mode'] = "full"
                print "Regenerating PNG Altitude for track.id=%d, %s" % (args['id'], args['sz'])
                mockh.Invoke(alt_h, args)

                args = { 'id': track.id  }
                print "Regenerating Bounds for track.id=%d" % (args['id'])
                self.UpdateTrackBounds(track)



    def RegenerateStats(self, opts, trackid=None):

        q = "select ID from TRACKS"
        if trackid:
            # support for -T 352, and -T '>=352' (to continue)
            if trackid[0].isdigit():
                tid = "=%s" % trackid
            else:
                tid = "%s" % trackid
            q = q + " where id %s" % tid


        lopts = wwwhandlers.mockhandler.D()
        lopts.dbfile = opts.dbfile
        lopts.nocache = True
        lopts.slope_distance_gap = self.slope_distance_gap
        lopts.cachedir = opts.cachedir

        for row in self.conn.execute(q):

            id = int(row[0])
            track = Track(None, None, None)
            track.id = id
            track.load(self.conn)
            track.ToReadable()

            gpx = GPXItem()
            gpx.Load(track.fname)
            gpx.MergeAll()
            gpx.gpx.tracks[0].segments[0].points = filter(lambda x: x.latitude != 0.0 and x.longitude != 0.0, gpx.gpx.tracks[0].segments[0].points)

            stats = gpxstats.CalculateStats(gpx.gpx.tracks[0].segments[0].points , distance=self.slope_distance_gap, hint=track.kind)

            track.SetStats(stats)
            print ""
            print "[*%d Title: %s]" % (track.id, track.title)
            print "[*File: %s]" % track.fname
            self.UpdateTrackStats(track)
            stats.PrintStats()
            self.conn.commit()

            if stats.duration > 3600 * 12:
                print "Stopping due a suspicius track duration. Commiting previous work"
                self.conn.commit()
                sys.exit(0)

    def RegenerateWaypoints(self, opts):

        lopts = wwwhandlers.mockhandler.D()
        lopts.dbfile = opts.dbfile
        lopts.nocache = True
        lopts.cachedir = opts.cachedir

        mockh = wwwhandlers.mockhandler.HandlerAdapter(lopts)
        wpt_h = wwwhandlers.converters.WPT2KML_Handler()
        args = { 'id': 'landmarks' }
        print "Regenerating Waypoints(LandMarks)"
        mockh.Invoke(wpt_h, args)



    def UpdateTrackStats(self, track):
        q = """update TRACKS set
                SCORE=%f,
                UPHILL_DISTANCE=%f,
                LEVEL_DISTANCE=%f,
                DOWNHILL_DISTANCE=%f,
                UPHILL_ELEVATION=%f,
                LEVEL_ELEVATION=%f,
                DOWNHILL_ELEVATION=%f,
                UPHILL_AVG_SLOPE=%f,
                LEVEL_AVG_SLOPE=%f,
                DOWNHILL_AVG_SLOPE=%f,
                UPHILL_P_DISTANCE=%f,
                LEVEL_P_DISTANCE=%f,
                DOWNHILL_P_DISTANCE=%f,

                UPHILL_SPEED=%f,
                LEVEL_SPEED=%f,
                DOWNHILL_SPEED=%f,

                UPHILL_TIME=%d,
                LEVEL_TIME=%d,
                DOWNHILL_TIME=%d,

                UPHILL_P_TIME=%f,
                LEVEL_P_TIME=%f,
                DOWNHILL_P_TIME=%f,

                ELEVATION=%f,
                DISTANCE=%f,

                CENTER_LAT=%f,
                CENTER_LON=%f,
                CLOCKWISE=%d,
                NUMPOINTS=%d,

                DURATION=%d,
                SPEED_AVG=%f,

                UPHILL_SLOPE_RANGE_DISTANCE='%s',
                DOWNHILL_SLOPE_RANGE_DISTANCE='%s',
                UPHILL_SLOPE_RANGE_TIME='%s',
                DOWNHILL_SLOPE_RANGE_TIME='%s',
                MAX_ALTITUDE=%f,
                MIN_ALTITUDE=%f,
                QUALITY=%f

                where id=%d""" % (track.score, \
                                                          track.uphill_distance, track.level_distance, track.downhill_distance, \
                                                          track.uphill_elevation, track.level_elevation, track.downhill_elevation, \
                                                          track.uphill_avg_slope, track.level_avg_slope, track.downhill_avg_slope, \
                                                          track.uphill_p_distance, track.level_p_distance, track.downhill_p_distance, \

                                                          track.uphill_speed, track.level_speed, track.downhill_speed,
                                                          track.uphill_time, track.level_time, track.downhill_time,
                                                          track.uphill_p_time, track.level_p_time, track.downhill_p_time,

                                                          track.elevation,
                                                          track.distance,

                                                          track.center_lat, track.center_lon, track.clockwise,
                                                          track.numpoints,
                                                          track.duration, track.speed_avg,

                                                          track.uphill_slope_ranges_distance,
                                                          track.downhill_slope_ranges_distance,
                                                          track.uphill_slope_ranges_time,
                                                          track.downhill_slope_ranges_time,
                                                          track.max_altitude,
                                                          track.min_altitude,
                                                          track.quality,

                                                          track.id)

        self.conn.execute(q)


    def UpdateTrackBounds(self, track):

        # calculate bounds
        track.LoadGPXFromFile()
        gpx = GPXItem()
        gpx.LoadFromString(track.gpx)
        gpx.MergeAll()

        gpx.gpx.tracks[0].segments[0].points = filter(lambda x: x.latitude != 0.0 and x.longitude != 0.0, gpx.gpx.tracks[0].segments[0].points)

        bounds = gpx.Bounds()

        SW = D()
        NE = D()
        SW.latitude = bounds.min_latitude
        SW.longitude = bounds.min_longitude
        NE.latitude = bounds.max_latitude
        NE.longitude = bounds.max_longitude

        # NW = geo.Location(bounds.max_latitude, bounds.min_longitude)
        # SE = geo.Location(bounds.min_latitude, bounds.max_longitude)

        q = "update TRACKS set NE_lat={ne_lat}, NE_lon={ne_lon}, SW_lat={sw_lat}, SW_lon={sw_lon} where ID={trackid}"
        q = q.format(ne_lat=NE.latitude, ne_lon=NE.longitude,
                 sw_lat=SW.latitude, sw_lon=SW.longitude,
                 trackid=track.id)

        self.conn.execute(q)


        # b = "and p.longitude >= {w_lon} and p.longitude <= {e_lon} and p.latitude <= {n_lat} and p.latitude >= {s_lat}"
        # b = b.format( w_lon = bounds['SW']['lon'],
        #              e_lon = bounds['NE']['lon'],
        #              n_lat = bounds['NE']['lat'],
        #              s_lat = bounds['SW']['lat'] )

    def TrackClone(self, trackid, tgtid):
        """clone title & places from trackid into tgtid"""

        # first, delete all the places from tgtid
        q = "delete from TRACK_IN_PLACES where id_track=%d" % tgtid
        self.conn.execute(q)

        # second, copy all the places from src
        q = "insert into TRACK_IN_PLACES (id_track, id_place) SELECT %d as tgtid, id_place from TRACK_IN_PLACES where id_track=%d" % (tgtid, trackid)
        self.conn.execute(q)

        # copy title
        q = "update TRACKS set title = (select title from TRACKS where id=%d) where id=%d" % (trackid, tgtid)
        self.conn.execute(q)

        # copy circular
        q = "update TRACKS set circular = (select circular from TRACKS where id=%d) where id=%d" % (trackid, tgtid)
        self.conn.execute(q)

        # copy clockwise
        q = "update TRACKS set clockwise = (select clockwise from TRACKS where id=%d) where id=%d" % (trackid, tgtid)
        self.conn.execute(q)

        # update cloned field
        q = "update TRACKS set cloned=%d where id=%d" % (trackid, tgtid)
        self.conn.execute(q)



        track = Track(None, None, None)
        track.id = tgtid
        track.load(self.conn)

        self.conn.commit()
        return track





    def ExportPlacesAsGPX(self,fname):

        places = self.LoadAllPlaces()
        data = gpxpy.utils.Points2GPXWayPoints(places)

        fd = open(fname,"wb+")
        fd.write(data.encode('UTF-8'))
        fd.close()


    def PurgePlaces(self):
        q = "select count(*) from places where latitude=0 and longitude = 0 and id not in (select id_place from track_in_places)"

        #q = "delete from places where latitude=0 and longitude = 0 and id not in (select id_place from track_in_places)"
        number = self.conn.execute(q).fetchone()[0]
        print "Number of tracks purged: %d" % (number)
        q = "delete from places where latitude=0 and longitude = 0 and id not in (select id_place from track_in_places)"
        number = self.conn.execute(q)
        self.conn.commit()


    def GetPlacesByLocation(self, trackid, distance=10.0, gpx_points=None):

        track = self.LoadTrackFromDB(trackid)

        if not track.fname:
            print("Can't load TrackID %s. Bailing out." % track.id)
            dbmanager.Close()
            sys.exit(0)


        print("Working on track=%s distance=%3.2f [fname=%s]" % (track.id, distance, track.fname))

        if not gpx_points:

            gpx = GPXItem()
            gpx.Load(track.fname)
            gpx.MergeAll()
            gpx.gpx.tracks[0].segments[0].points = filter(lambda x: x.latitude!=0.0 and x.longitude!=0.0, gpx.gpx.tracks[0].segments[0].points)

            gpx_optmizer = GPXOptimizer()
            opt_points = gpx_optmizer.Optimize(gpx.gpx.tracks[0].segments[0].points)
            gpx_optmizer.Print_stats()
            gpx.gpx.tracks[0].segments[0].points=  opt_points
            gpx_points = gpx.gpx.tracks[0].segments[0].points

        print("Doing: %d points" % len(gpx_points))
        points = gpx_points

        places_found_keys = {}
        places_found = []

        for p in points:

            # do the magic. Create a bound, then ... load all places in that bound.
            #b = b.format(w_lon=bounds['SW']['lon'],
            #            [NE]
            #          /
            #         /  (radious)
            #       [p]
            #       /
            #      /
            #   [SW]

            location_d = gpxpy.geo.LocationDelta(distance=distance,angle=45)   #NE
            NE = location_d.move(p)
            location_d = gpxpy.geo.LocationDelta(distance=distance,angle=225)  #SW
            SW =location_d.move(p)

            bounds = { 'NE': { 'lat': NE[0], 'lon': NE[1]},
                       'SW': { 'lat': SW[0], 'lon': SW[1]} }

            places = self.LoadPlacesByBounds(bounds=bounds)

            if len(places) > 0:
                for place in places:
                    if not place.id in places_found_keys:
                        places_found_keys[place.id] = True
                        places_found.append(place)

            sys.stdout.write('.')
        print "-Done-"
        print "Places Found (in order):"
        for p in places_found:
            print "\t(%d)\t'%s' ('%s')\t\t[%3.2f,%3.2f@%3.2f]" % (p.id, p.name.encode('utf-8',errors='replace'), p.description.encode('utf-8',errors='replace'), p.latitude, p.longitude, p.elevation)

        return places_found


    def RegenerateTrackPlaces(self, trackid, opts):
        ## do the regeneration here for a given track
        
        ## TBD
        
        track = self.LoadTrackFromDB(trackid)

        
        places_list = self.GetPlacesByLocation(track.id, opts)

        q = "delete from track_in_places where id_track = %d" % track.id
        self.conn.execute(q)
        
        for place in places_list:
            track_in_places = TrackInPlaces(track.id, place.id)
            track_in_places.insert(self.conn)

        places = map(lambda x: x.name.capitalize(), places_list)
        # rewrite the title.
        track.title = "* " + " - ".join(places)
        #####self.SaveTrackTitle(track.id, track.title)
        # commit it, so we can use the DB in the handlers.
        
        self.conn.commit()
        return places

    def RegenerateTitlesAndPlaces(self, opts, trackid=None):
        
        # batch code to regenerate all the places and the titles.
        
        q = "select ID from TRACKS"
        
        if trackid:
            # support for -T 352, and -T '>=352' (to continue)
            if trackid[0].isdigit():
                tid = "=%s" % trackid
            else:
                tid = "%s" % trackid
            q = q + " where id %s" % tid


        for row in self.conn.execute(q):

            id = int(row[0])
            track = Track(None, None, None)
            track.id = id
            track.load(self.conn)
        
            places_list = self.GetPlacesByLocation(track.id, opts.distance_to_place)

            q = "delete from track_in_places where id_track = %d" % track.id
            self.conn.execute(q)
        
            for place in places_list:
                track_in_places = TrackInPlaces(track.id, place.id)
                track_in_places.insert(self.conn)

            places = map(lambda x: x.name.capitalize(), places_list)
            # rewrite the title.
            track.title = "* " + " - ".join(places)
            self.SaveTrackTitle(track.id, track.title)
            # commit it, so we can use the DB in the handlers.
            


def TEST_RE():
    r1 = "2016-10-03-18-07-29 --- [MTB,FENIX3,SANTACRUZ] Navas-Bajoncillo-Trialera-Pantano-Rampa hormigon-Morro-Trialera-Cuesta-Santa Ana-Canal-Elevadora-Navas.gpx"
    r2 = "2016-10-03-18-07-29 --- [MTB] Navas_Bajoncillo_Trialera_Pantano_Rampa hormigon_Morro_Trialera_Cuesta_Santa Ana_Canal_Elevadora_Navas.gpx"
    r3 = "2016-10-03-18-07-29 --- Navas_Bajoncillo_Trialera_Pantano_Rampa hormigon_Morro_Trialera_Cuesta_Santa Ana_Canal_Elevadora_Navas.gpx"
    r4 = "Navas_Almenara_Robledo_San_Antonio_Fresnedillas_Navalagamella_Colmenar_NASA_Navas.gpx"

    r = [ r1, r2, r3, r4 ]

    t = Track("", "", "", "")

    for i in r:
        print i
        stamp, tags, places, extension = t.ParseFileName(i)
        print "STAMP:  ", stamp
        print "TAGS:   ", tags
        print "PLACES: ", places
        print "EXT:    ", extension

    sys.exit(0)


if __name__ == "__main__":

    dbmanager = DBManager()
    parser = argparse.ArgumentParser()


    parser.add_argument("-v", "--verbose", help="Show data about file and processing", action="count")
    parser.add_argument("-c", "--create", help="Create the database", action="store_true")
    parser.add_argument("-i", "--insert", help="Insert GPX File into DB", action="store")
    parser.add_argument("-w", "--waypoints", help="Insert GPX Waypoints as Places into DB", action="store")
    parser.add_argument("-d", "--description", help="Optional description for GPX")
    parser.add_argument("-g", "--get", help="Get track From Database")
    parser.add_argument("-a", "--altitude", help="Create Altitude PNG")
    parser.add_argument("-C", "--cachedir", help="Where the cache is stored", action="store", default="cache")
    parser.add_argument("-R", "--regenerate", help="Regenerate the cache", action="store_true")
    parser.add_argument("-R:w", "--regenerate_waypoints", help="Regenerate waypoints (LandMarks)", action="store_true")
    parser.add_argument("-R:s", "--regenerate_stats", help="Regenerate only the stats", action="store_true")
    parser.add_argument("-R:e", "--regenerate_elevation", help="Regenerate only the elevation", action="store_true")
    parser.add_argument("-R:t", "--regenerate_titles_and_places", help="Regenerate the titles and places", action="store_true")
    parser.add_argument("-F", "--fix_deleted", help="Regenerate only the stats", action="store")
    parser.add_argument("-T", "--track", help="Id of track being regenerated", action="store")
    parser.add_argument("-E:p", "--export_places", help="Export Places as GPX (filename)", action="store")
    parser.add_argument("-P:p", "--purge_places", help="Purge Places (lat=0, lon=0 and not used)", action="store_true")
    parser.add_argument("-D:p", "--distance_to_place", help="Purge Places (lat=0, lon=0 and not used)", action="store",type=float,default=80.0)

    parser.add_argument("dbfile", nargs="?", help="Database file (SqlLite3)")
    args = parser.parse_args()



    dbmanager.verbose = args.verbose

    # Return a file from database ##############################################
    if args.get:
        dbmanager.Connect(args.dbfile)
        dbmanager.LoadTrackFromDB(args.get)

        dbmanager.CloseAndCommit()
        sys.exit(0)

    # Draw the pngbase #########################################################
    if args.altitude:
        dbmanager.Connect(args.dbfile)
        dbmanager.CreateAltitudePNG(args.altitude)

        dbmanager.CloseAndCommit()
        sys.exit(0)


    # Create database #########################################################
    if args.create:
        dbmanager.CreateDB(args.dbfile)
        sys.exit(0)

    # load tracks from file ###################################################
    if args.insert:

        dbmanager.Connect(args.dbfile)

        if not os.path.exists(args.insert):
            gpxfiles = glob.glob(args.insert)
            if gpxfiles == []:
                print "Error: File not found (%s). Bailing out" % args.insert
                sys.exit(0)
        else:
            # load a file, or walk the directory for all de files.
            if os.path.isfile(args.insert):
                gpxfiles = [ args.insert ]
            else:
                gpxfiles = []
                for root, dirs, files in os.walk(args.insert):
                    for file in files:
                        _, ext = os.path.splitext(file)
                        if ext.lower() == '.gpx':
                            gpxfiles.append(os.sep.join([ root, file ]))


        for gpxfile in gpxfiles:


            r = dbmanager.InsertGPXIntoDB(gpxfile, description=args.description, opts=args)
            msg = "[OK] ADDED: %s to DB"
            if not r:
                msg = "[XX] error: %s"
            print  msg % gpxfile
        dbmanager.CloseAndCommit()

    # load waypoints as places  ################################################
    if args.waypoints:

        dbmanager.Connect(args.dbfile)

        if not os.path.exists(args.waypoints):
            gpxfiles = glob.glob(args.waypoints)
            if gpxfiles == []:
                print "Error: File not found (%s). Bailing out" % args.waypoints
                sys.exit(0)
        else:
            # load a file, or walk the directory for all de files.
            if os.path.isfile(args.waypoints):
                gpxfiles = [ args.waypoints ]
            else:
                gpxfiles = []
                for root, dirs, files in os.walk(args.waypoints):
                    for file in files:
                        _, ext = os.path.splitext(file)
                        if ext.lower() == '.gpx':
                            gpxfiles.append(os.sep.join([ root, file ]))


        for gpxfile in gpxfiles:


            r = dbmanager.InsertWayPointGPXIntoDB(gpxfile, description=args.description, opts=args)
            msg = "[OK] ADDED: %s to DB"
            if not r:
                msg = "[XX] error: %s"
            print  msg % gpxfile
        dbmanager.CloseAndCommit()

    # Regenerate caches  #######################################################
    if args.regenerate:
        dbmanager.Connect(args.dbfile)
        if args.track:
            dbmanager.RegenerateCache(args, trackid=args.track)
        else:
            dbmanager.RegenerateCache(args)
        dbmanager.CloseAndCommit()

    # Regenerate caches  #######################################################
    if args.regenerate_elevation:
        dbmanager.Connect(args.dbfile)
        if args.track:
            dbmanager.RegenerateCache(args, trackid=args.track,fullmode=False)
        else:
            dbmanager.RegenerateCache(args, fullmode=False)
        dbmanager.CloseAndCommit()

    # Regenerate stats  ########################################################
    if args.regenerate_stats:
        dbmanager.Connect(args.dbfile)
        if args.track:
            dbmanager.RegenerateStats(args, trackid=args.track)
        else:
            dbmanager.RegenerateStats(args)
        dbmanager.CloseAndCommit()

    # Regenerate waypoints######################################################
    if args.regenerate_waypoints:
        dbmanager.Connect(args.dbfile)
        dbmanager.RegenerateWaypoints(args)
        dbmanager.CloseAndCommit()

    # Regenerate titles and places #############################################
    if args.regenerate_titles_and_places:
        dbmanager.Connect(args.dbfile)
        dbmanager.RegenerateTitlesAndPlaces(args, trackid=args.track)
        dbmanager.CloseAndCommit()



    # Export places as GPX #####################################################
    if args.export_places:
        dbmanager.Connect(args.dbfile)
        dbmanager.ExportPlacesAsGPX(args.export_places)
        dbmanager.Close()

    # Purge Database (Places) ##################################################
    if args.purge_places:
        dbmanager.Connect(args.dbfile)
        dbmanager.PurgePlaces()
        dbmanager.CloseAndCommit()

    # FIX RODILLO AND THEORIC Tracks ###########################################
    if args.fix_deleted:

        dbmanager.Connect(args.dbfile)

        if not os.path.exists(args.fix_deleted):
            gpxfiles = glob.glob(args.fix_deleted)
            if gpxfiles == []:
                print "Error: File not found (%s). Bailing out" % args.fix_deleted
                sys.exit(0)
        else:
            # load a file, or walk the directory for all de files.
            if os.path.isfile(args.fix_deleted):
                gpxfiles = [ args.fix_deleted ]
            else:
                gpxfiles = []
                for root, dirs, files in os.walk(args.fix_deleted):
                    for file in files:
                        _, ext = os.path.splitext(file)
                        if ext.lower() == '.gpx':
                            gpxfiles.append(os.sep.join([ root, file ]))


        for gpxfile in gpxfiles:


            r = dbmanager.FixDeletedIntoDB(gpxfile, description=args.description)
            msg = "[OK] ADDED to DELETED_TRACKS: %s to DB"
            if not r:
                msg = "[XX] error: %s"
            print  msg % gpxfile
        dbmanager.CloseAndCommit()
