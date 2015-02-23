#!/usr/bin/env python
# -*- coding: utf-8 -*-

from mutagen.easyid3 import EasyID3
from PyQt4 import QtCore
from PyQt4.QtCore import SLOT,SIGNAL
import os
import fnmatch
import threading

def TAG(fil=None):
        if fil!=None:
                try:
                        return dict(EasyID3(fil))
                except:
                        return {}

class Library(QtCore.QThread):
        def __init__(self,parent):
                QtCore.QThread.__init__(self,parent)
                self.tagdb = []                                
                self.loc = []
                QtCore.QObject.connect(self, SIGNAL("rescanColl(list)"), self.populate)                                
                
        def run(self):                
                self.__loadColl__()          
                while 1:
                        self.sleep(2)
                        print '1'
                
                
      #try:
       # os.mkdir("Album Art")
        #self.fetchCovers()
      #except:
        
        #self.__loadCovers__()
          
      
        def __loadColl__(self):
                try:
                        f = open("mycoll.db","r")
                        self.loc = eval(f.read())
                        f.close()
                        self.__loadTags__()                              
                except:
                        return -1
                return 0

        def __loadTags__(self):
                try:  
                        f = open("mytags.db","r")                                                                         
                        self.tagdb = eval(f.read())
                        f.close()
                except:
                        return -1
                return 0

        def __readTags__(self):
                self.tagdb=[]
                for i in self.loc:
                        self.tagdb.append(TAG(i))
                f = open("mytags.db","w")
                f.write(str(self.tagdb))
                f.close()

        def populate(self,dirlist):
                self.loc = []
                recursv = "/*.mp3"
                curCount = 0
                prevCount = 0
    
                for i in dirlist:
                        for root, dirs, files in os.walk(i):          
                                for  fil in files:            
                                        if fnmatch.fnmatch(fil.lower(),"*.mp3"):
                                                self.loc.append(root+'/'+fil)      
                                
                f = open("mycoll.db","w")
                f.write(str(self.loc))
                f.close()
    
                self.__readTags__()
                print "Done Populating"
                print self.isRunning(),self.isFinished()
      

        def search(self,item):      
                results=[]
                item = item.upper()
                for i in xrange(len(self.tagdb)):       
                        if (self.mydbsrch[i].find(item)!=-1):          
                                results.append(i)
                return results
      
      
      



