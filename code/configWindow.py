import ui_control,os
from PyQt4 import QtGui,QtCore
from PyQt4.QtCore import SLOT,SIGNAL

  
# COLLECTION_DIRS=dir1,dir2,\n
class configWindow():        
    
    def __init__(self,controlWIN):     
        self.dirList=[]
        
        # Initialize UI
        self.__win = controlWIN 
        self.__ui = ui_control.Ui_configureWindow()          
        self.__ui.setupUi(self.__win)
        
        # Intialize Events (External Reference to this class should exist)
        self.__init_events__()
        
        # Load Config
        try:
            f = open("RhythmBird.conf","r")
            conf = f.read()
            f.close()
        except:
            conf=""
        
        # Load Collection Directories
        i=conf.find("COLLECTION_DIRS=")
        if(i == -1):
            conf+="COLLECTION_DIRS=\n"            
            f = open("RhythmBird.conf","w")
            f.write(conf)
            f.close()
        else:
            i+=16
        conf=conf[:-1]
        self.dirList = conf[i: i + conf[i:].find("\n") ].split(",")
        
        # Remove Invalid Entries
        for i in self.dirList:
            if os.path.isdir(i) == False:                
                self.dirList.remove(i)
        
        #Display Directories in List Widget        
        try:
            if self.dirList[0]!='' :                     
                self.__ui.songDirList.addItems(self.dirList)
        except:
            pass
    
  
    # To show , hide the window
    def show(self):
        self.__win.show()
        
    def close(self):
        self.__win.close()
        
    # Bind control to event handlers    
    def __init_events__(self):        
        try:            
            QtCore.QObject.connect(self.__ui.b_RemoveT, SIGNAL("clicked()"),self.removeSongDir)  
            QtCore.QObject.connect(self.__ui.b_AddT, SIGNAL("clicked()"),self.selectSongDir)  
            QtCore.QObject.connect(self.__ui.buttonBox, SIGNAL("rejected()"),self.__win.close)
        except:
            print "Event Bind Error: " 
      
   # Choose a song Directory, add it to list
    def selectSongDir(self):        
        # Show only Directories
        chooseDir = QtGui.QFileDialog(self.__win)
        chooseDir.setFileMode(QtGui.QFileDialog.Directory)
        chooseDir.setOption(QtGui.QFileDialog.ShowDirsOnly, True)
        selDir =  str(QtGui.QFileDialog.getExistingDirectory(self.__win, "Select Directory","",QtGui.QFileDialog.ShowDirsOnly | QtGui.QFileDialog.DontResolveSymlinks))
        
        # User Presses Cancel, avoid duplicate entries
        if  selDir!=None :
            try:
                self.dirList.index(selDir)
            except:
                self.dirList.append(selDir)
        else:
            return
        # Add dir to List        
        selDir.replace("'","")
        
        self.__ui.songDirList.addItem(QtCore.QString(selDir))
        
        # Update Configuration
        f = open("RhythmBird.conf","r")
        conf = f.read()
        f.close()
        i = conf.find("COLLECTION_DIRS=")+16
        i= i + conf[i:].find("\n")
        
        # Seperate multiple entries        
        conf = conf[:i]+selDir+",\n"+conf[i:]
        
         # Write Back Config   
        f = open("RhythmBird.conf","w")
        f.write(conf)
        f.close()
        
     # Select Multiple Directories and remove   
    def removeSongDir(self):
        rmdir =  self.__ui.songDirList.selectedIndexes()
        if rmdir == []:
            return
        
        for i in rmdir:
            self.dirList.pop(i.row())
            item = self.__ui.songDirList.takeItem(i.row())
            del item
        
            try:
                f = open("RhythmBird.conf","r")
                conf = f.read()
                f.close()
                i=conf.find("COLLECTION_DIRS=")+16
                i2 = i + conf[i:].find("\n")
                conf = conf[:i]+str(self.dirList)[1:-1]+',' +conf[i2:]
                f = open("RhythmBird.conf","w")
                f.write(conf)
                f.close()
            except:
                print "Configuration File Cannot be Accessed"
        
      
    
    
        
        
        
        


