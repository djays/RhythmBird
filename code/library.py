#!/usr/bin/env python
# -*- coding: utf-8 -*-

from mutagen.easyid3 import EasyID3
from PyQt4 import QtCore
from PyQt4.QtCore import SLOT,SIGNAL
import os
import fnmatch
from threadz import threadz

def TAG(fil=None):
    if fil!=None:
        try:
            return dict(EasyID3(fil))
        except:
            return {}

class Library():
    
    def __init__(self,parent,player):                     
        self.parent = parent
        self.player=player
        self.tagdb = []                                
        self.loc = []
        self.dirlist = []
        
        # Repopulate collection without pausing UI
        self.populateThread = threadz([self.__populate__],self.parent)
        
        # When Collection populated, update UI (in this thread)
        QtCore.QObject.connect(self.populateThread,SIGNAL("finished()"),self.player.__init_collecTree__,2)
        self.__loadColl__()   

        
    
    def populate(self,dirlist,action = None):
        self.dirlist = dirlist            
        self.populateThread.start()
        
        
    # Called before Object is Deleted, de_reference player var    
    def __del__(self):
        self.player = None

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
        self.tagdb = []
        for i in self.loc:
            self.tagdb.append(TAG(i))
        f = open("mytags.db","w")
        f.write(str(self.tagdb))
        f.close()

    def __populate__(self):
        print "Starting populating"
        self.loc = []                
        recursv = "/*.mp3"
        curCount = 0
        prevCount = 0

        for i in self.dirlist:
            for root, dirs, files in os.walk(i):          
                for  fil in files:            
                    if fnmatch.fnmatch(fil.lower(),"*.mp3"):
                        self.loc.append(root+'/'+fil)      

        f = open("mycoll.db","w")
        f.write(str(self.loc))
        f.close()

        self.__readTags__()
        print "Done Populating"


    def searchList(self,item,List):      
        results=[]
        item = item.upper()
        for i in List:    
            temp = str(self.tagdb[i]).upper()
            if (temp.find(item)!=-1):                            
                results.append(i)            
        return results
    
    def search(self,item):      
        results=[]
        item = item.upper()
        for i in xrange(len(self.tagdb)):    
            temp = str(self.tagdb[i]).upper()
            if (temp.find(item)!=-1):                            
                results.append(i)            
        return results






