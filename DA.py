# -*- encoding: utf-8 -*-
import os
import sys
import zlib
import urllib2
import json
from xml.dom import minidom

default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
	reload(sys)
	sys.setdefaultencoding(default_encoding)

def getURLContent(url):
	try:
		headers = {'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'}
		req = urllib2.Request(url = url,headers = headers)
		content = urllib2.urlopen(req).read()
	except:
		return 0
	return content

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

def getSign(params, appkey, AppSecret = None):
	params['appkey'] = appkey
	data = "";
	_data = params.keys()
	_data.sort()
	for key in _data:
		if data != "":
			data += "&"
		data += key + "=" + params[key]
	if AppSecret == None:
		return data
	m = hashlib.md5()
	m.update(data + AppSecret)
	return data + '&sign=' + m.hexdigest()

class Vedio():
	def __init__(self, m_aid = None, m_page = None):
		if m_aid:
			self.aid = m_aid
		if m_page:
			self.page = m_page

	aid = None #av号 int
	page = None    #页码 int
	title = None   #标题 string
	description = None  #介绍 string
	tag = None  #标签 list
	cover = None  #封面图url string
	created_at = None   #视频发布时间 string
	play_num = None    #播放次数 int
	comment_num = None #评论数 int
	danmaku_num = None #弹幕数 int
	favor_num = None   #收藏数 int
	credits = None  #评分 int
	coins = None   #硬币 int
	v_from = None   #视频来源 string
	mid = None #投稿人ID int
	author = None #投稿人 string
	cid = None  #弹幕id int
	offsite = None  #flash播放调用地址 string
	favorited = None #当前账号收藏状态 bool

	danmaku_limit = None #弹幕上限 int
	danmaku = None  #弹幕 list
	comments = None #评论 list

	def printVedioInfo(self):
		print 'av:', self.aid
		print 'title:', self.title
		print 'cid:', self.cid
		print 'danmaku num:', self.danmaku_num, "\n"

	def fetchDanmaku(self, save = True, getnew = False):
		filename = "%d.xml"%(self.cid)
		url = "http://comment.bilibili.cn/%d.xml"%(self.cid);
		content = ""
		hasfile = os.path.isfile(filename)

		#是否强制重新获取
		if getnew or not hasfile:
			print 'get danmaku:', url
			content = zlib.decompressobj(-zlib.MAX_WBITS).decompress(getURLContent(url))
		else :
			try :
				print 'read local danmaku:', filename
				with open(filename, 'r') as f:
					content = f.read()
			except :
				print 'get danmaku:', url
				content = zlib.decompressobj(-zlib.MAX_WBITS).decompress(getURLContent(url))

		#是否需要存本地xml
		if save and not hasfile:
			with open(filename, 'w') as f:
				f.write(content)

		dom = minidom.parseString(content)
		root = dom.documentElement
		dSets = root.getElementsByTagName('d')
		self.danmaku = []
		for d in dSets:
			plist = d.getAttribute('p').split(',')
			dm = Danmaku()
			dm.time = float(plist[0])
			dm.d_type = int(plist[1])
			dm.fontsize = int(plist[2])
			dm.color = int(plist[3])
			dm.timestamp = int(plist[4])
			dm.pool = int(plist[5])
			dm.uid = plist[6]
			dm.did = int(plist[7])
			dm.d_content = d.firstChild.data
			self.danmaku.append(dm)
		self.danmaku.sort(lambda x,y: cmp(x.time, y.time))

	def fetchHistoryDanmaku(self):
		pass

	def printDanmaku(self):
		for d in self.danmaku:
			print d.time, d.d_content

	def getDanmaku(self):
		return self.danmaku

class Danmaku():
	def __init__(self):
		pass
	time = None;    #弹幕发送相对视频时间 float
	d_type = None;    #弹幕类型：1~3滚动弹幕、4底端弹幕、5顶端弹幕、6逆向弹幕、7精准定位、8高级弹幕 int
	fontsize = None;    #字号：12非常小,16特小,18小,25中,36大,45很大,64特别大（默认25）int
	color = None;   #颜色：不是RGB而是十进制 int
	timestamp = None;   #Unix时间戳 int
	pool_type = None;    #弹幕池类型：0普通 1字幕 2特殊 int
	uid = None; #发送者ID string
	did = None; #弹幕在数据库的ID int
	d_content = None;   #弹幕内容 string

def getVedioInfo(aid, page, appkey, AppSecret = None, fav = None):
	paras = {"id":getString(aid), "page":getString(page)}
	if fav != None:
		paras['fav'] = fav
	url = 'http://api.bilibili.cn/view?' + getSign(paras, appkey, AppSecret)
	jsoninfo = JsonInfo(url)
	vedio = Vedio(aid, page)
	vedio.title = jsoninfo.getValue('title')
	vedio.description = jsoninfo.getValue('description')
	vedio.tag = []
	taglist = jsoninfo.getValue('tag')
	if taglist != None:
		for tag in taglist.split(','):
			vedio.tag.append(tag)
	vedio.cover = jsoninfo.getValue('pic')
	vedio.created_at = jsoninfo.getValue('created_at')
	vedio.play_num = jsoninfo.getValue('play')
	vedio.comment_num = jsoninfo.getValue('review')
	vedio.danmaku_num = jsoninfo.getValue('video_review')
	vedio.favor_num = jsoninfo.getValue('favorites')
	vedio.credits = jsoninfo.getValue('credit')
	vedio.coins = jsoninfo.getValue('coins')
	vedio.v_from = jsoninfo.getValue('from')
	vedio.mid = jsoninfo.getValue('mid')
	vedio.author = jsoninfo.getValue('author')
	vedio.cid = jsoninfo.getValue('cid')
	vedio.offsite = jsoninfo.getValue('offsite')
	vedio.favorited = jsoninfo.getValue('favorited')
	return vedio

def DA(d_list):
	keyword_hit_dict = {}
	for d in d_list:
		sentence = d.d_content
		#TODO:先判断整句是否匹配OOXX模式，如匹配，加入dict
		#分词，提取关键词加入dict
		if sentence in keyword_hit_dict:
			keyword_hit_dict[sentence]["hits"] += 1
			keyword_hit_dict[sentence]["occur"].append(d.time)
		else:
			keyword_hit_dict[sentence] = {"hits":1, "occur":[d.time]}
	return sorted(keyword_hit_dict.items(), lambda x, y: -cmp(x[1]["hits"], y[1]["hits"]))

def main():
	avid = 140460
	page = 1
	appkey = "03fc8eb101b091fb"

	vedio = getVedioInfo(avid, page , appkey, None, None)
	vedio.fetchDanmaku(save = True)
	vedio.printVedioInfo()
	# vedio.printDanmaku()
	keyword_hits = DA(vedio.getDanmaku())
	for k,v in keyword_hits:
		print k, v["hits"],
		for t in v["occur"]:
			print t,
		print "\n"

if __name__ == '__main__':
	main()