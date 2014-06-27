#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
File: phBackup.py

This script backup manifests DB for NGAR MDS
It requires module library modPh.py together with other
'standard' modules

Ver     Date        Author      Desc
0.00    20140415    Chris Janes Original Development
"""
#############################################
#
#   Here we import modules required
#
#############################################
# enable debugging
import sys
sys.path.append('/var/lib/phoneHome/lib')

import cgitb
import cgi
import ConfigParser
import datetime
import logging
import os
import psycopg2
import re

from modPh import modPh

#############################################
#
#   Here we st up our enviroment
#
#############################################

phoneHome = modPh()
log = logging.getLogger('phBackup')
logfile = phoneHome.logLoc + 'phBackup.log'
print 'logfile = ' + logfile
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



#############################################
#
#   Here are function definitions
#
#############################################

def makeBackup():
    """This function will create a backup in backupLoc"""
    filename = phoneHome.backupLoc + phoneHome.backupPrefix + '_tmp' + phoneHome.backupSuffix
    if os.path.isfile(filename):
        os.remove(filename)
    phoneHome.manSave(filename)
    
    
def tidyBackup():
    """
    This function manages the automatic backup files
    
    Arguments:
        None
    Return:
        None
    This function limits the number of backup kept to that definned in phoneHome.conf.backups.numberbackups
    This script can be run from cron with an entry in crontab like this 58 23 * * * /var/www/cgi-bin/phBackup.py
    Note that the following are all configurable in phoneHome.conf
        phoneHome.backupLoc     the location where backup file are stored
        phoneHome.backupPrefix  Prefix for backup files
        phoneHome.backupSuffix  Suffix for backup files
    """
    latestBackup = phoneHome.backupLoc + phoneHome.backupPrefix + '_tmp' + phoneHome.backupSuffix
    if os.path.isfile(latestBackup):
        for number in range(int(phoneHome.numberBackups), 0, -1):
            if number == int(phoneHome.numberBackups):
                filename = phoneHome.backupLoc + phoneHome.backupPrefix + str(number) + phoneHome.backupSuffix
                if os.path.isfile(filename):
                    os.remove(filename)
                
                else:
                    print filename + ' did not exist'
                oldfilename = filename
                
            else:
                print 'number = ' + str(number)
                filename = phoneHome.backupLoc + phoneHome.backupPrefix + str(number) + phoneHome.backupSuffix
                if os.path.isfile(filename):
                    os.rename(filename, oldfilename)
                else:
                    log.debug(filename + ' did not exist')
                oldfilename = filename
        os.rename(latestBackup, oldfilename)
        
    


#############################################
#
#   Here are the code proper starts
#
#############################################

log.info('phBackup Started')
makeBackup()
tidyBackup()
