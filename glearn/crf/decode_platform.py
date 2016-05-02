#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys

class Decode(object):
	@classmethod
	def decode(self, tagger, doc):
		""" Pay what you owe,and what you’re worth you’ll know.
		# doc = '\xce\xa6\toth\n200\tm'
		2014/11/21
		"""
		doc = doc.strip()

		output = ''
		conllPhase_list = doc.split('\n\n') # 一条decode格式语句词组间的分隔是\n\n
		for conllPhase_str in conllPhase_list:
			conllPhase_str = conllPhase_str.strip()
			if conllPhase_str == '':
				continue
			output += Decode.__parse(tagger,conllPhase_str)
		return output

	@classmethod
	def __parse(self, tagger, conllPhase_str):
		tagger.clear()

		token_list = conllPhase_str.split('\n')
		for token in token_list:
			tagger.add(str(token))
		tagger.parse()

		size = tagger.size()
		xsize = tagger.xsize()
		ysize = tagger.ysize()

		# import pdb;pdb.set_trace()
		res = ''
		for i in range(0, (size )):
		    for j in range(0, (xsize-1)): # xsize=2是conllPhase_str横向上的维度
		      res += str(tagger.x(i, j)) + "\t" # tagger.x以矩阵形式存储着conllPhase_str，行i取值范围[0,size],列j取值范围[0,xsize-1]
		    chunk_tag = tagger.y2(i)
		    res += chunk_tag + "\t" #已预测组块标识

		    for j in range(0, (ysize)): #遍历所有组块标识
		        if tagger.yname(j) == chunk_tag:
		            res += str(tagger.prob(i,j))
		    res += '\n'
		return res	

