
from PyQt4 import QtCore

# This is a Thread to execute operations that should continously
class threadz(QtCore.QThread):
    def __init__(self,func,parent=None):
        QtCore.QThread.__init__(self,parent)        
        self.func = func        
       
    
    def run(self):
        for i in self.func:
            if i!= None:
                i()            
        self.exit()
