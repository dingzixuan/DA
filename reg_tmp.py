# -*- coding: utf-8 -*-
import re
import sys
default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
	reload(sys)
	sys.setdefaultencoding(default_encoding)
	
acg_reg_list = [
	{'exp': ur'^(.)\1{3,}.*', 'key':'1'},	#单字符刷屏
	{'exp': ur'^(..)\1{3,}.*', 'key':'2'}, #双字符刷屏
	{'exp': ur'^(...)\1{3,}.*', 'key':'3'}, #三字符刷屏
	{'exp': ur'^(...)\1{3,}.*', 'key':'4'}, #四字符刷屏
	{'exp': ur'^(....)\1{3,}.*', 'key':'5'}, #五字符刷屏
	{'exp': ur'^(.....)\1{3,}.*', 'key':'6'}, #六字符刷屏
	{'exp': ur'.*233*.*', 'key':'233'},	#233后3重复任意多次
	{'exp': ur'[y,Y]{1}[o, O]+', 'key':'YOOOO'},	#YO，O重复一次或更多
	{'exp': ur'(.*\u5927\u6cd5\u597d)', 'key':''}	#XX大法好
]

for acg_reg in acg_reg_list:
	acg_reg['exp'] = re.compile(acg_reg['exp'])

def regMatch(s):
	for acg_reg in acg_reg_list:
		m = acg_reg['exp'].match(s.decode("utf8"))
		if m:
			if acg_reg['key'] == '':
				return m.group(1)
			else:
				return acg_reg['key']
	return None

def main():
	danmaku = "233333333"
	print reg_match(danmaku)

if __name__ == '__main__':
    main()