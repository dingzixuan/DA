# -*- coding: utf-8 -*-
import zlib
import urllib2
import json

def getURLContent(url):
	try:
		headers = {'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'}
		req = urllib2.Request(url = url,headers = headers)
		content = urllib2.urlopen(req).read()
	except:
		return 0
	return content

def getString(t):
	if type(t) == int:
		return str(t)
	return t

def getInt(string):
	try:
		i = int(string)
	except:
		i = 0
	return i

def encodeGroupsToJson(g):
	return json.dumps(g)

class JsonInfo():
	def __init__(self, url):
		self.info = json.loads(getURLContent(url))
	def getValue(self, *keys):
		if len(keys) == 0:
			return None
		if self.info.has_key(keys[0]):
			tmp = self.info[keys[0]]
		else:
			return None
		if len(keys) > 1:
			for key in keys[1:]:
				if tmp.has_key(key):
					tmp = tmp[key]
				else:
					return None
		return tmp
	info = None