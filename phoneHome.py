#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
File: phMan.py

This script provide manifest delivery to MA for NGAR MDS
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
import logging

from modPh import modPh

#############################################
#
#   Here we st up our enviroment
#
#############################################

phoneHome = modPh()


cgitb.enable()
log = logging.getLogger('phoneHome')
logfile = phoneHome.logLoc + 'phoneHome.log'
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
configFile = 'phoneHome.conf'
# The following are the details required for the db connect string


#############################################
#
#   Here are function definitions
#
#############################################



#############################################
#
#   Here the code proper starts
#
#############################################

form = cgi.FieldStorage()
phoneHome = modPh()
if not (form.has_key('fqdn')):
    log.debug('phoneHome.manDefault')
    phoneHome.manDefault()
else:
    FQDN = form.getvalue('fqdn').upper()
    
    log.debug('phoneHome.manManifest ' + FQDN )
    phoneHome.manManifest(FQDN)

