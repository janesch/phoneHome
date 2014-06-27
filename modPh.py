""" modPH a library of functions used by phoneHome

0.00    20140105    Chris Janes     original
0.10    20140310    Chris Janes     testDbExists added
                                    modPh.manifestUrl added to __init__, manElement, manDefaultElements
0.20    20140321    Chris Janes     agentCheck added
0.30    20140408    Chris Janes     mysql support added
"""

import sys
sys.path.append('/opt/abilisoft.com/asagent/share/')
#sys.path.insert(0,'/opt/abilisoft.com/asagent/share/asagent.pyz')
import ConfigParser
import os
# Comment out any db's you dont want to support - see getconn as well 
import sqlite3
#import psycopg2
#import MySQLdb
#import DB2
import re
import datetime
import subprocess
import socket
#from asagent import maql

class modPh:
    """
    A collection of functions to be used with the Manifest server (phoneHome).
    
    These functions are designed to work with a configuration file (see var configFile) that
    sets various CI
    """

    dbname = ''
    user = ''
    host = ''
    password = ''
    connectString = ''
    manifestLoc = ''
    configFile = '/var/lib/phoneHome/phoneHome.conf'
#    configFile = 'phoneHome.conf'
    version = '0.10'
    
    def __init__(self):
        """ This gets various variables from the config file
        
        Arguments:
        None
        Returns:
        None
        """
        config = ConfigParser.ConfigParser()
        config.readfp(open(modPh.configFile)) 
        modPh.dbtype= config.get('database', 'type')
        modPh.dbname= config.get('database', 'dbname')
        modPh.user= config.get('database', 'user')
        modPh.host= config.get('database', 'host')
        modPh.password= config.get('database', 'password')
        modPh.dbLocation = config.get('database', 'location')
        modPh.manifestLoc = config.get('phoneHome','manifestLoc')
        modPh.logLoc = config.get('phoneHome','logLoc')
        modPh.manifestVer = config.get('phoneHome','version')
        modPh.manifestUrl = config.get('phoneHome','manifestUrl')
        modPh.colManifest = config.get('phoneHome','colManifest')
        if modPh.dbtype == 'postgresql':
            modPh.connectString = "dbname='" + modPh.dbname + "' user='" + modPh.user + "' host='" + modPh.host + "' password='" + modPh.password + "'"
        elif modPh.dbtype == 'mysql':
            modPh.connectString = "db='" + modPh.dbname + "' user='" + modPh.user + "' host='" + modPh.host + "' passwd='" + modPh.password + "'"
        else:
            modPh.connectString = 'DB not suppported'
            
        modPh.numberBackups = config.get('backups','numberBackups')
        modPh.backupLoc = config.get('backups','backupLoc')
        modPh.backupPrefix = config.get('backups','backupPrefix')
        modPh.backupSuffix = config.get('backups','backupSuffix')
        #Added for Dynamic Manifests
        #oracle 
        modPh.oratabloc = config.get('oramon','oratabloc')
        modPh.oratabfile = modPh.oratabloc + 'oratab'
        modPh.oratabupdate = config.get('oramon','lastupdate')
        #webmon
        modPh.websourceloc = config.get('webmon','sourceloc')
        modPh.websourcefilename = config.get('webmon','sourcefile')
        modPh.websourcefile = modPh.websourceloc + modPh.websourcefilename
        modPh.webmonupdate = config.get('webmon','lastupdate')
        

    def getconn(self):
        """ This makes a connection to the relevent DB
        
        Arguments:
        None
        element     this is the name of the include file used
        Return:
        
        I gets the type of db from phoneHome.conf and constructs an
        appropriate connection string (where appropriate)
        Comment out any DB that you are not going to support
        """
        if modPh.dbtype == 'default':
            raise ConnectFailed('There is no default DB')
        elif modPh.dbtype == 'sqlite':
            try:
                modPh.connectString = modPh.dbLocation + modPh.dbname + '.db'
                conn = sqlite3.connect(modPh.connectString)
            except:
                raise ConnectFailed('Connection to sqlite db failed')
                
        elif modPh.dbtype == 'postgresql':
            try:
                modPh.connectString = "dbname='" + modPh.dbname + "' user='" + modPh.user + "' host='" + modPh.host + "' password='" + modPh.password + "'"
                conn =psycopg2.connect(modPh.connectString)
            except:
                raise ConnectFailed('Connection to postgresql db failed')
                
        elif modPh.dbtype == 'mysql': 
            try:
                conn = MySQLdb.connect(modPh.host , modPh.user, modPh.password, modPh.dbname)
            except:
                raise ConnectFailed('Connection to mysql db failed')
        #elif modPh.dbtype == 'DB2':
        #    try:
        #        modPh.connectString = "dsn='" + modPh.dbname + "', uid='" + modPh.user + "', pwd='" + modPh.password + "'"
        #        conn = DB2.connect(modPh.connectString)
        #    except:
        #        raise ConnectFailed('Connection to DB2 db failed')
        else:
            raise ConnectFailed('DB not suppported')
        return conn

    def insertElement(self, manifest, sequence, element):
        """ This inserts an element into a manifest
        
        Arguments:
        manifest    this is a list of include files that make up a manifest
        sequence    This give the order that thinsertElemtn include files are presented in
                    the manifest
        element     this is the name of the include file used
        Return:
        returns an 1 if successful and a 0 if not
        No checking is done to see if this element already exists, if it does
        exist then the DB will raise an exception and the element not added.
        """
        conn = self.getconn()
        try:
            cur = conn.cursor()
            query =  "INSERT INTO manifest (host, sequence, includefile) VALUES ('" + manifest.upper() + "', " + str(sequence) + ", '" + element + "');"
            cur.execute(query)
            conn.commit()
            conn.close()
            result = 1
        except:
            result = 0
        return result
    
    def checkElement(self, manifest, sequence):
        """ This function checks to see if an element already exists in a manifest
        
        Arguments:
        manifest    this is a list of include files that make up a manifest
        element     this is the name of the include file used
        Return:
        If this element exists then the function returns a 1 otherwise a 0 is returned
        """
        try:
            conn = self.getconn()
            cur = conn.cursor()
            query =  "select * from  manifest where host = '" + manifest + "' and sequence = " + str(sequence) + ";"
            cur.execute(query)
            array = cur.fetchall()
            lenArray = len(array)
            if lenArray == 1:
                return  1
            else:
                return 0
            
            comm.close()
        except:
            return 0

    def checkManifest(self, manifest):
        """ This function checks to see if an manifest already exists 
        
        Arguments:
        manifest    this is a list of include files that make up a manifest
        Return:
        If this manifest exists then the function returns a 1 otherwise a 0 is returned
        """
        try:
            conn = self.getconn()
            cur = conn.cursor()
            query =  "select * from  manifest where host = '" + manifest + "';"
            cur.execute(query)
            array = cur.fetchall()
            lenArray = len(array)
            if lenArray > 0:
                return  1
            else:
                return 0
            
            comm.close()
        except:
            return 0
              
    def getElement(self, manifest, sequence):
        """ this returns the element from a given manifest and sequence
 
        Arguments:
        manifest    this is a list of include files that make up a manifest
        sequence    This give the order that the include files are presented in
            the manifest
        Return:
        A string containing element, should the element not exist a 0 is returned
        """
        try:
            conn = self.getconn()
            cur = conn.cursor()
            query =  "select * from  manifest where host = '" + manifest + "' and sequence = " + str(sequence) + ";"
            cur.execute(query)
            array = cur.fetchall()
            lenArray = len(array)
            if lenArray == 1:
                line = array[0]
                return  line[2]
            else:
                return 0
            
            comm.close()
        except:
            return 0
        
    def swapElement(self, manifest, Sequence1, Sequence2):
        """ This functions swaps the position of 2 elements in manifest
        
        Arguments:
        manifest    this is a list of include files that make up a manifest
        Sequence1   the position of the first elemnet in the manifest
        Sequence2   the position of the second elemnet in the manifest
        Return:
        Note that the elements do not have to be adjacent. This returns
        a 1 of successful, and a 0 otherwise """

        try:
            Element1 = self.getElement(manifest, Sequence1)
            Element2 = self.getElement(manifest, Sequence2)
            self.updateElement(manifest, Sequence1, Element2)
            self.updateElement(manifest, Sequence2, Element1)
            return 1
        except:
            return 0
    
    
    def updateElement(self, manifest, sequence, element):
        """ this function changes the element for a given manifest/sequence
        
        Arguments:
        manifest    this is a list of include files that make up a manifest
        sequence    This give the order that the include files are presented in
            the manifest
        element     this is the name of the new include file to be used
        Return:
        returns a 1 if successfull. In all other cases a 0 is returned
        """
        try:
            conn = self.getconn()
            cur = conn.cursor()
            query =  "update manifest set includefile = '" + element + "' where host = '" + manifest + "' and sequence = " + str(sequence) + ";"
            cur.execute(query)
            conn.commit()
            return 1
            comm.close()
        except:
            return 0
        
    def deleteElement(self, manifest, sequence):
        """ this function deletes an element from the given manifest/sequence
        
        Arguments:
        manifest    this is a list of include files that make up a manifest
        sequence    This give the order that the include files are presented in
            the manifest
        element     this is the name of the include file used
        Return:
        Returns a 1 if successfull. In all other cases a 0 is returned
        """

        result = self.checkElement(manifest, sequence)
        if self.checkElement(manifest, sequence):
            try:
                conn = self.getconn()
                cur = conn.cursor()
                query =  "delete from manifest  where host = '" + manifest + "' and sequence = " + str(sequence) + ";"
                cur.execute(query)
                conn.commit()
                return 1
                comm.close()
            except:
                return 0
        else:
            return 0
    
    def getSeqGreater(self, manifest, sequence):
        """ This function returns the sequence of the element adjacent that has the higher value to the given element
        
        Arguments:
        manifest    this is a list of include files that make up a manifest
        element     this is the name of the include file used
        Return:
        Returns the value of the adjacent element or a 0 if there is no adjacent
            element
        """
        
        if self.checkElement(manifest, sequence):
            conn = self.getconn()
            cur = conn.cursor()
            query =  "select * from  manifest where host = '" + manifest + "' and sequence > " + str(sequence) + " order by sequence ASC;"
            cur.execute(query)
            array = cur.fetchall()
            lenArray = len(array)
            if lenArray > 0:
                record = array[0]
                return record[1]
            else:
                return 0
                
    def getSeqLess(self, manifest, sequence):
        """ This function returns the sequence of the element adjacent that has the lower value to the given element
        
        Arguments:
        manifest    this is a list of include files that make up a manifest
        element     this is the name of the include file used
        Return:
        Returns the vale of the adjacent element or a 0 if there is no adjacent
            element
        """
        if self.checkElement(manifest, sequence):
            conn = self.getconn()
            cur = conn.cursor()
            query =  "select * from  manifest where host = '" + manifest + "' and sequence < " + str(sequence) + " order by sequence DESC;"
            cur.execute(query)
            array = cur.fetchall()
            lenArray = len(array)
            if lenArray > 0:
                record = array[0]
                return record[1]
            else:
                return 0        
    
    def copyManifest(self, oldManifest, newManaifest):
        """ This function copies an existing manifest
        
        Arguments:
        oldManifest the name of the existing manifest
        newManifest the name of the new manifest to be created
        Return:
        Returns a 1 if successful and a 0 otherwise"""
        if self.checkManifest(newManaifest):
            return 0
        else:
            conn = self.getconn()
            cur = conn.cursor()
            query =  "select * from  manifest where host = '" + oldManifest + "' order by sequence ASC;"
            cur.execute(query)
            array = cur.fetchall()
            lenArray = len(array)
            if lenArray > 0:
                for line in array:
                    self.insertElement(newManaifest.upper(), line[1], line[2])
                return 1
            else:
                return 0
            
    def deleteManifest(self, manifest):
        """ this function deletes a manifest
        
        Arguments:
        manifest    the name of the manifest to be deleted
        Return:
        This function returns a 0 if successfull
        """
        result = self.checkManifest(manifest)
        if self.checkManifest(manifest):
            try:
                conn = self.getconn()
                cur = conn.cursor()
                query =  "delete from manifest  where host = '" + manifest + "';"
                cur.execute(query)
                conn.commit()
                comm.close()
                return 1
            except:
                return 0
        else:
            return 0
    
    def listManifests(self):
        """This function returns a list of manifests
        
        Arguments:
        None
        Return:
        Returns a list of manifests if successful or a 0 otherwise getconn
        """
        Manifests = []
        conn = self.getconn() 
        cur = conn.cursor()
        query =  "select distinct host from  manifest;"
        cur.execute(query)
        array = cur.fetchall()
        lenArray = len(array)
        if lenArray > 0:
            for line in array:
                Manifests.append(line[0])
            return Manifests
        else:
            return 0        

    def listBackupFiles(self):
        """ This function lists all the available Backup Files
        
        Arguments:
        None
        Return:
        Returns a list of all available backup files or 0 if none are avaialble
        """
        backupFiles = []
        pattern = modPh.backupSuffix + '$'
        for file in os.listdir(modPh.backupLoc):
            if re.search(pattern,file, flags=0):
                backupFiles.append(file)
        backupFiles.sort()
        return backupFiles


    def listFrags(self):
        """ This function lists all the available Manifest Fragments
        
        Arguments:
        None
        Return:
        Returns a list of all manifest fragments or 0 if none are avaialble
        """
        Fragments = []
        for file in os.listdir(modPh.manifestLoc):
            if re.search('xml$',file, flags=0):
                Fragments.append(file.rstrip('.xml'))
        Fragments.sort()
        return Fragments

    def listActionFrags(self):
        """ This function lists all the available Manifest Action Fragments
        
        Arguments:
        None
        Return:
        Returns a list of all manifest action fragments or 0 if none are
            avaialble
        """
        Fragments = []
        for file in os.listdir(modPh.manifestLoc):
            if re.search('man_act_.*xml$',file, flags=0):
                Fragments.append(file.rstrip('.xml'))
        Fragments.sort()
        return Fragments

    def listComponentFrags(self):
        """ This function lists all the available Manifest component Fragments
        
        Arguments:
        None
        Return:
        Returns a list of all manifest component fragments or 0 if none are
        avaialble
        """
        Fragments = []
        for file in os.listdir(modPh.manifestLoc):
            if re.search('man_comp_.*xml$',file, flags=0):
                Fragments.append(file.rstrip('.xml'))
        Fragments.sort()
        return Fragments

    def listConfigFrags(self):
        """ This function lists all the available Manifest Config Fragments
        
        Arguments:
        None
        Return:
        Returns a list of all manifest config fragments or 0 if none are
            avaialble
        """
        Fragments = []
        for file in os.listdir(modPh.manifestLoc):
            if re.search('man_conf_.*xml$',file, flags=0):
                Fragments.append(file.rstrip('.xml'))
        Fragments.sort()
        return Fragments

    def listUserFrags(self):
        """ This function lists all the available Manifest User Fragments
        
        Arguments:
        None
        Return:
        Returns a list of all manifest user fragments or 0 if none are avaialble
        """
        Fragments = []
        for file in os.listdir(modPh.manifestLoc):
            if re.search('man_user_.*xml$',file, flags=0):
                Fragments.append(file.rstrip('.xml'))
        Fragments.sort()
        return Fragments
    
    def getNextSequence(self, manifest, Type):
        """ This returns the next avaible sequence for a manifest
        
        Arguments:
        manifest    the name of the manifest from which you want the next avalable sequence
        Type        the type of element to be added 'user' 'action' 'component' 'config'
        Return:
        Returns the next sequence dependent on Type or a 0 should it fail
        """
        if Type == 'user':
            incType = 'man_user_'
            minSeq = 10
        elif Type == 'action':
            incType = 'man_act_'
            minSeq = 100
        elif Type == 'config':
            incType = 'man_conf_'
            minSeq = 1000
        else:
            incType = 'man_'
            minSeq = 2000
        conn = self.getconn()
        cur = conn.cursor()
        query =  "select max(sequence) from  manifest where host = '" + manifest + "' and includeFile like '" + incType + "%' ;"
        cur.execute(query)
        array = cur.fetchall()
        if array == [(None,)]:
            return minSeq
        else:
            record = array[0]
            result = record[0] + 10
            if int(result) < minSeq :
                return minSeq
            else:
                return result
        
    
    def manHeader(self, name):
        """ this prints the required manifest header

        Arguments:
        None
        Return:
        """
        now = datetime.datetime.utcnow()
        print 'Content-Type: text/xml'
        print ''
        print '<?xml version="1.0" encoding="utf-8"?> '
        print '<Manifest name="manifest.{name}"'.format(name=name)
        print '          updated="{year}/{month}/{day} {hour}:{minute}:{second}"'.format(year=now.year, month=now.month, day=now.day, hour=now.hour, minute=now.minute, second=now.second)
        print '          effectiveFrom="{year}/{month}/{day} {hour}:{minute}:{second}"'.format(year=now.year, month=now.month, day=now.day, hour=now.hour, minute=now.minute, second=now.second)
        print '          xmlns:xi="http://www.w3.org/2001/XInclude">'
        
    def manFooter(self):
        """ this prints the required manifest footer
        
        Arguments:
        """
        print '</Manifest>'
        
    def manElement(self, element):
        """this prints an manifest element
        
        Arguments:
        element the manifest element to be printed
        Return:
        """
        print '    <xi:include href="http:{URL}{IncludeFile}.xml"/>'.format(URL=modPh.manifestUrl, IncludeFile=element)
        
    def manDefaultElements(self):
        """ this will print the body of a default manifest
        
        Arguments:
        None
        Return:
        """
        print '    <!--    User Data   -->'
        print '     <xi:include href="http:{URL}man_user_admin_include.xml"/>'.format(URL=modPh.manifestUrl)
        print ''
        print '    <!--    Action Containers   -->'
        print ''
        print '    <xi:include href="http:{URL}man_act_trap_include.xml"/>'.format(URL=modPh.manifestUrl)
        print '    <xi:include href="http:{URL}man_act_hbtrap_include.xml"/>'.format(URL=modPh.manifestUrl)
        print '    <xi:include href="http:{URL}man_act_notify_include.xml"/>'.format(URL=modPh.manifestUrl)
        print '    <xi:include href="http:{URL}man_act_perf_include.xml"/>'.format(URL=modPh.manifestUrl)
        print ''
        print '    <!--    Config   -->'
        print ''
        print '    <xi:include href="http:{URL}man_conf_include.xml"/>'.format(URL=modPh.manifestUrl)
        print '    <xi:include href="http:{URL}man_conf_abilisoft.include.xml"/>'.format(URL=modPh.manifestUrl)
        print ''
        print '    <!--    Monitors    -->'
        print ''
        print '    <xi:include href="http:{URL}man_comp_general_include.xml"/>'.format(URL=modPh.manifestUrl)
        print '    <xi:include href="http:{URL}man_comp_abilisoft_include.xml"/>'.format(URL=modPh.manifestUrl)
        print ''

    def listElements(self, manifest):
        """ This function returns a list of elements in a manifest
        
        Arguments:
        manifest    the name of the manifest
        Return:
        Returns a list of elements for a manifest ordered by sequence
        """
        Elements = []
        if self.checkManifest(manifest):
            conn = self.getconn()
            cur = conn.cursor()
            query =  "select * from  manifest where host = '" + manifest + "' order by sequence ASC;"
            cur.execute(query)
            array = cur.fetchall()
            lenArray = len(array)
            if lenArray > 0:
                for line in array:
                    Elements.append(line[2])
                return Elements
            else:
                return 0
        else:            
            return 0
      
    def manManifest(self, manifest):
        """ This function prints a manifest
        
        Arguments:
        manifest    the name of the manifest to be delivered
        Return:
        """
        self.manHeader(manifest)
        if self.checkManifest(manifest):
            list = []
            list = self.listElements(manifest)
            for element in list:
                self.manElement(element)
        self.manFooter()
        return        

    def manDefault(self):
        """ This function prints (delivers) a default manifest
        
        Arguments:
        None
        Return:
        """
        self.manHeader('unknown')
        self.manDefaultElements()
        self.manFooter()
        
    def manSave(self, filename):
        """ this function saves all the manifests to a single file
        
        Arguments:
        filename    the name of the file that this function will save the information to
        Return:
        Returns 1 if successfull otherwise a 0
        this function saves all the manfests to a file in the format manifest,
        sequence, element
        """
        conn = self.getconn()
        cur = conn.cursor()
        query = "SELECT * FROM manifest  order by host, sequence;"
        cur.execute(query)
        array = cur.fetchall()
        lenArray = len(array)
        if lenArray == 0:
            return 0
        else:
            f = open(filename,'w')
            for row in array:
                f.write('{Host},{Sequence},{IncludeFile},'.format(Host=row[0], Sequence=row[1], IncludeFile=row[2]) + os.linesep)
            f.close()
            return 1
        
    def manRestore(self, filename):
        """ this function will restore the manifest server to a previous backup
        
        Arguments:
        filename    the name of the file that holds the backup to restore from
        Return:
        Returns 1 if successfull otherwise a 0
        this function will delete all the data from the manifest server before
        restoring from the backup
        """
        try:
            f = open(filename)
            lines = f.readlines()
            f.close()
            conn = self.getconn()
            cur = conn.cursor()
            query =  "delete from manifest ;"
            cur.execute(query)
            conn.commit()
            
            conn = self.getconn()
            cur = conn.cursor()
            for line in lines:
                data = line.split(',')
                query =  "INSERT INTO manifest (host, sequence, includefile) VALUES ('" + data[0] + "', " + data[1] + ", '" + data[2] + "');"
                cur.execute(query)        
            conn.commit()
            return 1
        except:
            return 0
    
    def delBackupFile(self, fileName):
        """ Deletes a backup file
        
        Arguments:
        fileName    the name of the backup file to be deleted
        Return:
        Returns 1 if successfull otherwise a 0
        """
        longFileName = modPh.backupLoc + fileName
        os.remove(longFileName)
        if os.path.isfile(longFileName) :
            return 0
        else:
            return 1
        
        
    def getElements(self, manifest):
        """ this function will return a list of sequences and elements  for a given manifest
        
        Arguments:
        manifest    this is a list of include files that make up a manifest
        sequence    This give the order that the include files are presented in the manifest
        element     this is the name of the include file used
        Return:
        Returns a list of seuences and element from the manifest specified in
        the calling parameters. Should it be unable to find the manifest then a
        0 will be returned.
        """
        Elements = []
        if self.checkManifest(manifest):
            conn = self.getconn()
            cur = conn.cursor()
            query =  "select sequence, includefile from  manifest where host = '" + manifest + "' order by sequence ASC;"
            cur.execute(query)
            array = cur.fetchall()
            lenArray = len(array)
            if lenArray > 0:
                for line in array:
                    Elements.append(line)
                return Elements
            else:
                return 0
        else:            

            return 0
    def htmlHeader(self):
        """Prints a html header.
        
        Arguments:
        None
        Return:
        """
        print "Content-type: text/html\r\n\r\n";
        print '<html>'
        print '<head>'
        print '<title>phoneHome</title>'
        print '<link rel="stylesheet" type="text/css" href="/phoneHome.css">'
        print '</head>'
        print '<body>'
        
    def testDbExists(self):
        """ Check to see that the Database exists (and is online)
        
        Arguments:
        None
        Return:
        Returns 1 if successfull otherwise a 0
        """
        try:
            conn = self.getconn()
            
        except:
            return 0
        return 1


    def printElement(self, element):
        """Prints the contents of a manifest Element
        
        Arguments:
        element the name of the manifest element (fragment) to be printed
        Return:
        """
        print 'Content-Type: text/xml '
        print ''
        filename = modPh.manifestLoc + element + '.xml'
        with open(filename) as file:
            lines = file.readlines()
        file.close
        for line in lines:
            if len(line):
                print line
    
    def agentCheck(self, host, user, password):
        """ Causes the agent to check to see if it has a new manifest to load
        
        Arguments:
        host        the hostname of the agents host
        user        the user name for the agent aapi
        Password    the corresponding password the the user
        Return:
        """
        
        cmdString = "/opt/abilisoft.com/asagent/bin/maql --batch /opt/abilisoft.com/asagent/etc/check.cmd --host " + user + "@" + host + " --password " + password + " > /tmp/check"
        value = os.system(cmdString)
        return value

    #def newAgentCheck(self, host, user, password):
    #    """ Causes the agent to check to see if it has a new manifest to load
    #    
    #    Arguments:
    #    host        the hostname of the agents host
    #    user        the user name for the agent aapi
    #    Password    the corresponding password the the user
    #    Return:
    #    """
    #    #login = user + '@' + host
    #    #value = subprocess.call(["/opt/abilisoft.com/asagent/bin/maql",  "--batch", "/opt/abilisoft.com/asagent/etc/check.cmd", "--host", login, "--password ", password ], shell = True)
    #    #return value
    #    try:
    #        aapi = maql.connect(host, user, password)
    #        aapi.Check()
    #    except:
    #        pass
        
    def configSectionExist(self, section):
        """ Check to see that a section exists withn the config file
        
        Arguments:
        section     the name of the section being checked
        Return:

        """
        config = ConfigParser.ConfigParser()
        config.readfp(open(modPh.configFile))
        result = config.has_section(section)
        return result
    
    def configAddSection(self, section):
        """ Add a section to the config file
        
        Arguments:
        section the name of the section to  be added to the config file
        Return:
        """
        config = ConfigParser.ConfigParser()
        config.readfp(open(modPh.configFile))
        if config.has_section(section) == 0:
            config.add_section(section)
            with open( modPh.configFile , 'wb') as configfile:
                config.write(configfile)

    def configOptionExists(self, section, option):
        """ Check to see if an option exists in the config file
        
        Arguments:
        section the section of the config file that the option should exist in
        option  the option of the config file being checked for
        Return:
        """
        config = ConfigParser.ConfigParser()
        config.readfp(open(modPh.configFile))
        result = config.has_option(section, option)
        return result

    def configSet(self, section, option, value):
        """ Sets an option in the config file
        
        Arguments:
        section the section of the config file that the option should exist in
        option  the option of the config file being checked for
        value   the value that the option should be set to
        Return:
        """
        try:
            config = ConfigParser.ConfigParser()
            config.readfp(open(modPh.configFile))
            self.configAddSection(section)
            config = ConfigParser.ConfigParser()
            config.readfp(open(modPh.configFile))
            config.set(section, option, value)
            with open( modPh.configFile , 'wb') as configfile:
                config.write(configfile)
            return 1
        except:
            return 0
    
    def configGet(self, section, option):
        """ get a value from the config file
        
        Arguments:
        section the section of the config file that the option should exist in
        option  the option of the config file being checked for
        Return:
        """
        config = ConfigParser.ConfigParser()
        config.readfp(open(modPh.configFile))
        if self.configOptionExists(section, option):
            result = config.get(section, option)
        else:
            result = ''
        return result
    
    def configRemove(self, section, option):
        """ removes an option from the config file
        
        Arguments:
        section the section of the config file that the option should exist in
        option  the option of the config file being checked for
        Return:
        """
        config = ConfigParser.ConfigParser()
        config.readfp(open(modPh.configFile))
        if self.configOptionExists(section, option):
            try:
                config.remove_option(section, option)
                result = 1
            except:
                result = 0
        with open( modPh.configFile , 'wb') as configfile:
            config.write(configfile)
        return result
    
    def pageHeader(self, title):
        """
        This function produces a consistent header/title for the web pages
        """
        self.htmlHeader()
        print "<h1>" + title + "</h1><br><br>";
        
    def newForm(self, form):
        print '<form action="' + form + '" method="post" target="_self">'

    def button(self, action, function, text):
        print '<td><form action="' + action + '" method="post" target="_self">'
        print '<input type="hidden" name="function" value="' + function + '">'
        print '<input type="submit" value="' + text + '" /></form></td>'
        
    def btnSubmit(self, function, text):
        print '<input type="hidden" name="function" value="' + function + '">'
        print '<td width="100" align="center">'
        print '<input type="submit" value="' + text + '" class="menu"/>'
        print '</form></td>'
    
    def btnCancel(self, action):
        self.button(action, '', 'Cancel')
    
    def btnOK(self, action):
        self.button(action, '', 'OK')
    
    def radio(self, name, label, width):
        print '<td width="' + str(width) + '" align="right">' + label + '</td><td width="10"><input type="radio" name="' + name + '" value="' + label + '"></td>'
        
    def upLoadAllWeb(self, filename):
        source = open(filename)
        sites = source.readlines()
        source.close
        for site in sites:
            if site[0] == '#':
                continue
            else:
                line = site.split(',')
                host = line[0]
                template = line[1]
                id = line[2]
                url = line[3].replace("\n","")
                conn = self.getconn()
                cur = conn.cursor()
                strSQL =  "INSERT INTO webmon (host, template, id, url) VALUES ('" + host + "', '" + template + "', '" + id + "', '" + url + "');"
                #print strSQL
                cur.execute(strSQL)
                conn.commit()
                conn.close()

    def upLoadOratab(self, filename):
        source = open(filename)
        instances = source.readlines()
        source.close
        for instance in instances:
            if instance[0] == '#':
                continue
            else:
                line = instance.split(':')
                ORACLE_SID = line[0].rstrip()
                ORACLE_HOME = line[1].rstrip()
                ORACLE_DBSTART = line[2].rstrip()
                conn = self.getconn()
                cur = conn.cursor()
                strSQL =  "INSERT INTO oramon (HOST, ORACLE_SID, ORACLE_HOME, ORACLE_DBSTART) VALUES ('" + host + "', '" + ORACLE_SID + "', '" + ORACLE_HOME + "', '" + ORACLE_DBSTART + "');"
                print strSQL
                cur.execute(strSQL)
                conn.commit()
                conn.close()


    def deleteAllWeb(self):
        conn = self.getconn()
        cur = conn.cursor()
        strSQL =  "delete from webmon;"
        #print strSQL
        cur.execute(strSQL)
        conn.commit()
        conn.close()
        
    def deleteOratab(self):
        conn = self.getconn()
        cur = conn.cursor()
        strSQL =  "delete from oramon;"
        #print strSQL
        cur.execute(strSQL)
        conn.commit()
        conn.close()
        
        



