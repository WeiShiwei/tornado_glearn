#!/usr/bin/env python
# -*- coding: utf-8 -*- 
# Copyright (c) 2014 Qtrac Ltd. All rights reserved.

import os
from jpype import *
import global_variables as gv

import collections
WordFlag = collections.namedtuple("WordFlag","word flag")

class JPype(object):
	"""docstring for JPype"""
	
	def __init__(self, jarpath = gv.jarpath):
		super(JPype, self).__init__()
		if not isJVMStarted(): 
			startJVM(getDefaultJVMPath(),"-ea", 
				"-Djava.class.path=%s" % (':'.join([os.path.join(jarpath,'ansj_seg-2.0.7.jar'),
													os.path.join(jarpath,'nlp-lang-0.3.jar'),
													os.path.join(jarpath,'tree_split-1.4.jar')])))
		self.ToAnalysis = JClass("org.ansj.splitWord.analysis.ToAnalysis")
		

	def __del__(self):
		shutdownJVM()
		
	def cut(self, content):
		""" 
		content:
		String str = u"合金圆锯片  50/100KW WQ100-App4mm"
		
		ansj_result:
		[u'\u5408\u91d1/n', u'\u5706\u952f\u7247/nz', u'', u'', u'50/m', u'/', u'100/m', u'kw/en', u'', u'wq/en', u'100/m', u'-', u'app/en', u'4/m', u'mm/en']

		ws:
			合金 n
			圆锯片 nz
			50 m
			/ oth
			100 m
			KW en
			WQ en
			100 m
			- oth
			App en
			4 m
			mm en

		confused example:
		S4 63ppr稳态管  公称外径：65（mm） 壁厚：7.4（mm）长度：4（m）产品规格：63
		[s/en, 4/m,  , 63/m, ppr/en, 稳态/n, 管  /nr, 公称/nz, 外径/gm, ：/w, 65/m, （/w, mm/en, ）/w,  , 壁/ng, 厚/a, ：/w, 7.4/m, （/w, mm/en, ）/w, 长度/n, ：/w, 4/m, （/w, m/en, ）/w, 产品规格/nz, ：/w, 63/m]
		
		content = u"输入功率:150-250W,电压220v"
		[输入/v, 功率/n, :, 150/m, -, 250/m, w/en, ,, 电压/n, 220/m, v/en]
		[u'\u8f93\u5165/v', u'\u529f\u7387/n', u':', u'150/m', u'-', u'250/m', u'w/en', u'', u'', u'\u7535\u538b/n', u'220/m', u'v/en']

		"""
		content = unicode(content)

		ansj_result = [wordflag.strip() for wordflag in self.ToAnalysis.parse(content).toString().strip('[]').split(', ')]
		pos_beg = 0
		ws = list()
		for elem in ansj_result:
		    if elem == u'':
		        pos_beg += 1
		        continue
		    elif len(elem)==1:
		        pos_beg += 1
		        ws.append( WordFlag(elem,'oth') )
		    else:
		    	try:
		    		index = elem.rindex(u'/')
		    		word = elem[:index]
		    		flag = elem[index+1:]
		    		# word,flag = elem.split(u'/') # ValueError: too many values to unpack
		    	except Exception, e:
		    		print "elem:",elem
		    		print "ansj_result:",ansj_result
		    		# raise e
		    		return list()
		        
		        origin_word = content[pos_beg:pos_beg+len(word)]
		        origin_word = origin_word.strip()
		        origin_word = ''.join(origin_word.split())
		        ws.append(WordFlag(origin_word,flag))

		        pos_beg += len(word)

		# for e in ws:
		# 	print e.word,e.flag
		return ws


if __name__ == '__main__':
	# content = u'S4 63ppr稳态管  公称外径：65（mm） 壁厚：7.4（mm）长度：4（m）产品规格：63'
	# content = u'S4 63ppr稳态管  公称外径：65（mm） 壁厚：7.4（mm）长度：4（m）产品规格：63'
	content = u'一体化太阳能庭院灯 SHTY-205 5W 太阳能电池板 最大功率 18V10W (高效单晶硅) 太阳能电池板 使用寿命 25 年 电池 类型 锂电池（12.8V/4AH A品山木） 电池 使用寿命 5 年 LED灯(不带人体感应器) 最大功率 12V 5W LED灯(不带人体感应器) LED芯片品牌 台湾晶圆高亮度 LED灯(不带人体感应器) 流明(LM) 500-550lm LED灯(不带人体感应器) 使用寿命 50000小时 LED灯(不带人体感应器) 发光角度 120° 充电时间 太阳能充电 6小时 (强烈太阳光) "放电时间" 全功率 >12小时 "放电时间" 省电模式 >24小时 工作温度 单位( ℃ ) -30℃~+70℃ 通光量 单位(k) 6000k 安装高度 单位(m) 2.5-3.5m 两灯间距 单位 (m) 7-9m 灯的材质 铝合金 认证 CE / ROHS / IP65 保修期 2年 包装和重量 产品尺寸 480×280×55mm 包装和重量 产品净重 4.5kg 包装和重量 包装盒 中性纸盒 包装和重量 包装尺寸 500×570×370mm 包装和重量 装箱 4套/箱 包装和重量 毛重 22kg 集装箱 20尺柜 1080pcs 集装箱 40尺柜 2250pcs'
	content = u'一体化太阳能庭院灯 SHTY-208 8W 太阳能电池板 最大功率 18V15W (高效单晶硅) 太阳能电池板 使用寿命 25 年 电池 类型 锂电池（12.8V/6AH A品山木） 电池 使用寿命 5 年 LED灯(不带人体感应器) 最大功率 12V 8W LED灯(不带人体感应器) LED芯片品牌 台湾晶圆高亮度 LED灯(不带人体感应器) 流明(LM) 800-880lm LED灯(不带人体感应器) 使用寿命 50000小时 LED灯(不带人体感应器) 发光角度 120° 充电时间 太阳能充电 6小时 (强烈太阳光) "放电时间" 全功率 >12小时 "放电时间" 省电模式 >24小时 工作温度 单位( ℃ ) -30℃~+70℃ 通光量 单位(k) 6000k 安装高度 单位(m) 3-4m 两灯间距 单位 (m) 8-10m 灯的材质 铝合金 认证 CE / ROHS / IP65 保修期 2年 包装和重量 产品尺寸 540×320×55mm 包装和重量 产品净重 5.8kg 包装和重量 包装盒 中性纸盒 包装和重量 包装尺寸 560×570×410mm 包装和重量 装箱 4套/箱 包装和重量 毛重 27kg 集装箱 20尺柜 900pcs 集装箱 40尺柜 1920pcs'
	content = u"-30℃~+70℃ CE / ROHS / IP65"
	content = u"输入功率:150-250W,电压220v"

	ansj_seg = JPype()
	ws = ansj_seg.cut(content)

	print '\n'.join([w.word+'	'+w.flag for w in ws])