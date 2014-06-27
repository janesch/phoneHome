#!/usr/bin/python
# -*- coding: UTF-8 -*-

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
import threading

from modPh import modPh

#############################################
#
#   Here we set up our enviroment
#
#############################################
phoneHome = modPh()


cgitb.enable()
log = logging.getLogger('phDev')
logfile = phoneHome.logLoc + 'phDev.log'
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

class myThread (threading.Thread):
    def __init__(self, threadID):
        threading.Thread.__init__(self)
        self.threadID = threadID

    def run(self):
        log.debug("~~~Starting " + self.name)
        reloadAllAgents()
        log.debug("~~~Exiting " + self.name)

def showMenu(manifest):
    phoneHome.htmlHeader()
    print '<body>'
    print "<h1>phDev Menu</h1><br><br>";
    print '<table style="width:100px" id="menu">'
    
    print '<tr><td>Default Agent is ' + manifest + '</td></tr>' 
     
    print '<tr><form action="/cgi-bin/phDev.py" method="post" target="_self">'
    print '<input type="hidden" name="function" value="reloadAgent">'
    print '<td width="100" align="center"> <input type="submit" value="Reload ' + manifest + '" class="menu"/></td></tr>'
    print '</form>'
    
    print '<tr><form action="/cgi-bin/phDev.py" method="post" target="_self">'
    print '<input type="hidden" name="function" value="selectAgent">'
    print '<td width="100" align="center"> <input type="submit" value="Select Agent" class="menu"/></td></tr>'
    print '</form>'
    
    print '<tr><form action="/cgi-bin/phDev.py" method="post" target="_self">'
    print '<input type="hidden" name="function" value="reloadAllAgents">'
    print '<td width="100" align="center"> <input type="submit" value="Reload All Agents" class="menu"/></td></tr>'
    print '</form>'

    print '<tr><form action="/cgi-bin/phDev.py" method="post" target="_self">'
    print '<input type="hidden" name="function" value="disable">'
    print '<td width="100" align="center"> <input type="submit" value="Disable phDev Functionallity" class="menu"/></td></tr>'
    print '</form>'
    
    print '<tr><form action="/cgi-bin/phMan.py" method="post" target="_self">'
    print '<td width="100" align="center"> <input type="hidden" name="function" value="">'
    print '<input type="submit" value="Main Menu"  class="menu"/></td></tr>'
    print '</form>'
    
    print '</table>'
    return

def reloadAgent(manifest):            
    log.info('reloadAgent  ' + manifest)
    host = manifest + ':9080'
    phoneHome.agentCheck(host , 'admin', 'admin')

def reloadAllAgents():
    log.info('reloadAllAgents')
    listHosts = phoneHome.listManifests()
    for host in listHosts:
        log.debug('host = ' + host)
        try:
            phoneHome.agentCheck(host + ':9080', 'admin', 'admin')
            log.info('~~~Manifest reload requested for ' + host)
            #time.sleep(5)
        except:
            log.info('~~~Manifest reload failure for ' + host)

def doReloadAllAgents():
    log.info('doReloadAllAgents')
    phoneHome.htmlHeader()
    print '<body>'
    print "<h1>phDev Menu</h1><br><br>";
    print '<table style="width:100px" id="menu">'
    print '<tr><td>Reloading Manifests for all Agents in background</td></tr>'
    thread1 = myThread(1)
    log.info('thread1.start')
    thread1.start
    print '<tr><form action="/cgi-bin/phDev.py" method="post" target="_self">'
    print '<td width="100" align="center"> <input type="hidden" name="function" value="">'
    print '<input type="submit" value="Continue"  class="menu"/></td></tr>'
    print '</form>'
    
    print '</table>'
    return
    
    
def selectAgent():
    log.debug( 'selectAgent' )
    array = phoneHome.listManifests()
    lenArray = len(array)
    array.sort()

    phoneHome.htmlHeader()
    print "<h1>phDev - Select Agent</h1><br><br>";
    print '<table style="width:800px" id="manifest" >'
    print '<form action="/cgi-bin/phDev.py" method="post" target="_self">'
    colwidth = (800 / int(phoneHome.colManifest)) - 10
    count = 0
    for data in array:
        if count == 0:
            print '<tr>'
        print '<td width="' + str(colwidth) + '" align="right">' + data + '</td><td width="10"><input type="radio" name="newManifest" value="' + data + '"></td>'
        count = count + 1
        if count == int(phoneHome.colManifest):
            count = 0
            print '</tr>'
    print '</table><br><br>'
    print '<table id="chris">'
    print '<tr><td></td><td></td></tr>'
    print '<tr><td><input type="hidden" name="function" value="setAgent"><input type="submit" value="Select Agent" /></td>'
    print '</form>'
    print '<form action="/cgi-bin/phDev.py" method="post" target="_self">'
    print '<td><input type="hidden" name="function" value=""><input type="submit" value="Cancel" /></td></tr>'
    print '</form>'
    print '</table>'    

def setAgent(setAgent):
    log.debug( 'setAgent ' + setAgent )
    phoneHome.configSet('development','manifest', newManifest )
    return

def disable():
    
    phoneHome.htmlHeader()
    print '<body>'
    print "<h1>phDev Menu</h1><br><br>";
    print '<table style="width:100px" id="menu">'
    phoneHome.configRemove('development', 'manifest')
    print '<tr><td>phDev Functionality has been disabled</td></tr>' 
    print '<tr><form action="/cgi-bin/phMan.py" method="post" target="_self">'
    print '<td width="100" align="center"> <input type="hidden" name="function" value="">'
    print '<input type="submit" value="OK"  class="menu"/></td></tr>'
    print '</form>'
    
    print '</table>'
    return    
    
#############################################
#
#   Here are the code proper starts
#
#############################################


if phoneHome.testDbExists():
    log.debug('')
    log.debug('phDev Starts')
    # Create instance of FieldStorage 
    form = cgi.FieldStorage() 
    
    # Get data from fields
    function = form.getvalue('function')
    log.debug('function = ' + str(function))
    newManifest = form.getvalue('newManifest')
    log.debug('newManifest = ' + str(newManifest))

    if function == 'setAgent' :
        setAgent(newManifest)
        showMenu(newManifest)
    elif phoneHome.configOptionExists('development', 'manifest'):
        manifest = phoneHome.configGet('development', 'manifest')
        if function == 'reloadAgent' :
            reloadAgent(manifest)
            showMenu(manifest)
        elif function == 'reloadAllAgents':
            doReloadAllAgents()
        elif function == 'selectAgent' :
            selectAgent()
        elif function == 'disable' :
            disable()
        else:
            showMenu(manifest)
    else:
        selectAgent()        
else:
    dbMissing()
