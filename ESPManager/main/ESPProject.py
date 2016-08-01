#coding:utf-8

'''
Created on 2015年11月25日

@author: I321761
'''

import re
import time, datetime
    
class ESPProject():
    alias = {
             '10.128.184.142':'(TPD)',
             '10.128.184.214':'(TPE)',
             '10.128.184.174':'(TPQ)',
             '10.128.184.250':'(TPT)',
             }
    
    def __init__(self, name, status, cmdAgent):
        self.configs = [name, '', status, '', ''] #name, hana, status, table, zmq
        self._cmd = cmdAgent
        self._init_config()
        
    def __lt__(self, other):
        return self.get_name() < other.get_name()
    def _init_config(self):
        #ret, out, err = self._cmd.execute("cat %s.ccl | grep JdbcUrl | awk -F '//' '{print $2}' | awk -F ':' '{print $1}'"%self.get_name())
        ret, out, err = self._cmd.execute("grep = %s.ccl"%self.get_name())
        print out
        if out:
            hana, table, zmq = '', '', ''
            for i in out:
                try:
                    if 'jdbc' in i:
                        hana = i.split('//')[1].split(':')[0]
                    if 'InsertTable' in i:
                        table = i.split("'")[1]
                    if 'ZMQUrl' in i:
                        zmq = i.split('tcp://')[1].split("'")[0]
                except Exception, e:
                    print e

            self.configs[1] = self.alias.get(hana, '') + hana
            self.configs[3] = table
            self.configs[4] = zmq
    def set_status(self, stat):
        self.configs[2] = stat
    def get_config(self):
        return self.configs
    def get_name(self):
        return self.configs[0]

    def start(self):
        ret, out, err = self._cmd.execute('./esp_inst.sh proj_reload %s'%self.get_name())
        print 'Project start:%s'%self.get_name()
        return ret
    
    def stop(self):
        print 'Project stop:%s'%self.get_name()
        ret, out, err = self._cmd.execute('./esp_inst.sh proj_stop %s'%self.get_name())
        return ret
    
    def delete(self):
        pass
    
    def tail(self):
        ret, out, err = self._cmd.execute('tail -n 100 ../../projects/`ls ../../projects | grep espn_`/nicwsp.%s.0/stdstreams.log'%self.get_name())
        return ''.join(out)
    
    def get_log(self):
        ret, out, err = self._cmd.execute('cat ../../projects/`ls ../../projects | grep espn_`/nicwsp.%s.0/stdstreams.log'%self.get_name())
        return ''.join(out)
    def get_ccl(self):
        ret, out, err = self._cmd.execute('cat %s.ccl'%self.get_name())
        return ''.join(out)
    def get_lasted_insert_status(self):
        ret, out, err = self._cmd.execute('grep "Worker.doInsertTask" ../../projects/`ls ../../projects | grep espn_`/nicwsp.%s.0/stdstreams.log | tail -n 20'%self.get_name())
        if not out:
            print 'No out data'
            return ''
        time_count = []
        for line in out:
            mr = re.match(r"(.+) INFO .*] (\d+) Rows, Used: (\d+) ms", line)
            if not mr:
                mr = re.match(r"(.+) INFO .* (\d+) Rows, Used: (\d+)", line)
                
            if not mr:
                print "Not matched:%s"%line
            else:
                dt, count, used =  mr.groups()[:3]
                count = long(count)
                dt = datetime.datetime.strptime(dt, '%m-%d-%Y %H:%M:%S.%f') + datetime.timedelta(hours=8)
                dt = dt.strftime('%Y-%m-%d %H:%M:%S')
                time_count.append(u'%s: 插入%s条， 用时%s毫秒\r\n'%(dt, count, used))
        head = u"*"*10 + u"  HANA:%s  表:%s  "%(self.configs[1], self.configs[3]) +   u"*"*10 + u"\r\n"*3
        return head + ''.join(time_count)

