#coding:utf-8
'''
Created on 2015年12月8日

@author: I321761
'''

from PyQt4 import QtGui, QtCore
import ConfigParser
import os, sys
import json
from main.Hana import Hana


class HanaWindow(QtGui.QWidget):
    config_file = './hanacmds.ini'
    
                    
    def __init__(self, hanainfo, parent = None):
        self.hanainfo = hanainfo
        super(HanaWindow, self).__init__(parent)
        
        self._init_config()
        self._init_ui()
        self._init_hana()
        self._refresh_tree()
        
    def _init_hana(self):
        self.hana = Hana(self.hanainfo)
        
    def _init_ui(self):
        splitH = QtGui.QSplitter(QtCore.Qt.Horizontal)
        splitV = QtGui.QSplitter(QtCore.Qt.Vertical)
        
        wTree = self._init_ui_tree()
        wCmd = self._init_ui_query_cmd()
        wResult = self._init_ui_query_result()
        wBtn = self._init_ui_buttons()
        wColumns = self._init_ui_table_columns()
        self._init_ui_context_menu()
        
        h_layout1 = QtGui.QHBoxLayout()
        h_layout1.addWidget(wColumns, 1)
        h_layout1.addWidget(wResult, 5)
        h_widget1 = QtGui.QWidget()
        h_widget1.setLayout(h_layout1)
        
        h_layout2 = QtGui.QHBoxLayout()
        h_layout2.addWidget(wCmd)
        h_layout2.addWidget(wBtn)
        h_widget2 = QtGui.QWidget()
        h_widget2.setLayout(h_layout2)
        
        splitV.addWidget(h_widget1)
        splitV.addWidget(h_widget2)

        splitV.setStretchFactor(0, 3)
        splitV.setStretchFactor(1, 1)
        splitH.addWidget(wTree)
        splitH.addWidget(splitV)
        splitH.setStretchFactor(0, 1)
        splitH.setStretchFactor(1, 3)
        
        layout = QtGui.QVBoxLayout()
        layout.addWidget(splitH)
        self.setLayout(layout)
    
    def _init_ui_tree(self):
        print '_init_ui_tree'
        self.wTree = QtGui.QTreeWidget()
        self.wTree.itemDoubleClicked.connect(self._onTreeItemDbClicked)
        self.wTree.itemClicked.connect(self._onTreeItemClicked)
        
        return self.wTree
    
    def _init_ui_context_menu(self):
        print '_init_context_menu'
        self.wTree.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.wTree.customContextMenuRequested.connect(self._on_tree_contextMenuEvent)
        self.sessionMenu = QtGui.QMenu(self)
        self.cmdMenu = QtGui.QMenu(self)
        
        menu1 = [('Add category', self._on_add_category), 
                 ('Delete category', self._on_add_category), 
                 ('Add command', self._on_add_cmd)]
        for info in menu1:
            act = QtGui.QAction(info[0], self)
            act.triggered.connect(info[1])
            self.sessionMenu.addAction(act)
            
        menu1 = [('Delete commands', self._on_del_cmd),]
        for info in menu1:
            act = QtGui.QAction(info[0], self)
            act.triggered.connect(info[1])
            self.cmdMenu.addAction(act)
    def _init_ui_table_columns(self):
        self.wColumns = QtGui.QTextEdit()
        return self.wColumns
    
    def _init_ui_buttons(self):
        self.bnExecute = QtGui.QPushButton('Execute')
        self.bnExecute.clicked.connect(self._onBtnExecuteClicked)
        return  self.bnExecute
    
    def _onBtnExecuteClicked(self):
        cmd = self.wCmd.toPlainText().toUtf8().data()
        print '_onBtnExecuteClicked:', cmd
        if cmd:
            self.wResult.setText(self.hana.execute(cmd)[1])
    
    def _on_add_category(self):
        print '_on_add_category'
    def _on_add_cmd(self):
        print '_on_add_cmd'
        item = self.wTree.currentItem()
        if not item:
            return
        section = item.text(0).toUtf8().data()
        
        cmd_alias, ret = QtGui.QInputDialog.getText(self, 'Alias', "Input command's alias name", mode=QtGui.QLineEdit.Normal)
        if not ret:
            return
        cmd_alias = cmd_alias.toUtf8().data()
        
        cmd, ret = QtGui.QInputDialog.getText(self, 'SQL', "Input SQL", mode=QtGui.QLineEdit.Normal)
        if not ret:
            return
        
        cmd = cmd.toUtf8().data()
        self._add_command(section, cmd_alias, cmd)
        
    def _on_del_cmd(self):
        print '_on_del_cmd'
        item = self.wTree.currentItem()
        if not item:
            return
        section = item.parent().text(0).toUtf8().data()
        alias = item.text(0).toUtf8().data()
        
        self._del_command(section, alias)
        
    def _add_command(self, session, alias, cmd):
        self.cmds[session][alias] = cmd
        with open(self.config_file, 'wb') as f:
            f.write(json.dumps(self.cmds))
        self._refresh_tree()
        
    def _del_command(self, session, alias):
        print '_on_del_cmd'
        self.cmds[session].pop(alias)
        with open(self.config_file, 'wb') as f:
            f.write(json.dumps(self.cmds))
        self._refresh_tree()
        
    def _on_tree_contextMenuEvent(self, point):
        print 'contextMenuEvent'
        
        item = self.wTree.currentItem()
        if not item:
            return
        
        item_txt = item.text(0).toUtf8().data()
        
        print 'item text:', item_txt
        #root node
        if self.wTree.indexOfTopLevelItem(item) != -1:
            self.sessionMenu.exec_(QtGui.QCursor.pos())
        else:
            self.cmdMenu.exec_(QtGui.QCursor.pos())
    
    def _onTreeItemDbClicked(self, item):
        print '_onTreeItemDbClicked:', item.text(0)
        rootItem = item.parent()
        if rootItem:
            print '==>', rootItem.text(0), item.text(0)
            cmd = self.cmds[rootItem.text(0).toUtf8().data()][item.text(0).toUtf8().data()]
            print cmd
            
            self.wCmd.setHtml('<p><b><font color="#cc1111">%s</font></b></p>'%cmd)
            self.wResult.setText(self._execute_cmd(cmd)[1])
            #self.wResult.setHtml('<p><b><font color="#1111ff">%s</font></b></p>'%self._execute_cmd(cmd))
    
    def _onTreeItemClicked(self, item):
        print '_onTreeItemClicked:', item.text(0)
        rootItem = item.parent()
        if rootItem:
            cmd = self.cmds[rootItem.text(0).toUtf8().data()][item.text(0).toUtf8().data()]
            self.wCmd.setHtml('<p><b><font color="#cc1111">%s</font></b></p>'%cmd)
        else:
            table = item.text(0).toUtf8().data()
            columns = '\r\n'.join(self.hana.get_table_columns(table))
            self.wColumns.setText(columns)
            
            cmd = 'SELECT TOP 10 * FROM "SAPCD_ITRAFFIC"."%s"'%table
            self.wCmd.setHtml('<p><b><font color="#cc1111">%s</font></b></p>'%cmd)
              
    def _refresh_tree(self):
        if not self.wTree:
            return
        
        self.wTree.clear()
        tables = self.hana.get_tables()
        for table in tables:
            print 'Add top level item:', table
            t = QtCore.QStringList(table)
            item = QtGui.QTreeWidgetItem(t)
            self.wTree.addTopLevelItem(item)
            
            for column in self.hana.get_table_columns(table):
                item.addChild(QtGui.QTreeWidgetItem(QtCore.QStringList(column)))
                
                
        #self.wTree.expandAll()
    
    def _init_ui_query_cmd(self):
        self.wCmd = QtGui.QTextEdit()
        
        return self.wCmd
    
    def _init_ui_query_result(self):
        self.wResult = QtGui.QTextEdit()
        self.wResult.setTextColor(QtGui.QColor(11, 11, 255))
        return self.wResult
    
    def _init_config(self):
        self.cmds = {
                     'raw_taxi': {
                                  'top 10':'SELECT TOP 10 SUBSTRING(DEVID, 2), GPS_TIME, RECEIVE_TIME FROM "SAPCD_ITRAFFIC"."sapcd.itraffic.dp.s.db::TAXI.RAW_TAXI" WHERE TO_DATE(RECEIVE_TIME) = CURRENT_UTCDATE ORDER BY RECEIVE_TIME DESC'
                                  },
                     'raw_lpr': {
                                  'top 10':'SELECT TOP 10 RECORD_ID, CAP_TIME, RECEIVE_TIME FROM "SAPCD_ITRAFFIC"."sapcd.itraffic.dp.s.db::FDD.RAW_LPR" WHERE TO_DATE(RECEIVE_TIME) = CURRENT_UTCDATE ORDER BY RECEIVE_TIME DESC'
                                  },
                     'raw_rfid': {
                                  'top 10':'SELECT TOP 10 RECORD_ID, COLLECT_TIME, RECEIVE_TIME FROM "SAPCD_ITRAFFIC"."sapcd.itraffic.dp.s.db::FDD.RAW_RFID" WHERE TO_DATE(RECEIVE_TIME) = CURRENT_UTCDATE ORDER BY RECEIVE_TIME DESC'
                                  },
                     }
        
        if not os.path.exists(self.config_file) or not os.path.isfile(self.config_file):
            with open(self.config_file, 'wb') as f:
                f.write(json.dumps(self.cmds))
        
        with open(self.config_file, 'r') as f:
            self.cmds = json.load(f)
        print 'self.cmds:', self.cmds

        
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    #win.showMaximized()

    
    
    hanas = (
        {'name':'TPD', 'ip':'10.128.184.142', 'user':'SYSTEM', 'password':'Hana67890', 'instance': '00'},
        {'name':'TPE', 'ip':'10.128.184.214', 'user':'SYSTEM', 'password':'Hana67890', 'instance': '00'},  
        )
    for hanainfo in hanas:
            tw = HanaWindow(hanainfo)
    tw.show()       
    sys.exit(app.exec_())