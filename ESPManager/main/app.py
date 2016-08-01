#coding=utf8
'''
Created on 2015年11月25日

@author: I321761
'''
import sys
from PyQt4 import QtGui
from ui.MainWindow import MainWindow

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    win = MainWindow()
    win.show()
    #win.showMaximized()

    
    sys.exit(app.exec_())