#!/usr/bin/env python
# coding:utf-8
# autoupdate.py
# Author: Wang Wei Qiang <wwqgtxx@gmail.com>


import sys
import os
import glob

sys.path += glob.glob('%s/*.egg' % os.path.dirname(os.path.abspath(__file__)))

try:
	import gevent
	import gevent.socket
	import gevent.monkey
	gevent.monkey.patch_all()
except (ImportError, SystemError):
	gevent = None
try:
	import OpenSSL
except ImportError:
	OpenSSL = None

from simpleproxy import LocalProxyServer
from simpleproxy import server
from simpleproxy import logging
from simpleproxy import common as proxyconfig
from common import sysconfig as common
from common import FileUtil
from common import Config
from common import config
from common import __config__
from common import __sha1__
from common import __file__
from common import __version__
from makehash import makehash
from sign import verify
from sign import sign

import os
import sys
import re
import ConfigParser
import hashlib
import thread
import urllib2
import random



class Updater(object):
	def __init__(self,serverurl,old_file_sha1_ini,dir):
		proxies = {'http':'%s:%s'%('127.0.0.1', proxyconfig.LISTEN_PORT),'https':'%s:%s'%('127.0.0.1', proxyconfig.LISTEN_PORT)}
		self.opener = urllib2.build_opener(urllib2.ProxyHandler(proxies))
		self.server = str(serverurl)
		self.old_file_sha1_ini = old_file_sha1_ini
		self.dir = dir
	def getfile(self,filename):
		while 1:
			try:
				response = self.opener.open(self.server+filename)
				file = response.read()
				return file
			except Exception as e:
				print e
				return
	def writefile(self,filename,sha1v):
		file = self.getfile(filename)
		path = self.dir+filename
		input = FileUtil.open(path,"r")
		oldfile = input.read()
		input.close()
		output = FileUtil.open(path,"wb")
		output.write(file)
		print 'Update	'+filename+'	OK!'
		output.close()
		input = FileUtil.open(path,"r")
		sha1vv = FileUtil.get_file_sha1(input)
		input.close()
		if sha1v == sha1vv :
			print 'Verify	'+filename+'	OK!'
		else:
			output = FileUtil.open(path,"wb")
			output.write(oldfile)
			print 'Recover	'+filename+'	OK!'
			output.close()
	def update(self):
		oldsha1 = self.old_file_sha1_ini
		path = 'sha1.ini.tmp'
		FileUtil.if_has_file_remove(path)
		output = FileUtil.open(path,"wb")
		tmp = self.opener.open(self.server+'/sha1.ini')
		output.write(tmp.read()) 
		output.close()
		input = FileUtil.open(path,"r")
		tmp2 = input.read()
		input.close()
		hash = self.opener.open(self.server+'/sha1.sign').read()
		print sign(tmp2)
		print hash
		ok = verify(tmp2,hash)
		if not ok:
			print 'Verify Failed!'
			return
		print 'Verify Successful1!'
		newsha1 = Config('sha1.ini.tmp')
		for path, sha1v in newsha1.getsection('FILE_SHA1'):
			if not (sha1v == oldsha1.getconfig('FILE_SHA1',path)):
				path = path.replace('$path$','')
				path = path.replace('\\','/')
				self.writefile(path,sha1v)
		FileUtil.if_has_file_remove(path)



def main():
	dir = FileUtil.cur_file_dir()
	os.chdir(dir)
	sys.stdout.write(common.info())
	sys.stdout.write(proxyconfig.info())
	thread.start_new_thread(server.serve_forever, tuple())
	sha1 = makehash(dir)
	updater = Updater(common.AUTOUPDATE_SERVER[0],sha1,dir)
	updater.update()

	#for path, sha1v in sha1.getsection('FILE_SHA1'):
		#newpath = path.replace('$path$',dir)
		#print newpath + ' = ' + sha1v

if __name__ == '__main__':
	main()