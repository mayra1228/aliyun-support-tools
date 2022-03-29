#!/usr/bin/python
# -*- coding:utf-8 -*-
# @Time   : 2019/7/2 11:08 AM
# @Author : mayra.zhao
# @File   : AWSCnf.py
import ConfigParser
from base64 import b64decode

class AWSCnf(object):
    def __init__(self,cnffile,project):
        self.project = project
        self.awscnf = {}
        self.status = True
        try:
           config = self.ReadConfig(cnffile)
           self.awscnf['id'] = str(self.Decode(config.get(project, "ACCESS_ID"),SECRET))
           self.awscnf['key'] = str(self.Decode(config.get(project, "ACCESS_KEY"),SECRET))
           self.awscnf['region'] = config.get(project, "region")
        except Exception,e:
           print('*** Caught exception - Configuration File Error: %s :\n%s: %s\n' % (cnffile ,e.__class__, e))
           self.status = False

    def ReadConfig(self,cnfconfig):
        config = ConfigParser.ConfigParser()
        config.readfp(open(cnfconfig))
        return config

    def Decode(self,orig,key):
        """
        for safe: read config file & decode password
        """
        strorg = b64decode(orig.encode('utf-8'))
        strlength=len(strorg)
        keylength=len(key)
        hh=[]
        for i in range(strlength):
            hh.append((ord(strorg[i])-ord(key[i%keylength]))%256)
        return ''.join(chr(i) for i in hh).decode('utf-8')