#coding:utf-8
'''
Created on 2015年11月25日

@author: I321761
'''

import os
class CMDAgent():
    def __init__(self, ssh, logger):
        self._ssh = ssh
        self.logger = logger
    def __call__(self, cmd):
        return self.execute(cmd)
    def _log(self, msg):
        self.logger.log(msg)
    def execute(self, cmd):
        stdout, stderr = self._ssh.exec_command('cd /opt/sybase/ESP-5_1/cluster/config/espn;'+cmd)[1:]
        out, err = stdout.readlines(), stderr.readlines()
        msg_out = u''.join([i.replace('\n', os.linesep) for i in out])
        if len(msg_out) < 1024*10:
            self._log('=> %s\n   %r\n   %r'%(cmd, msg_out, err) )
        return (True if not err else False, out, err)