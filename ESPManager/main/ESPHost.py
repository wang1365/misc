#coding:utf-8
'''
Created on 2015年11月25日

@author: I321761
'''

import paramiko
from CMDAgent import CMDAgent
from ESPProject import *

class ESPHost():
    def __init__(self, hostinfo, logger):
        self._hostinfo = hostinfo
        self._logger = logger
        self._connected = False
        self._ssh = paramiko.SSHClient()
        self._ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self._cmd = CMDAgent(self._ssh, logger)
        self._projects = []
    
    def _log(self, msg):
        self._logger.log(msg)
        
    def init(self):
        if not self._connected:
            self.connect()
        ret, out, err = self._list_project_name()
        self._log( "All projects:%r"%out)
        if out:
            self._projects = [ESPProject(i, u'未加载', self._cmd) for i in out]
            self._update_projects_status()

    def connect(self):
        ret = False
        err = ''
        
        self._log('\n'*2+'*'*10+'Start connect host:%s, %s, %s'%(self._hostinfo['ip'], self._hostinfo['user'], self._hostinfo['password'])+'*'*10)
        try:
            self._ssh.connect(self._hostinfo['ip'], username=self._hostinfo['user'], password=self._hostinfo['password'])
            self._log( 'host connect success:%r'%self._hostinfo['ip'])
            ret = True
        except Exception, e:
            self._log('host connect failed:%r'%e)
            err = str(e)
        self._connected = ret
        return (self._connected, err)
        
    def _on_connected(self):
        #self._enter_espn()
        #self._pwd()
        self._list_projects()
        #self._get_projects_status()
         
    def disconnect(self):
        self._ssh.close()
        self._connected = False
    
    def _list_project_name(self):
        ret, out, err = self._cmd.execute('ls | grep ccl')
        if out:
            #out = [i.strip('.ccl\n') for i in filter(lambda x: 'proj_a_' not in x, out)]
            out = [i.strip('.ccl\n') for i in out if 'proj_a_' not in i]
            out.sort(reverse = True)
        return (ret, out, err)
             
    def _update_projects_status(self):
        ret, out, err = self._cmd.execute('./esp_inst.sh stat')
        if out:
            for stat_info in filter(lambda x : u'===> Found' in x, out):   
                s = stat_info.split(' ')
                if len(s) == 11:
                    status = self._status_to_cn(s[10])
                    self._log( 'Update %s ==> %s'%(s[8].strip(), status))
                    self.get_project(s[8].strip()).set_status(status)
                    
    def _status_to_cn(self, status):
        if 'running' in status:
            return u'运行中'
        elif '' in status:
            return u'停止'
        else:
            return u'未加载'
        
    def get_project(self, name):
        if not self._projects:
            self._log( 'project is null')
            return None
        for i, proj in enumerate(self._projects):
            if proj.get_name() == name:
                return proj
        return None
    
    def get_projects(self):
        return self._projects