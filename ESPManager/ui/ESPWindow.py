#coding:utf-8
'''
Created on 2015年11月25日

@author: I321761
'''

from PyQt4 import QtGui, QtCore
from main.Logger import Logger
from main.ESPHost import ESPHost
from main.Worker import Worker
from LogWindow import LogWindow
from WaitingWindow import WaitingWindow

class ESPWindow(QtGui.QWidget):
    sig_start_done = QtCore.pyqtSignal()
    sig_stop_done = QtCore.pyqtSignal()
    sig_refresh_done = QtCore.pyqtSignal()
    
    def __init__(self, hostinfo, parent = None):
        self.hostinfo = hostinfo
        self.projects = []
        self.logger = Logger()
        self.logger.SIGNAL_MES.connect(self._addLog)
        super(ESPWindow, self).__init__(parent)
        
        self._init_ui()
        
        
    
    def _log(self, msg):
        self.logger.log(msg)
        
    def _init_ui(self):
        v = QtGui.QVBoxLayout()
        top_h = QtGui.QHBoxLayout()
        top_h_v = QtGui.QVBoxLayout()
        
        top = QtGui.QWidget()
        top.setMinimumHeight(100)
     
        self.host = ESPHost(self.hostinfo, self.logger)
        self._refresh_data()
        
        tb = self._tb = QtGui.QTableWidget(20, 3)
        tb.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        tb.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        tb.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        tb.setAlternatingRowColors(True)
        tb.itemDoubleClicked.connect(self._onItemClick)
        tb.setHorizontalHeaderLabels([u'ESP项目', u'目的HANA', u'项目状态'])
        tb.setCursor(QtGui.QCursor(QtCore.Qt.OpenHandCursor))
        tb.itemSelectionChanged.connect(self._onTableItemSelectionChanged)
        
        btns = (
                (u"启动项目", self._onBtnStart),
                (u"停止项目", self._onBtnStop),
                (u"刷新",    self._onBtnRefresh),
                (u"查看日志", self._onBtnCheckLog),
                (u"查看ccl", self._onBtnCheckCCL),
                )
        
        for i in btns:
            btn = QtGui.QPushButton(i[0])
            btn.clicked.connect(i[1])
            top_h_v.addWidget(btn)
        
        self._edit_msg = QtGui.QTextEdit()
        self._edit_msg.setReadOnly(True)
        self._edit_msg.setMinimumHeight(100)
        
        top_h.addWidget(tb)
        top_h.addLayout(top_h_v)
        top.setLayout(top_h)
        
        split = QtGui.QSplitter(QtCore.Qt.Vertical)
        split.addWidget(top)
        split.addWidget(self._edit_msg)
        v.addWidget(split)
        
        self.setLayout(v)
        
        self._initRightPopMenu()
        
    def _initRightPopMenu(self):
        self._tb.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self._tb.customContextMenuRequested.connect(self._onTableRightClicked)
        self._popmenu = QtGui.QMenu(self._tb)

        menus = ((u"启动项目", self._onBtnStart),
                (u"停止项目",self._onBtnStop),
                (u"刷新",self._onBtnRefresh),
                (u"查看日志",self._onBtnCheckLog),
                (u"查看ccl",self._onBtnCheckCCL),
                (u"查看最近数据插入情况",self._onBtn10Minutes),
                )
        for i in menus:
            action = QtGui.QAction(i[0], self._tb)
            self._popmenu.addAction(action)
            action.triggered.connect(i[1])

    def _onTableItemSelectionChanged(self):
        items = self._tb.selectedItems()
        for item in items:
            pass
            #item = QtGui.QTableWidgetItem()
            #item.setBackgroundColor(QtGui.QColor(100, 0, 0))
               
    def _onTableRightClicked(self, pos):
        print  '_onTableRightClicked'
        self._popmenu.exec_(QtGui.QCursor.pos())
        
    def _onItemClick(self, item):
        #item = QTableWidgetItem()
        index = item.row()
        if len(self.projects) > index:
            self._log(self.projects[index].tail())
        
    def _refresh_data(self):
        self.sig_refresh_done.connect(self._refresh_data_done)
        self.woker = Worker(self.host.init, "Data refresh", self.sig_refresh_done)
        self.woker.start()
        
    def _refresh_data_done(self):
        self._refresh_ui()
    
    def _refresh_ui(self):
        self.projects = self.host.get_projects()
        
        for i, proj in enumerate(self.projects):
            print "##############################%r"%proj.get_config()
            for j, val in enumerate(proj.get_config()[:3]):
                print ">>>>>>>>>>>>>>>>>>", (j, val)
                item = QtGui.QTableWidgetItem()
                item.setData(0, val)
                item.setData(1, proj)
                item.setTextAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
                if proj.get_config()[2] == u'运行中':
                    item.setBackgroundColor(QtGui.QColor(0,200,10)) 
                    #item.setTextColor(QtGui.QColor(255,255,255))
                elif u'停止' in proj.get_config()[2]:
                    item.setBackgroundColor(QtGui.QColor(200,0,10)) 
                self._tb.setItem(i, j, item)
        self._tb.resizeColumnsToContents()
        self._tb.setFocus()
        #self._tb.setItemSelected(self._tb.item(0, 0), True)
    def hasWorkerRunning(self):
        ret = self.woker.isRunning()
        if ret:
            self._log("Worker [%s] is still running"%self.woker.getname())
            QtGui.QMessageBox.information(None, u"提醒", u"已经存在一个命令正在执行中，请稍后再试！", 
                                          buttons=QtGui.QMessageBox.Ok)
        return ret
      
    def _onBtnStart(self):
        print '_onBtnStart:'
        
        if self.hasWorkerRunning():
            return
        
        proj = self._getSelectedProject()
        if proj:
            if QtGui.QMessageBox.Yes == QtGui.QMessageBox.question(None, u"启动项目", 
                                    u"是否要启动项目: %s ?\n\n目标HANA:  %s\n项目状态:  %s"%tuple(proj.get_config()[:3]), 
                                   buttons=QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, 
                                   defaultButton=QtGui.QMessageBox.Yes):
                self._start_project(proj)
        else:
            QtGui.QMessageBox.information(None, u"提醒", u"请先选择一个项目!", 
                                          buttons=QtGui.QMessageBox.Ok)
        self._tb.setFocus()
        
    def _start_project(self, proj):
        self.sig_start_done.connect(self._start_project_done)
        self.woker = Worker(proj.start, "Start project", self.sig_start_done)
        self.woker.start()
        self._start_timer(u'启动 %s 中'%proj.get_name())
    def _start_project_done(self):
        self._refresh_data()
        self._stop_timer()
        
    def _stop_project(self, proj):
        self.sig_stop_done.connect(self._stop_project_done)
        self.woker = Worker(proj.stop, "Stop project", self.sig_stop_done)
        self.woker.start()
        self._start_timer(u'停止 %s 中'%proj.get_name())
    def _stop_project_done(self):
        self._refresh_data()
        self._stop_timer()
                
    def _start_timer(self, txt):
        self.title = self.topLevelWidget().windowTitle()
        self.timer_txt = txt
        self.timer_count = 0
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self._update_timer)
        self.timer.start(500)
        
    def _update_timer(self):
        self.timer_count = self.timer_count + 1
        self.topLevelWidget().setWindowTitle(self.title + '(%s%s)'%(self.timer_txt, '.'*(self.timer_count%7)))
        
    def _stop_timer(self):
        self.timer.stop()
        self.topLevelWidget().setWindowTitle(self.title)
            
    def _onBtnStop(self):
        print '_onBtnStop:'
        if self.hasWorkerRunning():
            return
        proj = self._getSelectedProject()
        if proj:
            if QtGui.QMessageBox.Yes == QtGui.QMessageBox.question(None, u"停止项目", 
                                    u"是否要停止项目: %s ?\n\n目标HANA:  %s\n项目状态:  %s"%tuple(proj.get_config()[:3]),
                                   buttons=QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, 
                                   defaultButton=QtGui.QMessageBox.Yes):
                self._stop_project(proj)
        else:
            QtGui.QMessageBox.information(None, u"提醒", u"请先选择一个项目!", 
                                          buttons=QtGui.QMessageBox.Ok)
        self._tb.setFocus()
            
    def _onBtnRefresh(self):
        self._log("Start refresh")
        
        if self.hasWorkerRunning():
            return
        
        
        self._refresh_data()
        #pb = WaitingWindow('')
        #pb.setModal(True)
        #pb.exec_()
        
            
    def _onBtnCheckLog(self):
        print '_onBtnCheckLog:'
        proj = self._getSelectedProject()
        if proj:
            txt = proj.get_log()
            lw = LogWindow(self.topLevelWidget())
            lw.setText(txt)
            lw.exec_()
            
        self._tb.setFocus()
        
    def _onBtnCheckCCL(self):
        print '_onBtnCheckCCL:'
        proj = self._getSelectedProject()
        if proj:
            txt = proj.get_ccl()
            lw = LogWindow(self.topLevelWidget())
            lw.setText(txt)
            lw.exec_()
            
        self._tb.setFocus()
    def _onBtn10Minutes(self):
        print '_onBtn10Minutes:'
        proj = self._getSelectedProject()
        if proj:
            txt = proj.get_lasted_insert_status()
            lw = LogWindow(self.topLevelWidget())
            lw.setText(txt)
            lw.exec_()
            
    def _addLog(self, msg):
        self._edit_msg.append(msg)
        scrollbar = self._edit_msg.verticalScrollBar();
        scrollbar.setSliderPosition(scrollbar.maximum());
        
    def _getSelectedProject(self):
        index = self._tb.currentRow()
        if index >= 0 and len(self.projects) > index:
            return self.projects[index]
        else:
            return None