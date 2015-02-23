#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys,os
from PyQt4 import QtGui,QtCore
from PyQt4.QtCore import SLOT,SIGNAL
from PyQt4.phonon import Phonon
import ui_player
from configWindow import configWindow
from library import *
from time import sleep
import threadz
from rsmanager import Manager
from shutil import copy as CopySong



class Player:

    def __init__(self):

        self.Title = "RhythmBird"

        # MainWindow
        self.__win   = None

        # Phonon.MediaObject
        self.__media = None        

        # UI class        
        self.__ui    = None

        # Initialize the Application and Pass the arguments
        app = QtGui.QApplication(sys.argv)        
        app.setApplicationName("RythmBird")
        
        # Used to differnetiate between pause and playnext 
        self.state = 0

        # The Collection        
        self.__lib = Library(app,self)

        # The Resource Manager
        self.__res=Manager(self.__lib)

        # Keep Track of Progress
        self.__secs  = 0
        self.__mins  = 0
        self.__ticks = 0

        # Total Time of the Song
        self.__totalTime = "0:00"

        # Initialize The User Interface and bind its eventsn
        self.__init_ui__()

        # Initialize Phonon and its events
        self.__init_phonon__()        

        # Initializ Config Window
        self.configWIN = configWindow(QtGui.QDialog())     

        # Load Collection Tree
        self.__init_collecTree__()

        if (len(sys.argv) >1):
            self.open()
            self.play()
        else:
        # Show Window on Screen And Bind System exit with application exit
            self.__win.show()


        # Initialize Playlist
        self.__init_playlist__()

        # Initialize Misc. Stuff
        self.__init_misc__()
        
        self.__ui.progressBar.mousePressEvent = self.progressBarHandler

        sys.exit(app.exec_())        
        
    def progressBarHandler(self, click):
        tim = self.__media.currentTime()
        if tim == 0 or not self.__media.isSeekable():
            return
        pos = float(click.x())/float(self.__ui.progressBar.width())      
        tim = int(pos*self.__media.totalTime())
        self.__media.seek(tim)
        self. __change_time_on_seek__(tim)
        
    def __init_misc__(self):
        # Search Collection Events
        QtCore.QObject.connect(self.__ui.srchCollect, SIGNAL("textChanged (const QString&)"), self.searchColl)
        QtCore.QObject.connect(self.__ui.clearSearch, SIGNAL("clicked()"), self.clearSearch)
        
        # Search Playlist Events
        QtCore.QObject.connect(self.__ui.srchPlist, SIGNAL("textChanged (const QString&)"), self.searchPl)
        QtCore.QObject.connect(self.__ui.clearSearchPl, SIGNAL("clicked()"), self.clearSearchPl)

    # Clear Playlist Events
    def clearSearchPl(self):        
        for i in xrange(len(self.currPL)):
            self.__ui.playlistTree.showRow(i)
        self.__ui.srchPlist.setText("")
            
    # Search Playlist Table
    def searchPl(self,srch):
        srch = str(srch).strip()
        for i in xrange(len(self.currPL)):
            self.__ui.playlistTree.showRow(i)
        if srch == "":
            self.clearSearchPl()            
            return
        res  = self.__lib.searchList(srch,self.currPL)
        for i in xrange(len(self.currPL)):
            if self.currPL[i] not in res:
                self.__ui.playlistTree.hideRow(i)
        pass
    
    # When Search is erase
    def clearSearch(self):
        for song in self.songItems:            
                song.setHidden(False)
        for artist in self.artistItems:
            artist.setHidden(False)
            artist.setExpanded(False)
        for album in self.albumItems:
            album.setHidden(False)
            album.setExpanded(False)
            self.__ui.srchCollect.setText("")
        
    # Search Collection and Update UI
    def searchColl(self, srch):        
        srch = str(srch).strip()        
        #   When User Erases Search Term Restore to default 
        if srch == "":
            self.clearSearch()
            return        
        
        # Get Result song items
        res = self.__lib.search(srch)        

        # Hide all items initialy
        for song in self.songItems:            
            song.setHidden(True)            
            
        for artist in self.artistItems:
            artist.setHidden(True)
            artist.setExpanded(False)
            
        for album in self.albumItems:
            album.setHidden(True)
            album.setExpanded(False)
            
        #   Show items which were matched
        for i in res:            
            self.songItems[i].setHidden(False)
            album = self.songItems[i].parent()
            album.setHidden(False)
            album.setExpanded(True)            
            artist = album.parent()            
            artist.setHidden(False)
            artist.setExpanded(True)

    def __init_collecTree__(self):                
        artist=[]
        self.artistItems=[]        
        self.songItems=[]
        self.albumItems=[]
        self.__ui.collectTree.sortByColumn(0,0)        
        pos = 0                
        for i in self.__lib.tagdb:
            try:
                theArtist = i['artist']
            except KeyError,k:
                theArtist = [u"Unknown"]

            if theArtist not in artist:                     
                item = QtGui.QTreeWidgetItem(theArtist)
                self.artistItems.append(item)
                self.__ui.collectTree.addTopLevelItem(item)                                    
                artist.append(theArtist)      
            else:
                item = self.artistItems[artist.index(theArtist)]

            try:
                theAlbum = i['album']
            except KeyError,k:
                theAlbum = [u"Unknown"]

            albumFound = 0

            for index  in xrange(item.childCount()):
                citem = item.child(index)                
                if (unicode(citem.text(0)) == theAlbum[0]):                    
                    albumFound = 1
                    break;

            if (albumFound == 0):
                citem = QtGui.QTreeWidgetItem(theAlbum)
                self.albumItems.append(citem)
                item.addChild(citem)

            try:       
                theTitle = i['title']
            except KeyError,k:
                theTitle = [u"Unknown"]    
            theTitle.append(unicode(pos))                        
            itm = QtGui.QTreeWidgetItem(theTitle)
            self.songItems.append(itm)
            citem.addChild(itm)
            pos+=1




    def  __init_ui__(self):

        # Application logo
        self.__logo = QtGui.QIcon(QtGui.QPixmap(":/Icons/logo.png"))

        # Initialize Icons for Play/Pause
        self.iconPlay = QtGui.QIcon()
        self.iconPlay.addPixmap(QtGui.QPixmap(":/Icons/player_start.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.iconPause = QtGui.QIcon()
        self.iconPause.addPixmap(QtGui.QPixmap(":/Icons/player_pause.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)

        # Set skin 
        QtGui.QApplication.setStyle(QtGui.QStyleFactory.create("Oxygen"))    
        QtGui.QApplication.setPalette(QtGui.QApplication.style().standardPalette())

        # Set the Main Window
        self.__win = QtGui.QMainWindow()        
        self.__ui = ui_player.Ui_MainWindow()
        self.__ui.setupUi(self.__win)   
        self.__init_tray__()        
        self.__reset_progress__()    

        # Bind All Qt Events
        QtCore.QObject.connect(self.__ui.actionOpen, SIGNAL("triggered()"), self.open)
        QtCore.QObject.connect(self.__ui.actionUpdate, SIGNAL("triggered()"), self.updateColl)
        QtCore.QObject.connect(self.__ui.actionRescan, SIGNAL("triggered()"), self.rescanColl)
        QtCore.QObject.connect(self.__ui.actionConfigure, SIGNAL("triggered()"), self.configureWindow)
        QtCore.QObject.connect(self.__ui.actionQuit, SIGNAL("triggered()"), self.close)
        QtCore.QObject.connect(self.__ui.b_Play, SIGNAL("clicked()"), self.play)        
        QtCore.QObject.connect(self.__ui.b_Next, SIGNAL("clicked()"), self.playNext)        
        QtCore.QObject.connect(self.__ui.b_Prev, SIGNAL("clicked()"), self.playPrev)        
        QtCore.QObject.connect(self.__ui.b_Clear, SIGNAL("clicked()"), self.clearPlaylist)        
        QtCore.QObject.connect(self.__ui.b_Stop, SIGNAL("clicked()"), self.stop)

        QtCore.QObject.connect(self.__ui.collectTree, SIGNAL("itemDoubleClicked(QTreeWidgetItem *,int)"), self.loadSong)


        # Maximize Screen on Startup    
        screen = QtGui.QDesktopWidget().screenGeometry()
        #self.__win.resize(screen.width(),screen.height())

    # Clear Playlist and state
    def clearPlaylist(self):
        self.__ui.playlistTree.clearContents()
        self.__ui.playlistTree.setRowCount(0)
        self.currPL = []
        self.__plRow = 0
        self.currSong = -1

    # Load a Artist or Album or a Song
    def loadSong(self,song):

        # Its not a Song
        if song.childCount()!=0:
            for i in xrange(song.childCount()):
                ch = song.child(i)

                # Its an Artist
                if ch.childCount()!=0:
                    for j in xrange(ch.childCount()):
                        ch2 = ch.child(j)
                        songid = int(ch2.text(1))
                        self.appendPl(songid)

                # Its an Album        
                else:
                    songid = int(ch.text(1))
                    self.appendPl(songid)

        # Its a Song    
        else:    
            songid = int(song.text(1))                 
            self.appendPl(songid)

#        self.open(self.__lib.loc[songid])


    def updateColl(self):
        print "in"

    def close(self):
        self.configWIN.close()
        self.__win.close()


    def __init_tray__(self):

        # Define Actions that we are using
        a_Main = QtGui.QAction(self.__logo,"RhythmBird",self.__win)        
        self.a_Play = QtGui.QAction(self.iconPlay,"Play/Pause",self.__win)        
        a_Stop = QtGui.QAction(QtGui.QIcon(":/Icons/player_stop.png"),"Stop",self.__win)
        a_Prev = QtGui.QAction(QtGui.QIcon(":/Icons/player_prev.png"),"Prev",self.__win)
        a_Next = QtGui.QAction(QtGui.QIcon(":/Icons/player_next.png"),"Next",self.__win)
        a_Exit = QtGui.QAction(QtGui.QIcon(":/Icons/exit.png"),"Exit",self.__win)

        # Bind Action to the events
        QtCore.QObject.connect(self.a_Play, SIGNAL("triggered()"),self.__ui.b_Play,SLOT("click()"))
        QtCore.QObject.connect(a_Stop, SIGNAL("triggered()"),self.__ui.b_Stop,SLOT("click()"))
        QtCore.QObject.connect(a_Prev, SIGNAL("triggered()"),self.__ui.b_Prev,SLOT("click()"))
        QtCore.QObject.connect(a_Next, SIGNAL("triggered()"),self.__ui.b_Next,SLOT("click()"))
        QtCore.QObject.connect(a_Exit, SIGNAL("triggered()"),self.__ui.actionQuit,SLOT("trigger()"))                      

        # Set the System Tray Menu              
        trayMenu = QtGui.QMenu(self.__win)
        trayMenu.addAction(a_Main)
        trayMenu.addSeparator()
        trayMenu.addActions([a_Prev,self.a_Play,a_Stop,a_Next,a_Exit])             
        trayMenu.addAction(a_Exit)

        # Set the System Tray Icon                 
        self.trayIcon = QtGui.QSystemTrayIcon(self.__logo, self.__win)        
        self.trayIcon.setContextMenu(trayMenu)  
        self.trayIcon.show()        
        self.trayIcon.setToolTip("Stopped") 

        # Signal for Icon Activation ( Click)
        traySignal = "activated(QSystemTrayIcon::ActivationReason)"
        QtCore.QObject.connect(self.trayIcon, SIGNAL(traySignal), self.__icon_activated)

        # Flag for checking on icon click
        self.__Visible = 1

    # Overriding Default Qt Event     
    def closeEvent(self, event):        
        self.__ui.hide()
        self.trayIcon.show() 
        event.ignore()

    # When User Double Clicks on the icon
    def __icon_activated(self, reason):
        if reason == QtGui.QSystemTrayIcon.Trigger:
            if self.__Visible == 0:
                self.__win.show()    
                self.__Visible = 1
            else:
                self.__win.hide()
                self.__Visible = 0

    # Initialize Phonon Object
    def __init_phonon__(self):

        self.__media = Phonon.MediaObject(self.__win)
        self.__media.setTickInterval(200)        
        self.audioOutput = Phonon.AudioOutput(Phonon.MusicCategory, self.__win)
        Phonon.createPath(self.__media,self.audioOutput)
        self.__ui.volumeSlider.setAudioOutput(self.audioOutput) 

        # Display volume in label 
        self.__ui.volumeDisplay.setText(QtCore.QString(str(int(self.audioOutput.volume() *100))))

        # Phonon Events 
        QtCore.QObject.connect(self.__media, SIGNAL("tick(qint64)"), self.__ticked__)
        QtCore.QObject.connect(self.__media, SIGNAL("finished()"), self.playNext)
        QtCore.QObject.connect(self.audioOutput, SIGNAL("volumeChanged(qreal)"), self.__volume_changed__)
        # self.__ui.seekSlider.setMediaObject(self.__media)              

    # On Volume change update label
    def __volume_changed__(self):                
        self.__ui.volumeDisplay.setText(QtCore.QString(str(int(self.audioOutput.volume() *100))))                        

    # Show the configuration Window    
    def configureWindow(self):
        self.configWIN.show()             

    # Rescan collection and repopulate it in the display
    def rescanColl(self):        
        self.__ui.collectTree.clear()
        self.__lib.populate(self.configWIN.dirList)


    # Play song from Playlist
    def playfromList(self):        
        self.stop()       
        
        # TODO : loading album art , lyrics, osd        
        index = self.currPL[self.currSong]                
        self.__ui.lyrcBrowser.setHtml(self.__res.requestLyrics(index))
        self.__ui.lyrcBrowser.reload()
        self.__ui.wikiView.setHtml(self.__res.requestWiki(index)) 
        self.__ui.wikiView.reload()
        self.__ui.albumArt.setPixmap(QtGui.QPixmap(self.__res.requestArt(index)))
        try:
            self.__ui.artistName.setText(str(self.__lib.tagdb[index]['artist'][0]))
            self.__ui.trackTitle.setText(str(self.__lib.tagdb[index]['title'][0]))
        except:
            print "Text Label Error"
        self.state = 1            
        self.open(self.__lib.loc[index])



    # Play Next song in the playlist
    def playNext(self):
        # Play list restarting
        if self.__plRow == 0:
            return

        self.currSong+=1

        if self.currSong >= self.__plRow:
            self.currSong = 0

        self.playfromList()

    # Play Previous song in the playlist
    def playPrev(self):
        if ((self.__plRow == 0) or (self.currSong -1 <0)):
            return

        self.currSong-=1
        self.playfromList()

    # Play Song where user clicks at playlist
    def playAt(self,x,y):
        self.currSong = x
        self.playfromList()        

    # Open a audio file via dialog or program arg or direct passing
    def open(self,filename=None):

        if (filename==None):
            if (len(sys.argv) >1):
                filename = sys.argv[1]
                print "Trying to Play " + filename      
            else:
                filename = QtGui.QFileDialog.getOpenFileName(self.__win, 'Select a Song', os.path.expanduser('~'), 'Audio Files (*.wav *.mp3 *.m4a *.ogg *.flac)')

        if not os.path.isfile(filename) and filename!= None :
            print 'File Cannot be Opened'
            return -1

        # This is done for time being due to phonon not able to handle ( in names

        CopySong(filename,"tempPlay.mp3")
        self.__media.setCurrentSource(Phonon.MediaSource("tempPlay.mp3"))        

        while self.__media.totalTime() == -1:
            sleep(0.1)

        self.__totalTime = (self.__media.totalTime())/1000               
        mins = str(self.__totalTime/60)       
        secs = str(self.__totalTime%60)

        if (len(secs)==1):
            secs='0'+secs        
        self.__totalTime =  mins+':'+secs

        self.__reset_progress__()                           

        self.__secs = 0
        self.__mins = 0

        self.play()


    # For Playing or Pausing 
    def play(self):                
        chk = self.__media.state()    
        
        # It seems when you the phonon media object is stopped, it enter 2 (PAUSED) state, for next,prev songs
        if self.state ==1:
                self.state = 0
                if (chk == 2):
                    chk = 0

                
        if (chk == 1 or chk == 4 or chk == 0):
            self.__media.play()             
            self.__ui.b_Play.setIcon(self.iconPause)                  
            self.a_Play.setIcon(self.iconPause)   
            self.__ui.progressBar.setMaximum(self.__media.totalTime())                                         

        elif (chk == 5):
            self.__media.stop()
            print 'Unsupported Media Type'
            self.__win.setWindowTitle('qPlayer')          

        elif(chk == 2):
            self.__ui.b_Play.setIcon(self.iconPlay)
            self.a_Play.setIcon(self.iconPlay)   
            self.__media.pause()

    # For Pausing For explicit api support 
    def pause(self):
        self.__media.pause()        

    # stop the audio playback; resets to beginning of file
    def stop(self):
        self.__media.stop()        
        self.__ui.b_Play.setIcon(self.iconPlay)
        self.__reset_progress__()

    # callback for the tick signal which is fired during playback;
    # update progress bar
    def __ticked__(self,time):

        self.__ui.progressBar.setProperty('value', QtCore.QVariant(time))
        self.__ui.progressBar.repaint()        
        self.__ticks = (self.__ticks + 1) % 5
        if self.__ticks == 0:
            self.__ui.progressBar.setFormat(self.__format_time__()+"     /     "+self.__totalTime)

    def __change_time_on_seek__(self,tim):        
        tim = tim/1000
        self.__mins = tim/60
        self.__secs = tim%60

    # Compute new time string to display in progress bar
    def __format_time__(self):

        self.__secs = (self.__secs + 1) % 60
        if self.__secs == 0:

            self.__mins = self.__mins + 1
        if self.__secs < 10:
            sstr = '0' + str(self.__secs)
        else:
            sstr = str(self.__secs)
        return str(self.__mins) + ':' + sstr

    # reset progress bar to initial state
    def __reset_progress__(self):
        self.__ui.progressBar.setProperty('value', QtCore.QVariant(0))
        self.__ui.progressBar.setFormat("0:00"+"     /     "+self.__totalTime)

        self.__secs = 0
        self.__mins = 0
        self.__ticks = 0

    # Initialize playlist
    def __init_playlist__(self):
        self.__plRow = 0
        self.currSong = -1      # Current Song being played in the Playlist
        self.currPL = []           # The List to store all ids of the songs to be played
        # Play Song When Clicked
        QtCore.QObject.connect(self.__ui.playlistTree,SIGNAL("cellDoubleClicked(int,int)"),self.playAt)
        
        # Forced change pf drop event
        self.__ui.playlistTree.dropEvent = self.handleDrop        
        
        
     # Drop Event for the playlist    
    def handleDrop(self,DropEvent):            
        item = DropEvent.source().currentItem()    
        
        # Album Check
        count  = item.childCount()
        if count !=0:
            for i in xrange(count): 
                child = item.child(i)
                                
                # Artist Check
                count2 = child.childCount()
                
                # Its and Artist Item
                if count2!=0:
                    for j in xrange(count2):
                        song = child.child(j)
                        self.appendPl(song.text(1))
                # Its an Album Item
                else:
                    self.appendPl(child.text(1))
                # Its a Song Item
        else:
            self.appendPl(item.text(1))
        
    # Append Song to the playlist    
    def   appendPl(self,songid):
        songid = int(songid)
        tag = self.__lib.tagdb[songid]
        self.__ui.playlistTree.setRowCount( self.__ui.playlistTree.rowCount() + 1)
        try:
            temp = tag['title'][0]
        except:
            temp = ""

        item = QtGui.QTableWidgetItem(temp)
        self.__ui.playlistTree.setItem(self.__plRow, 0, item)

        try:
            temp = tag["artist"][0]
        except:
            temp = ""

        item = QtGui.QTableWidgetItem(temp)
        self.__ui.playlistTree.setItem(self.__plRow, 1, item)

        try:
            temp = tag["album"][0]
        except:
            temp ="" 

        item = QtGui.QTableWidgetItem(temp)
        self.__ui.playlistTree.setItem(self.__plRow, 2, item)

        try:    
            temp = tag["genre"][0]
        except:    
            temp = ""

        item = QtGui.QTableWidgetItem(temp)
        self.__ui.playlistTree.setItem(self.__plRow, 3, item)
        self.currPL.append(songid)
        self.__plRow+=1

        if self.__plRow == 1:            
            self.playNext()

    # Populate the Playlist layout
    def populateList(self , musicList):

        self.__ui.playlistTree.setRowCount(len(musicList))

        for i in xrange(len(musicList)):            
            self.__ui.playlistTree.setVerticalHeaderItem(i, QtGui.QTableWidgetItem())

        for y, row in enumerate(musicList):
            for x, cell in enumerate(row):
                item = QtGui.QTableWidgetItem(cell)

                self.__ui.playlistTree.setItem(y, x, item)

        self.__ui.playlistTree.resizeColumnsToContents()



