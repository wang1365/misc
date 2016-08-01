#coding:utf-8
'''
Created on 2015年12月10日

@author: I321761
'''

import commands, subprocess
import os, sys

class Hana(object):
    def __init__(self, info):
        self.info = info
        self.cmd_file = "cmd.sql.%s"%info['ip']
        self.hdbcmd = r'C:\Program Files\SAP\hdbclient\hdbsql.exe -n %s -i %s -u %s -p %s  -I %s -resultencoding UTF8 ' \
                    %(info['ip'], info['instance'], info['user'], info['password'], self.cmd_file)
 
        self.tables = {}
        
        self._init_tables()
        
    def execute(self, cmd):
        return self._execute(cmd)
    
    def _execute(self, cmd, formated = True):
        print "==>cmd:", cmd
        
        with open(self.cmd_file, 'wb') as f:
            f.write(cmd)
            
        hdbcmd = self.hdbcmd if not formated else self.hdbcmd + ' -A'
        p = subprocess.Popen(hdbcmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()
    
        print 'returncode:', p.returncode
        print 'stdout:', stdout
        print 'stderr:', stderr
        
        return (True if stdout else False, stdout if stdout else stderr)
       
    def get_tables(self):
        tables = self.tables.keys()
        tables.sort()
        return tables
    
    def get_table_columns(self, table):
        return self.tables[table]
    
    def _init_tables(self):
        if self.tables:
            print 'tables not empty, alread queried'
            return self.tables
        
        cmd = 'select table_name, column_name from TABLE_COLUMNS where SCHEMA_NAME = \'SAPCD_ITRAFFIC\''
        ret, output = self._execute(cmd, False)
        print '====>', output
        if ret:
            tl = output.split(os.linesep)[1:]
            
            for t in tl:
                tc = t.split(',')
                if len(tc) == 2:
                    table, column = tc[0].strip('"'), tc[1].strip('"')
                    if not self.tables.has_key(table):
                        self.tables[table] = [column]
                    else:
                        self.tables[table].append(column)
                        
        print '_init_tables', self.tables
    