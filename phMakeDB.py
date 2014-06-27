#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
File: phMakeDB.py

This script creates the DB for NGAR MDS
It requires module library modPh.py together with other
'standard' modules

Ver     Date        Author      Desc
0.00    20140410    Chris Janes Original Development
"""


#############################################
#
#   Here we import modules required
#
#############################################
import sys
sys.path.append('/var/lib/phoneHome/lib')
import cgitb
import cgi
import ConfigParser
import datetime
import logging
import os
import psycopg2
import time
import re
import sqlite3

from modPh import modPh

#############################################
#
#   Here we set up our enviroment
#
#############################################
phoneHome = modPh()


cgitb.enable()
log = logging.getLogger('phMan')
logfile = phoneHome.logLoc + 'phMan.log'
hdlr = logging.FileHandler(logfile)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
log.addHandler(hdlr) 
log.setLevel(logging.DEBUG)


#############################################
#
#   Here are the global variables required
#
#############################################

# The following are the details required for the db connect string


# we set up a datetime var as now
now = datetime.datetime.now()

#############################################
#
#   Here are function definitions
#
#############################################


#############################################
#
#   Here are the code proper starts
#
#############################################


if phoneHome.testDbExists():
    print 'DB Exists'
else:
    print 'DB does not Exists'
    if modPh.dbtype == 'sqlite':
        conn = phoneHome.getconn()
        cur = conn.cursor()
        cur.execute('CREATE TABLE manifest (host text, sequence int, includefile text ,PRIMARY KEY (host, sequence));')
        conn.commit()
        conn.close()

        