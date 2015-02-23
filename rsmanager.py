#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os,urllib2
from urllib import urlencode

class Manager:

    # Initialize Lyrics, Artist Info Manager 
    def __init__(self,Library):
        if not os.path.isdir("LyricsDB"):
            os.mkdir("LyricsDB")
        if not os.path.isdir("ArtistInfoDB"):
            os.mkdir("ArtistInfoDB")
        if not os.path.isdir("Album Art"):
            os.mkdir("Album Art")

        # Last.fm Key
        self.__key="19ceabf0295dc56fb0f52826321a1887"         
        self.ArtURL  = "http://ws.audioscrobbler.com/2.0/?method=album.getinfo&api_key="+self.__key
        self.LyURL = "http://www.lyricsplugin.com/wmplayer03/plugin/?"
        self.WikiURL = "http://en.wikipedia.org/wiki/"
        self.__lib = Library    
        self._AA="Album Art/"
        self._LD = "LyricsDB/"
        self._AD = "ArtistInfoDB/"
        
     # Fetches Art For all songs
    def requestAllArt(self):        
        for i in xrange(len(self.__lib.loc)):
            x= self.requestArt(i)            
    
    # Fetches Lyrics For all songs
    def requestAllLyrics(self):        
        for i in xrange(len(self.__lib.loc)):
            x= self.requestLyrics(i)   
            
    # Fetched ArtistInfo for all artists
    def requestAllWiki(self):        
        for i in xrange(len(self.__lib.loc)):
            x= self.requestWiki(i)   
    
            
        
    # Get Album Art from HD if available or get it from internet
    def requestArt(self,songid):
        try:            
            artist = str(self.__lib.tagdb[songid]['artist'][0])
            album = str(self.__lib.tagdb[songid]['album'][0])
            if not os.path.exists(self._AA+artist.replace("/","_")+"_"+album.replace("/","_")+".jpg"):                
                self.fetchArt(artist,album)            
        except:
            return ""
        
        return self._AA+artist+"_"+album+".jpg"
            
    
    # Get Album Art from Internet (Last.fm)
    def fetchArt(self,artist,album):                            
        data = urlencode({"artist":artist,"album":album})
        try:
            aa = urllib2.urlopen(self.ArtURL+"&"+data)
            imgurl = aa.read()
            aa.close()
            imgurl = imgurl[imgurl.find('<image size="extralarge">')+25:]
            imgurl = imgurl[:imgurl.find('</image>')]
            img = urllib2.urlopen(imgurl) 
            imgdata = img.read()
            img.close()                  
            fil = file(self._AA+artist.replace("/","_")+"_"+album.replace("/","_")+".jpg","w")
            fil.write(imgdata)
            fil.close()                            
            
        except:
            pass
        return

    # Get Lyrics from HD if available or get it from internet
    def requestLyrics(self,songid):
        try:
            if not os.path.exists(self._LD+str(songid)+".lyrc"):
                self.fetchLyrics(songid)
        except:
            return ""
        if not os.path.exists(self._LD+str(songid)+".lyrc"):
            return ""
        else:
            fil = file(self._LD+str(songid)+".lyrc","r")
            lyricfile = fil.read()
            fil.close()
            return lyricfile


    # Get Artist Info from the HD or internet
    def requestWiki(self,songid):        
        try:
            artist = str(self.__lib.tagdb[songid]['artist'][0])            
            artist = artist.replace(" ","_")   
            if not os.path.exists(self._AD+artist+".ainfo"):                
                self.fetchArtistInfo(artist)                
        except:                 
            return ""        
        
        fil = file(self._AD+str(artist)+".ainfo",'r')
        info = fil.read()
        fil.close()
        return info
        #return self._AD+artist+".ainfo"
        
        
    #Get Artist Info from intenet
    def fetchArtistInfo(self,artist):                          
        request = urllib2.Request(self.WikiURL+artist)        
        request.add_header('User-Agent','RhythmBird:0.1')            
        opener  = urllib2.build_opener()                
        info = opener.open(request).read()                
        info=info[info.find('<h3 id="siteSub">'):]
        info=info[:info.find('<li id="disclaimer">')]
        fil = file(self._AD+str(artist)+".ainfo",'w')
        fil.write(info)
        fil.close()
        
    # Get lyrics from the internet
    def fetchLyrics(self,songid):

        try:

            data = { "artist": str(self.__lib.tagdb[songid]["artist"][0] ),  "title":str(self.__lib.tagdb[songid]["title"] [0])}            
            result = urllib2.urlopen(self.LyURL+urlencode(data))                    
            lyrics = result.read()
            result.close()                    
            lyrics = "<center><u><h3>"+data['title']+"</h3>"+"<h5>"+data['artist']+"</h5></center><br>"+lyrics[lyrics.find('<div id="lyrics">'):]            
            lyrics = lyrics[:lyrics.find('</div>')+6]

        except:           
            lyrics = ""
            return

        fil = file(self._LD + str(songid)+".lyrc","w")    
        fil.write(lyrics)
        fil.close()





