#!/usr/bin/env python
# -*- coding: utf-8 -*-

from mutagen.easyid3 import EasyID3
import os
import fnmatch

class TAG:
    def __init__(self,fil=None):
      if fil!=None:
        return dict(EasyID3(fil))

class Collection:
    def __init__(self):
      self.mydb = []
      
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
        print self.mydb    

      except:
        return -1

      return 0
    def __loadTags__(self):
        f = open("mytags.db","r")                                                                         
        self.db = eval(f.read())
        f.close()

    def __readTags__(self):
        for i in self.loc:
            self.mydb.append(EasyID3(i))
        f = open("mytags.db","w")
        f.write(str(self.mydb))
        f.close()

    def populate(self,dirlist):
      #print dirlist
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
      

    def search(self,item):      
      results=[]
      item = item.upper()
      for i in xrange(len(self.mydbsrch)):       
        if (self.mydbsrch[i].find(item)!=-1):          
          results.append(i)
      return results
      
      
      

dirlist = ['/media/Stuff/Music/']
a = Collection()
a.populate(dirlist)

