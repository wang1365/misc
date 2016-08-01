#coding:utf-8
'''
Created on 2015年11月26日

@author: I321761
'''

from PyQt4 import QtGui, QtCore

class WaitingWindow(QtGui.QDialog):
    def __init__(self, text, parent = None):
        super(WaitingWindow, self).__init__(parent)
        self.text = text
        self.resize(400, 50)
        self.label = QtGui.QLabel(u"命令执行中")
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setTextFormat(QtCore.Qt.RichText)
        v = QtGui.QVBoxLayout()
        v.addWidget(self.label)
        self.setLayout(v)
        
        self.tick = 0
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(1000)
        
    def update(self):
        self.tick = self.tick + 1
        self.label.setText(u"<p>命令执行中" + u'.'*(self.tick%4) + u"</p>")
