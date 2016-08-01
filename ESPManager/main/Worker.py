#coding:utf-8
'''
Created on 2015年11月25日

@author: I321761
'''

from PyQt4 import QtCore

class Worker(QtCore.QThread):
    def __init__(self, job, name, signal):
        self.job = job
        self.name = name
        self.signal = signal
        super(Worker, self).__init__()
        
    def _log(self, msg):
        self.logger.log(msg)
        
    def run(self):
        print 'Worker run begin'
        self.job()
        self.signal.emit()
        print 'Worker run end'
        
    def getname(self):
        return self.name