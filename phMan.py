#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
File: phMan.py

This script provide some of the management for NGAR MDS
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

def saveManifest(fileName):
    """
    This  function creates backups of the manifest DB
    
    Arguments:
        None
    Return:
        Message on webpage
    This function produces a csv file in a location defined in the phoneHome config file (backups - backuploc)
    The file name is based upon the Date/Time that thebackup was created with a suffix defined in the phoneHome
    config file (backups - backuploc) 
    """
    log.debug('saveManifest')
    phoneHome.pageHeader('')
    datestring = "{year}_{month}_{day}_{hour}_{minute}_{second}".format(year=now.year, month=now.month, day=now.day, hour=now.hour, minute=now.minute, second=now.second)
    shortfilename = datestring + phoneHome.backupSuffix
    filename = phoneHome.backupLoc + shortfilename
    print '<table id="files">'
    print '<tr><td>'

    if phoneHome.manSave(filename):
        print 'FileName is {FILE}<BR>'.format(FILE=shortfilename)
        print 'Manifests Backed up'
    else:
        print 'No Manifests found'
    print '</td></tr> '
    print '<tr><td><br>'
    print '</td></tr> '
    print '<tr>'
    phoneHome.btnOK('/cgi-bin/phMan.py')
    print '</tr> '
    print '</table>'
    print '</body>'
    return

def selectRestoreManifest():
    """
    This  function restores the manifest DB from a backup file
    
    Arguments:
        None
    Return:
        Message on webpage
    This function uses a csv file in a location defined in the phoneHome config file (backups - backuploc)
    The file name will have a suffix defined in the phoneHome config file (backups - backuploc) 
    """
    log.debug('selectRestoreManifest')
    phoneHome.pageHeader('')    
    backupFiles = phoneHome.listBackupFiles()
    print '<table id="files">'
    for file in backupFiles:
        print '<tr><td><button>' + file + '</button></td>'
        print '<td>'
        phoneHome.newForm('/cgi-bin/phMan.py')
        print '<input type="hidden" name="fileName" value="' + file + '">'
        phoneHome.btnSubmit('restoreFromBackup', 'RESTORE')
        if re.match('Backup', file, flags=0):
            print '<td></td>'
        else:
            print '<td>'
            phoneHome.newForm('/cgi-bin/phMan.py')
            print '<input type="hidden" name="fileName" value="' + file + '">'
            phoneHome.btnSubmit('deleteBackup', 'DELETE')

        print '</tr>'
    print '<tr>'
    phoneHome.btnCancel('/cgi-bin/phMan.py')
    print '</tr>'
    print '</table>'
    return

def deleteBackupFile(fileName):
    log.debug('deleteBackupFile')
    phoneHome.pageHeader('')
    print '<table id="files">'
    print '<tr><td>'
    if phoneHome.delBackupFile(fileName):
        print 'FileName is {FILE}<BR>'.format(FILE=fileName)
        print 'File Deleted '
    else:
        print 'FileName is {FILE}<BR>'.format(FILE=fileName)
        print 'Delete Failed'
    print '</td></tr> '
    print '<tr><td><br>'
    print '</td></tr> '
    print '<tr>'
    phoneHome.button('/cgi-bin/phMan.py', '', 'Menu')
    print '</tr> '
    print '</table>'
    return    
    
    
def restoreManifest(filename):
    log.debug('restoreManifest')
    phoneHome.pageHeader('')
    LongFileName = phoneHome.backupLoc + filename
    log.debug('LongFileName = ' + LongFileName)

    print '<table id="files">'
    print '<tr><td>'
    if phoneHome.manRestore(LongFileName):
        print 'FileName is {FILE}<BR>'.format(FILE=filename)
        print 'Restore Complete'
    else:
        print 'FileName is {FILE}<BR>'.format(FILE=filename)
        print 'Restore Failed'
    print '</td></tr> '
    print '<tr><td><br>'
    print '</td></tr> '
    print '<tr>'
    phoneHome.button('/cgi-bin/phMan.py', '', 'Menu')
    print '</tr> '
    print '</table>'

    return

def showMenu():
    """
    This function provide a menu for the UI
    """
    log.debug('showMenu')
    phoneHome.pageHeader('Phonehome Management Menu')
    print '<table style="width:100px" id="menu">'
     
    print '<tr>'
    phoneHome.newForm('/cgi-bin/phEdit.py')
    phoneHome.btnSubmit('new','Create Manifest')
    print '</tr>'
    
    print '<tr>'
    phoneHome.newForm('/cgi-bin/phMan.py')
    phoneHome.btnSubmit('edit','Edit Manifest')
    print '</tr>'
    
    print '<tr>'
    phoneHome.newForm('/cgi-bin/phMan.py')
    phoneHome.btnSubmit('viewManifest','View Manifest')
    print '</tr>'
    
    print '<tr>'
    phoneHome.newForm('/cgi-bin/phMan.py')
    phoneHome.btnSubmit('prepCopy','Copy a Manifest')
    print '</tr>'
    
    print '<tr>'
    phoneHome.newForm('/cgi-bin/phMan.py')
    phoneHome.btnSubmit('prepDel','Delete a Manifest')
    print '</tr>'
    
    print '<tr>'
    phoneHome.newForm('/cgi-bin/phMan.py')
    phoneHome.btnSubmit('','Import Manifest')
    print '</tr>'
    
    print '<tr>'
    phoneHome.newForm('/cgi-bin/phMan.py')
    phoneHome.btnSubmit('backup','Create Backup')
    print '</tr>'
    
    print '<tr>'
    phoneHome.newForm('/cgi-bin/phMan.py')
    phoneHome.btnSubmit('restore','Manage Backups')
    print '</tr>'
    
    print '<tr>'
    phoneHome.newForm('/cgi-bin/phMan.py')
    phoneHome.btnSubmit('importFrag','Import Fragment')
    print '</tr>'
    
    print '<tr>'
    phoneHome.newForm('/cgi-bin/phMan.py')
    phoneHome.btnSubmit('selectViewFrag','View Fragment')
    print '</tr>'
    
    print '<tr>'
    phoneHome.newForm('/cgi-bin/phMan.py')
    phoneHome.btnSubmit('environ','Environment')
    print '</tr>'

    print '</table>'
    return

def showEnviron():
    """
    Function produces a webpage showing the Environment that the webservice runs in
    """
    log.debug( 'showEnviron' )
    phoneHome.pageHeader('Phonehome Management Environment')
    print '<table>'
    for param in os.environ.keys():
#      print "<b>%20s</b>: %s<br>" % (param, os.environ[param])
        print "<tr><td>%20s<</td><td>%s</td></tr>" % (param, os.environ[param])
    print '</table>'
    phoneHome.btnOK('/cgi-bin/phMan.py')


def prepCopy():
    log.debug('prepCopy')
    phoneHome.pageHeader('')
    array = phoneHome.listManifests()
    lenArray = len(array)
    array.sort()
    print '<table style="width:800px" id="manifest" >'
    print '<form action="/cgi-bin/phMan.py" method="post" target="_self">'
    
    colwidth = (800 / int(phoneHome.colManifest)) - 10
    count = 0
    for data in array:
        if count == 0:
            print '<tr>'
        phoneHome.radio('Manifest', data, colwidth)
        count = count + 1
        if count == int(phoneHome.colManifest):
            count = 0
            print '</tr>'
    print '</table><br><br>'
    
    print '<table id="chris">'
    print '<tr><td>New Manifest</td><td><input type="text" name="NewManifest" size="25" ></td></tr>'
    print '<tr><td></td><td></td></tr>'

    print '<tr><td><input type="hidden" name="function" value="Copy"><input type="submit" value="Copy" /></td>'
    print '</form>'
    phoneHome.btnCancel('/cgi-bin/phMan.py', )
    print '</tr>'
    print '</table>'
    
    
def doCopy(ExistingManifest, NewManifest):
    log.debug('doCopy')
    phoneHome.pageHeader('')
    print '<center><table>'
    print '<form action="/cgi-bin/phMan.py" method="post" target="_self">'
    print '<tr><td></td><td></td></tr>'
    
    try:
        ExistingManifest = ExistingManifest.strip()
        NewManifest = NewManifest.strip()
        phoneHome.copyManifest(str(ExistingManifest), str(NewManifest))
        log.debug( 'Copied Manifest ' + str(ExistingManifest) + ' to ' + str(NewManifest) )
        print '<tr><td>Manifest copied</td><td></td></tr>'
    except:
        log.debug( 'Failed to Copied Manifest ' + str(ExistingManifest) + ' to ' + str(NewManifest) )
        print '<tr><td>Fail to Copy Manifest</td><td></td></tr>'

    print '<tr>'
    phoneHome.btnOK('/cgi-bin/phMan.py')
    print '</tr>'
    print '</table>'

def prepDel():
    log.debug( 'prepDel' )
    phoneHome.pageHeader('Delete a Manifest')
    array = phoneHome.listManifests()
    lenArray = len(array)
    array.sort()
    print '<table style="width:800px">'
    print '<form action="/cgi-bin/phMan.py" method="post" target="_self">'

    colwidth = (800 / int(phoneHome.colManifest)) - 10
    count = 0
    for data in array:
        if count == 0:
            print '<tr>'
        phoneHome.radio('Manifest', data, colwidth)
        count = count + 1
        if count == int(phoneHome.colManifest):
            count = 0
            print '</tr>'

    print '<tr>'
    print'<td><input type="hidden" name="function" value="Delete"</td><td><input type="submit" value="Delete" />'
    print '</form>'
    phoneHome.btnCancel('/cgi-bin/phMan.py')
    print '</tr>'
    print '</form>'
    print '</table>'

    
def doDelete(ExistingManifest):
    log.debug( 'doDelete' )
    phoneHome.pageHeader('Manifest ' + ExistingManifest + ' Deleted')
    print '<table style="width:100px" id="menu">'
    print '<tr><td></td><td></td></tr>'
    try:
        ExistingManifest = ExistingManifest.strip()
        phoneHome.deleteManifest(ExistingManifest)
        log.debug( 'Deleted Manifest ' + str(ExistingManifest))
    except:
        log.debug( 'Delete Manifest Failed ' + str(ExistingManifest))
        print '<tr><td>Delete Failed</td><td></td></tr>'
    print '<tr>'
    phoneHome.btnOK('/cgi-bin/phMan.py')
    print '</tr>'
    print '</table>'


def editManifest():
    log.debug( 'editManifest' )
    phoneHome.pageHeader('Select Manifest to Edit')
    array = phoneHome.listManifests()
    lenArray = len(array)
    array.sort()
    print '<table style="width:800px" id="manifest" >'
    print '<form action="/cgi-bin/phEdit.py" method="post" target="_self">'
    colwidth = (800 / int(phoneHome.colManifest)) - 10
    count = 0
    for data in array:
        if count == 0:
            print '<tr>'
        #print '<td width="' + str(colwidth) + '" align="right">' + data + '</td><td width="10"><input type="phoneHome.radio" name="manifest" value="' + data + '"></td>'
        phoneHome.radio('manifest', data, colwidth)
        count = count + 1
        if count == int(phoneHome.colManifest):
            count = 0
            print '</tr>'
    print '</table>'
    print '<table id="chris">'
    phoneHome.btnSubmit('Copy', 'Edit')
    #print '<tr><td><input type="hidden" name="function" value="Copy"</td><td><input type="submit" value="Edit" />'
    print '</form>'
    phoneHome.btnCancel('/cgi-bin/phMan.py')
    print '</tr>'
    print '</table>'
    
def uploadFrag():
    log.debug( 'uploadFrag' )
    phoneHome.pageHeader('')

 
def saveFrag(fileItem,fileName):
    log.debug( 'saveFrag' )
    phoneHome.pageHeader('')



def dbMissing():
    """
    Tests that the DB is available
    """
    log.debug( 'dbMissing' )
    phoneHome.pageHeader('Phonehome - Database not available')
    print '<table id="files">'
    print '<tr><td>DB not available - please refer to your sys admin</td></tr>'
    print '</table>'
    




def selectElementView():
    log.info('selectElementView  ' )
    phoneHome.pageHeader('Select Element to View')
    print '<form action="/cgi-bin/phMan.py" method="post" target="_self">'

    print '<br>User Elements'
    print '</td></tr><table border="1">'
    UserFrags = phoneHome.listUserFrags()
    Count = 0
    for userFrag in UserFrags:
        if Count == 0:
            print '<tr>'
        phoneHome.radio('element', userFrag, '250')
        Count = Count + 1
        if Count == 4:
            print '</tr>'
            Count = 0
    print '</table>'

    print '<br>Action Elements'
    print '</td></tr><table border="1">'
    ActionFrags = phoneHome.listActionFrags()
    Count = 0
    for actionFrag in ActionFrags:
        if Count == 0:
            print '<tr>'
        phoneHome.radio('element', actionFrag, '250')
        Count = Count + 1
        if Count == 4:
            print '</tr>'
            Count = 0
    print '</table>'

    print '<br>Config Elements'
    print '</td></tr><table border="1">'
    ConfigFrags = phoneHome.listConfigFrags()
    Count = 0
    for ConfigFrag in ConfigFrags:
        if Count == 0:
            print '<tr>'
        phoneHome.radio('element', ConfigFrag, '250')
        Count = Count + 1
        if Count == 4:
            print '</tr>'
            Count = 0
    print '</table>'
    
    print '<br>Component Elements'
    print '</td></tr><table border="1">'
    ComponentFrags = phoneHome.listComponentFrags()
    Count = 0
    for componentFrag in ComponentFrags:
        if Count == 0:
            print '<tr>'
        phoneHome.radio('element', componentFrag, '250')
        Count = Count + 1
        if Count == 4:
            print '</tr>'
            Count = 0
    print '</table>'

    print '<table>'
    print '<tr>'
    print '<td>'
    print '<input type="hidden" name="function" value="viewElement">'
    print '<input type="submit" value="View" /></td>'
    print '</form>'
    phoneHome.btnCancel('/cgi-bin/phMan.py')
    print '</form></td></tr>'

    print '</table>'


def viewElement(element):
    log.info('viewElement  ' )
    phoneHome.printElement(element)

def viewManifest():
    """
    Provises a list of manifests that can be selected to view
    """
    log.debug( 'viewManifest' )
    array = phoneHome.listManifests()
    lenArray = len(array)
    array.sort()
    phoneHome.pageHeader('Phonehome View a Manifest')
    print '<table style="width:800px">'
    print '<form action="/cgi-bin/phoneHome.py" method="post" target="viewManifest">'
    colwidth = (800 / int(phoneHome.colManifest)) - 10
    count = 0
    for data in array:
        if count == 0:
            print '<tr>'
        #print '<td width="' + str(colwidth) + '" align="right">' + data + '</td><td width="10"><input type="phoneHome.radio" name="fqdn" value="' + data + '"></td>'
        phoneHome.radio('fqdn', data, colwidth)
        count = count + 1
        if count == int(phoneHome.colManifest):
            count = 0
            print '</tr>'
    phoneHome.btnSubmit('View', 'View')
    #print '<tr><td><input type="hidden" name="function" value="View"</td><td><input type="submit" value="View" />'
    #print '</form>'
    #print '</form>'
    #print '<form action="/cgi-bin/phMan.py" method="post" target="_self">'
    #print '<td><input type="hidden" name="function" value=""</td><td><input type="submit" value="Cancel" /></td>'
    phoneHome.btnCancel('/cgi-bin/phMan.py')
    print '</tr>'
    print '</form>'
    print '</table>'
    
  
    
    
    
    
#############################################
#
#   Here are the code proper starts
#
#############################################


if phoneHome.testDbExists():

    # Create instance of FieldStorage 
    form = cgi.FieldStorage() 
    
    # Get data from fields
    function = form.getvalue('function')
    log.debug('function = ' + str(function))
    fileName = form.getvalue('fileName')
    log.debug('fileName = ' + str(fileName))
    fileItem = form.getvalue('fileItem')
    log.debug('fileName = ' + str(fileItem))
    ExistingManifest = form.getvalue('Manifest')
    log.debug('ExistingManifest = ' + str(ExistingManifest))
    NewManifest = form.getvalue('NewManifest')
    log.debug('NewManifest = ' + str(NewManifest))
    Element = form.getvalue('element')
    log.debug('Element = ' + str(Element))
    
    
    
    
    if function == 'backup' :
        saveManifest(fileName)
    elif function == 'restore' :
        selectRestoreManifest()
    elif function == 'restoreFromBackup':
        restoreManifest(fileName)
    elif function == 'deleteBackup':
        deleteBackupFile(fileName)
    elif function == 'importFrag':
        uploadFrag()
    elif function == 'saveFrag':
        saveFrag(fileItem,fileName)
    elif function == 'environ' :
        showEnviron()
    elif function == 'prepCopy' :
        prepCopy()
    elif function == 'Copy' :
        doCopy(ExistingManifest, NewManifest.upper())
    elif function == 'prepDel' :
        prepDel()
    elif function == 'Delete' :
        doDelete(ExistingManifest)
    elif function == 'menu' :
        showMenu()
    elif function == 'viewManifest' :
        viewManifest()
    elif function == 'edit' :
        editManifest()
    elif function == 'selectViewFrag' :
        selectElementView()
    elif function == 'viewElement' :
        viewElement(Element)
    else:
        showMenu()
else:
    dbMissing()
