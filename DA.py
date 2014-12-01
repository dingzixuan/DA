#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import util
from biliclass import getVedio
from reg_tmp import regMatch
import jieba
jieba.load_userdict("acg_dict.txt")
import jieba.posseg as pseg
import jieba.analyse

# 二分查找，在从小到大排列的时间序列中找到和target最接近的坐标
def biSearch(a, target):
	low = 0
	high = len(a) - 1
	while low <= high:
		mid = (low + high) / 2
		midVal = a[mid]

		if midVal < target:
			low = mid + 1
		elif midVal > target:
			high = mid - 1
		else:
			return mid
	return high

# 简单将每一句弹幕内容作为key，输出hits数前top个完整弹幕
def DA_getSentenceHits(d_list, top):
	sentence_hit_dict = {}
	for d in d_list:
		sentence = d.d_content
		if sentence in sentence_hit_dict:
			sentence_hit_dict[sentence]["hits"] += 1
			sentence_hit_dict[sentence]["occur"].append(d.time)
		else:
			sentence_hit_dict[sentence] = {"hits":1, "occur":[d.time]}
	return sorted(sentence_hit_dict.items(), lambda x, y: -cmp(x[1]["hits"], y[1]["hits"]))[:top]

# 将整个弹幕内容作为整体，使用结巴分词的关键词提取功能
def DA_getKeyWords(d_list, top):
	contents = ""
	for d in d_list:
		contents += d.d_content + "。"
	jieba.analyse.set_stop_words("stopwords")
	tags = jieba.analyse.extract_tags(contents, topK=top)
	return tags

# 统计关键词，及出现次数，返回前top个结果
def DA_getKeywordsHits(d_list, top):
	stop = [line.strip().decode('utf-8') for line in open('stopwords').readlines() ]	
	keyword_hit_dict = {}
	for d in d_list:
		sentence = d.d_content
		#先判断整句是否匹配模板中定义的模式，如匹配，加入dict
		reg_tmp_key = regMatch(sentence)
		if reg_tmp_key:
			if reg_tmp_key in keyword_hit_dict:
				keyword_hit_dict[reg_tmp_key]["hits"] += 1
				keyword_hit_dict[reg_tmp_key]["occur"].append(d.time)
			else:
				keyword_hit_dict[reg_tmp_key] = {"hits":1, "occur":[d.time]}
			continue	#如果匹配模板，则不再进行分词
		#分词，提取关键词加入dict
		words = jieba.cut(sentence, cut_all=False)	# 分词
		words = set(words)-set(stop)	# 去掉停用词		
		for w in words:
			if w in keyword_hit_dict:
				keyword_hit_dict[w]["hits"] += 1
				keyword_hit_dict[w]["occur"].append(d.time)
			else:
				keyword_hit_dict[w] = {"hits":1, "occur":[d.time]}
	return sorted(keyword_hit_dict.items(), lambda x, y: -cmp(x[1]["hits"], y[1]["hits"]))[:top]

# 关键词按时间序列聚类
# 我是本体！！上面的都是实验！！
WINDOW = 30	# 最小窗口：30s
def DA_getKeywordsGroups(d_list, top):
	stop = [line.strip().decode('utf-8') for line in open('stopwords').readlines() ]	
	keyword_hit_dict = {}
	for d in d_list:
		sentence = d.d_content
		#先判断整句是否匹配模板中定义的模式，如匹配，加入dict
		reg_tmp_key = regMatch(sentence)
		if reg_tmp_key:
			if reg_tmp_key in keyword_hit_dict:
				keyword_hit_dict[reg_tmp_key]["hits"] += 1
				keyword_hit_dict[reg_tmp_key]["occur"].append(d.time)
			else:
				keyword_hit_dict[reg_tmp_key] = {"hits":1, "occur":[d.time]}
			continue	#如果匹配模板，则不再进行分词
		#分词，提取关键词加入dict
		words = jieba.cut(sentence, cut_all=False)	# 分词
		words = set(words)-set(stop)	# 去掉停用词		
		for w in words:
			if w in keyword_hit_dict:
				keyword_hit_dict[w]["hits"] += 1
				keyword_hit_dict[w]["occur"].append(d.time)
			else:
				keyword_hit_dict[w] = {"hits":1, "occur":[d.time]}
	keyword_hit_dict = sorted(keyword_hit_dict.items(), lambda x, y: -cmp(x[1]["hits"], y[1]["hits"]))[:top]
	groups = []	# 要返回的，关键词按时间序列聚类的结果
	for k, keyword in keyword_hit_dict:
		occur_time_list = keyword['occur']
		avg_freq = len(occur_time_list) / (occur_time_list[-1] - occur_time_list[0])
		total = len(occur_time_list)
		while len(occur_time_list) > 1:
			cur_window = WINDOW	#初始滑动窗口大小
			sind = 0    #其实sind在当前算法中一直未0,stime也不会变
			stime = occur_time_list[sind]
			etime = stime + cur_window
			eind = biSearch(occur_time_list, etime)
			etime = occur_time_list[eind]	# 修正etime
			cur_window = etime - stime	# 修正当前窗口大小
			while cur_window == 0:
				eind += 1
				etime = occur_time_list[eind]
				cur_window = etime - stime
				continue
			cur_window_freq = (eind - sind + 1) / cur_window	# 当前窗口频率
			# 如果当前窗口内的频率小于平均频率，则向后滑动窗口
			if cur_window_freq < avg_freq:	
				occur_time_list.pop(0)
				continue
			# 否则尝试向后加大窗口
			else:
				while True:
					try_eind = eind + 1
					if try_eind >= len(occur_time_list): break	# 如果已越界则结束循环
					# 尝试向后平移
					try_cur_window = occur_time_list[try_eind] - occur_time_list[sind]
					try_cur_window_freq = (try_eind - sind + 1) / try_cur_window
					# 如果尝试向后加入一个新元素后：
					# 1.新加入元素的时间与当前窗口最后一个元素的时间相差不超过一个窗口(原始最小窗口)
					# 2.且保证新freq不小于平均值，则加入（可能小于当前频率，考虑相对下降百分比）
					if (occur_time_list[try_eind]-occur_time_list[eind] < WINDOW) and (try_cur_window_freq >= avg_freq):
						eind = try_eind
						etime = occur_time_list[eind]
						cur_window = try_cur_window
						cur_window_freq = try_cur_window_freq
					# 如果尝试向后加入一个新元素后导致freq小于平均值，则不加入,结束循环
					else:
						break		
				# 循环结束，将当前window加入group中
				# 考虑当前window中的总数，如果不到total的20%，则不考虑加入
				hits = eind - sind + 1
				if total / hits > 5:
					occur_time_list = occur_time_list[eind+1:]
					continue
				# TODO: 从occur区间截取绘图点
				area = {
					"keyword": k,
					"hits": hits,
					"freq":cur_window_freq,
					"start_time":stime,
					"end_time":etime
				}
				groups.append(area)
				occur_time_list = occur_time_list[eind+1:]
	return groups

def main():
	avid = 140460
	page = 1
	appkey = "03fc8eb101b091fb"

	vedio = getVedio(avid, page , appkey, None, None)
	vedio.fetchDanmaku(save = True)
	vedio.printVedioInfo()
	keyword_groups = DA_getKeywordsGroups(vedio.getDanmaku(), 30)
	for area in keyword_groups:
		print "keyword:", area["keyword"]
		print "hits:", area["hits"]
		print "start:", area["start_time"]
		print "end:", area["end_time"]
		print "freq:", area["freq"]

if __name__ == '__main__':
	main()
