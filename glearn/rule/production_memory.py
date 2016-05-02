#!/usr/bin/env python
# -*- coding: utf-8 -*- "
import os
import sys
import getopt
import collections
import csv , ujson
import re
from time import time
from datetime import datetime

sys.path.append( os.path.join( os.path.abspath(os.path.dirname(__file__)) , '../../dependence'))

from distutils.util import get_platform
sys.path.insert(0, "ahocorasick-0.9/build/lib.%s-%s" % (get_platform(), sys.version[0:3]))
import ahocorasick
import ahocorasick.graphviz

sys.path.append( os.path.join( os.path.abspath(os.path.dirname(__file__)) , '../..'))
from glearn.sqlite import orm
# from glearn.resources.property_items import PropertyItems
from glearn.specification.spec_template import specificationTemplate

reload(sys)                         #  
sys.setdefaultencoding('utf-8')     # 


class RegexPattern(object):
	"""docstring for RegexPattern"""
	def __init__(self, pattern, regrex, substitute):
		super(RegexPattern, self).__init__()

		self.pattern = pattern
		self.regrex = regrex
		self.substitute = substitute

		self.prog = re.compile(  self.regrex )
		
class RegexMatcher(object):
	"""docstring for RegexMatcher"""
	def __init__(self):
		super(RegexMatcher, self).__init__()
		self.category_regexPattern_dict = self.__load_regex()

	def __load_regex(self):
		# {"25.11":[RegexPattern(),...],...}
		category_regexPattern_dict = collections.defaultdict(list)

		for p in orm.CrfPattern.fetch_patterns():
			category, pattern, regrex, substitute = p
			category_regexPattern_dict[category].append( RegexPattern( pattern, regrex, substitute) )

		return category_regexPattern_dict

	def matching(self, category, doc):
		""" unused """
		for pat in self.category_regexPattern_dict[category]:
			prog = pat.prog
			substitute = pat.substitute

			match = prog.search( doc )
			if match:
				print match.group(),substitute,pat.regrex
				prog_dict = ujson.loads( prog.subn( substitute, match.group())[0] )
				return prog_dict
		return dict()

class ExactMatcher(object):
	"""docstring for ExactMatcher"""
	def __init__(self):
		super(ExactMatcher, self).__init__()
		self.trees = dict()

	def make_tree(self, category, templates):
		tree = ahocorasick.KeywordTree()
		tree.add('!@#$%^&*') # make() can not be called until at least one string has been add()ed.
		for template in templates:
			tree.add(template)
		print("Ahocorasick KeywordTree Making: ---"+category)
		tree.make()
		print('\n'+'=' * 80)
		
		self.trees[category] = tree

	def matching(self, category, doc):
		""" 规格或型号完全匹配 """
		# 如果规格模板是从redis中读取，则不需要为category而make_tree
		templates,from_redis = specificationTemplate.retrieve_templates(category)
		if not from_redis:
			self.make_tree(category, templates)

		if isinstance(doc, unicode):
			doc = doc.encode('utf-8')
		try:
			tree = self.trees[category]
		except KeyError:
			return {"XXX":''}
		for match in tree.findall_long(doc):
			beg,end = int(match[0]),int(match[1])
			word = unicode(doc[beg:end].strip())
			return {"XXX":word}
		return {"XXX":''}

class Rules(object):
	""" 获取规则的接口 """
	regex_matcher = RegexMatcher()
	exact_matcher = ExactMatcher()

def main():
	# re = RegexMatcher()
	# print re.category_regexPattern_dict
	# print re.matching('25.11',u'铝芯交联聚氯乙烯绝缘聚氯乙烯钢带铠装护套电力电缆	VLV2-22	3*300+1*150')
	# print re.matching('25.11',u'3*120+1') #u'3\xd7120+1'
	# print re.matching('25.11',u'你好吗：205.0×240.0×240.0mm生活')

	exact_matcher = ExactMatcher()
	doc = "电缆终端头ZR-YJV-5x6"
	doc = "电缆终端头ZR-YJV22-5x6"
	# import pdb;pdb.set_trace()
	print exact_matcher.matching('25.11',doc)
	print exact_matcher.matching('25.11',doc)
	print exact_matcher.matching('16.01',doc)
	print exact_matcher.matching('16.01',doc)


if __name__ == "__main__":
	main()
