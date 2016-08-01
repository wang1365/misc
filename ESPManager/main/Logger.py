#coding:utf-8
'''
Created on 2015年11月25日

@author: I321761
'''

from PyQt4 import QtCore

class Logger(QtCore.QObject):
    SIGNAL_MES = QtCore.pyqtSignal(str)
    def log(self, msg):
        self.SIGNAL_MES.emit(msg)