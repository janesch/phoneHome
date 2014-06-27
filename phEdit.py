#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
File: phEdit.py

This script provide some of the tools to edit manifests
for NGAR MDS
It requires module library modPh.py together with other
'standard' modules

Ver     Date        Author      Desc
0.00    20140411    Chris Janes Original Development
"""
#############################################
#
#   Here we import modules required
#
#############################################
import sys
sys.path.append('/var/lib/phoneHome/lib')
# enable debugging
import cgitb
import cgi
import ConfigParser
import datetime
import logging
import os
import re

from modPh import modPh

#############################################
#
#   Here we st up our enviroment
#
#############################################

phoneHome = modPh()

cgitb.enable()
cgitb.enable()
log = logging.getLogger('phEdit')
logfile = phoneHome.logLoc + 'phEdit.log'
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

def pageDisplay(manifest):
    """ This function displays a manifest and allows some editing
    
    Arguments:
    manifest    The manifest to be displayed/edited
    Returns:
    None
    This function creates a webpage that displays each element of a manifest ordered
    by sequence. Each element can be moved within the manifest or deleted. Additional
    elements can be added to the manifest and the MA can be requested to re-read it's
    manifest
    """
    log.info('pageDisplay  ' + manifest)
    phoneHome.pageHeader('Phonehome Edit Manifest')
    print "<h1>" + manifest + "</h1><br><br>";
    print '<table id="editManifest">'
    if manifest == 'NONE':
        print '<tr><td></td></tr>'
        print '<tr><td>No manifest selected</td></tr>'
        print '<tr><td></td></tr>'
        print '<tr><form action="/cgi-bin/phMan.py" method="post" target="_self">'
        print '<input type="hidden" name="function" value="edit">'
        print '<td width="100" align="center"> <input type="submit" value="Continue" class="menu"/></td></tr>'
        print '</form>'
        print '</table>'
    else:
        Elements = phoneHome.getElements(manifest)
        lenElements = len(Elements)
        for element in Elements:
            
            print '<tr><td>' + str(element[0]) + '</td><td>' + element[1] + '</td>'
            print '<td>'
            phoneHome.newForm('/cgi-bin/phEdit.py')
            #print '<td><form action="/cgi-bin/phEdit.py" method="post" target="_self">'
            print '<input type="hidden" name="sequence" value="' + str(element[0]) + '">'
            print '<input type="hidden" name="manifest" value="' + manifest + '">'
            phoneHome.btnSubmit('UP', 'UP')
            #print '<input type="hidden" name="function" value="UP">'
            #print '<input type="submit" value="UP">'
            #print '</form></td>'
            
            print '<td>'
            phoneHome.newForm('/cgi-bin/phEdit.py')
            #print '<td><form action="/cgi-bin/phEdit.py" method="post" target="_self">'
            print '<input type="hidden" name="sequence" value="' + str(element[0]) + '">'
            print '<input type="hidden" name="manifest" value="' + manifest + '">'
            #print '<input type="hidden" name="function" value="DOWN">'
            phoneHome.btnSubmit('DOWN', 'DOWN')
            #print '<input type="submit" value="DOWN">'
            #print '</form></td>'
             
            print '<td>'
            phoneHome.newForm('/cgi-bin/phEdit.py')
            #print '<td><form action="/cgi-bin/phEdit.py" method="post" target="_self">'
            print '<input type="hidden" name="sequence" value="' + str(element[0]) + '">'
            print '<input type="hidden" name="manifest" value="' + manifest + '">'
            phoneHome.btnSubmit('DELETE', 'DELETE')
            #print '<input type="hidden" name="function" value="DELETE">'
            #print '<input type="submit" value="DEL">'
            #print '</form></td>'
            print '</tr>'
        print '</table>'
        print '<table id="editManifest">'
        print '<td><form action="/cgi-bin/phEdit.py" method="post" target="_self">'
        print '<input type="hidden" name="function" value="INSERT">'
        print '<input type="hidden" name="manifest" value="' + manifest + '">'
        print '<input type="submit" value="Insert New Element">'
        print '</form></td>'
        print '<td><form action="/cgi-bin/phEdit.py" method="post" target="_self">'
        print '<input type="hidden" name="function" value="RESTART">'
        print '<input type="hidden" name="manifest" value="' + manifest + '">'
        print '<input type="submit" value="Restart Agent">'
        print '</form></td>'
        print '<td><form action="/cgi-bin/phMan.py" method="post" target="_self">'
        print '<input type="hidden" name="function" value="">'
        print '<input type="submit" value="Finish">'
        print '</form></td>'
        print '</tr>'
        print '</table>'

def selectElement(manifest):
    """ This function displays a list of available manifest element to be selected
    
    Arguments:
    manifest    The manifest to be displayed/edited
    Returns:
    None
    This function lists all available manifest elements grouped by element type. It allows you
    to select one (radio button) to be added to the manifest
    """
    log.info('selectElement  ' + manifest)
    phoneHome.pageHeader('Phonehome Edit Manifest - Insert Element')
    phoneHome.newForm('/cgi-bin/phEdit.py')
    #print '<form action="/cgi-bin/phEdit.py" method="post" target="_self">'

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
    print '<input type="hidden" name="manifest" value="' + manifest + '">'
    phoneHome.btnSubmit('doInsert', 'Insert')
    phoneHome.btnCancel('/cgi-bin/phEdit.py')
    print '</tr>'
    print '</table>'
    

def insertElement(manifest, element):
    """This function inserts an element into a manifest
    
    Arguments:
    manifest    the name of the manifest to which the element is to be added
    element     the name of the element to be added to the manifest
    Returns:
    None
    This function inserts an element into a manifest dependent upo the type
    of element it is. When compplete it caused the edit manifest page to be
    refreshed.
    """
    log.info('insertElement  ' + manifest + '  ' + element)
    if re.match('man_user_', element, flags=0):
        Type = 'user'
    elif re.match('man_act_', element, flags=0):
        Type = 'action'
    elif re.match('man_conf_', element, flags=0):
        Type = 'config'
    else:
        Type = 'other'
    sequence = phoneHome.getNextSequence(manifest, Type)
    log.debug('sequence = ' + str(sequence))
    phoneHome.insertElement(manifest, sequence, element)
    pageDisplay(manifest)

def moveElementUp(manifest, sequence):
    """ This function move an element Up (next lowest sequence) in a manifest
    
    Arguments:
    manifest    the name of the manifest to which the element is to be added
    element     the name of the element to be added to the manifest
    Returns:
    None
    This function will move an element up in the order of processing (lower
    sequence number) by swapping with the element immeadialy above it.
    """
    log.info('moveElementUp   ' + manifest + '  ' + str(sequence))
    swapSequence = phoneHome.getSeqLess(manifest, sequence)
    element = phoneHome.getElement(manifest, sequence)
    swapElement = phoneHome.getElement(manifest, swapSequence)
    phoneHome.updateElement(manifest, sequence, swapElement)
    phoneHome.updateElement(manifest, swapSequence, element)
    pageDisplay(manifest)

def moveElementDown(manifest, sequence):
    """ This function move an element Down (next highest sequence) in a manifest
    
    Arguments:
    manifest    the name of the manifest to which the element is to be added
    element     the name of the element to be added to the manifest
    Returns:
    None
    This function will move an element up in the order of processing (higher
    sequence number) by swapping with the element immeadialy below it.
    """
    log.info('moveElementDown  ' + manifest + '  ' + str(sequence))
    swapSequence = phoneHome.getSeqGreater(manifest, sequence)
    element = phoneHome.getElement(manifest, sequence)
    swapElement = phoneHome.getElement(manifest, swapSequence)
    phoneHome.updateElement(manifest, sequence, swapElement)
    phoneHome.updateElement(manifest, swapSequence, element)
    pageDisplay(manifest)

def newManifest():
    log.info('newManifest  ')
    phoneHome.pageHeader('Phonehome Create Manifest - Select Name')
    print '<table>'
    print '<tr><td>Enter Name for New Manifest</td>'
    phoneHome.newForm('/cgi-bin/phEdit.py')
    #print '<td><form action="/cgi-bin/phEdit.py" method="post" target="_self">'
    print '<input type="text" name="manifest"></td></tr>'
    phoneHome.btnSubmit('CREATE', 'Insert')
    #print '<input type="hidden" name="function" value="CREATE"'
    #print '<tr><td><input type="submit" value="Insert" /></td>'
    phoneHome.btnCancel('/cgi-bin/phMan.py')
    #print '<td><input type="reset" value="Reset" /></td>'
    print '</tr></table>'


def createManifest(manifest):
    log.info('createManifest  ' + manifest)
    if phoneHome.checkManifest(manifest) == 0:
        selectElement(manifest)
    else:
        log.debug('selectElement  ' + manifest)
        print "Content-type: text/html\r\n\r\n";
        phoneHome.pageHeader('Phonehome Edit Manifest - Insert Element')
        print '<table>'
        print '<tr><td>Manifest Exists</td>'
        print '<td><form action="/cgi-bin/phEdit.py" method="post" target="_self"> <input type="text" name="manifest"></td></tr>'
        print '<input type="hidden" name="function" value="INSERT"'
        print '<tr><td><input type="submit" value="Continue" /></td></tr>'
        print '</form></table>'        

def restartAgent(manifest):            
    log.info('restartAgent  ' + manifest)
    phoneHome.pageHeader('Phonehome Restart Agent')
    print "<h1>" + manifest + "</h1><br><br>";
    print '<table id="manifest">'
    host = manifest + ':9080'
    phoneHome.agentCheck(host , 'admin', 'admin')
    print '<tr><td> ma.aapi.rpc_check issued to ' + manifest + '</td></tr>'
    print '<td><form action="/cgi-bin/phMan.py" method="post" target="_self">'
    print '<input type="hidden" name="function" value="">'
    print '<input type="submit" value="Continue">'
    print '</form></td></tr>'
    print '</table>'


    
#############################################
#
#   Here are the code proper starts
#
#############################################


# Create instance of FieldStorage 
form = cgi.FieldStorage() 
phoneHome = modPh()
log.debug('Version = ' + phoneHome.manifestVer )

function = form.getvalue('function')
log.debug('function = ' + str(function))

manifest = str(form.getvalue('manifest'))
manifest = manifest.upper()
log.debug('manifest = ' + manifest)

sequence = form.getvalue('sequence')
log.debug('sequence = ' + str(sequence))

element = form.getvalue('element')
log.debug('element = ' + str(element))
# Get data from fields

if function == 'DELETE' :
    log.debug('phoneHome.deleteElement  ' + manifest + ' ' + sequence )
    phoneHome.deleteElement(manifest, sequence)
    pageDisplay(manifest)
elif function == 'INSERT':
    selectElement(manifest)
    #log.debug('phoneHome.insertElement  ' + manifest )
elif function == 'doInsert':
    insertElement(manifest, element)
    #log.debug('phoneHome.insertElement  ' + manifest )
elif function == 'UP':
    moveElementUp(manifest, sequence)
elif function == 'DOWN':
    moveElementDown(manifest, sequence)
elif function == 'CREATE':
    createManifest(manifest)
elif function == 'new':
    newManifest()
elif function == 'RESTART':
    restartAgent(manifest)
else:
    pageDisplay(manifest)
