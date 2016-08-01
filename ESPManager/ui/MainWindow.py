#coding:utf-8
'''
Created on 2015年11月25日

@author: I321761
'''

from PyQt4 import QtGui
from ui.ESPWindow import ESPWindow
from ui.HanaWindow import HanaWindow

esps = (
         {'ip':'10.128.184.131', 'user':'root', 'password':'Sap12345' },
         {'ip':'10.128.184.150', 'user':'root', 'password':'Sap12345'},
         {'ip':'10.254.203.191', 'user':'root', 'password':'Sap67890'},
         {'ip':'10.101.1.10', 'user':'root', 'password':'Sap67890'},
         #('10.128.170.54', 'root', 'Initial0'),
         #('10.128.184.234', 'root', 'Sap12345'),
         )

hanas = (
        {'name':'TPD', 'ip':'10.128.184.142', 'user':'SYSTEM', 'password':'Hana67890', 'instance': '00'},
        {'name':'TPE', 'ip':'10.128.184.214', 'user':'SYSTEM', 'password':'Hana67890', 'instance': '00'},  
        )

class MainWindow(QtGui.QWidget):
    def __init__(self, *argv, **kwarg):
        super(MainWindow, self).__init__(*argv, **kwarg)
        self._init_ui()
        self.resize(1000, 800)

    def _init_ui(self):
        self.setWindowTitle(u'ESP管理器')
        
        self.tab = QtGui.QTabWidget()
        self.espTab = QtGui.QTabWidget()
        self.hanaTab = QtGui.QTabWidget()
        
        self.tab.addTab(self.espTab, 'ESP')
        self.tab.addTab(self.hanaTab, 'HANA')
        for espinfo in esps:
            tw = ESPWindow(espinfo)
            self.espTab.addTab(tw, espinfo['ip'])
            
        for hanainfo in hanas:
            tw = HanaWindow(hanainfo)
            self.hanaTab.addTab(tw, '%s(%s)'%(hanainfo['name'], hanainfo['ip']))
        
        v = QtGui.QVBoxLayout()
        v.addWidget(self.tab)
        self.setLayout(v)