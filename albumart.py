import sys
from os import listdir

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from pictureflow import *

app = QApplication(sys.argv)

w = PictureFlow()
thedir = 'Album Art/'
images = listdir(thedir)
for i in images:
	if i.endswith('jpg'):
		w.addSlide(QPixmap(thedir+'%s' % i))
w.show()

sys.exit(app.exec_())
