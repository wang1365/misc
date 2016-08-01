#coding:utf-8
'''
Created on 2015年11月25日

@author: I321761
'''
from PyQt4 import QtGui, QtCore

class LogWindow(QtGui.QDialog):
    def __init__(self, parent = None):
        super(LogWindow, self).__init__(parent, QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint)
        self.brow = QtGui.QTextBrowser(self)
        
        v = QtGui.QVBoxLayout()
        v.addWidget(self.brow)
        
        self.setLayout(v)
        self.resize(800, 600)
        
    def setText(self, text):
        self.brow.setPlainText(text)