#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import collections
from time import time
from datetime import datetime
sys.path.append( os.path.join( os.path.abspath(os.path.dirname(__file__)) , '../../dependence'))
# from trie import Trie
# RIGHT_SYMBOL = '@'

from distutils.util import get_platform
sys.path.insert(0, "ahocorasick-0.9/build/lib.%s-%s" % (get_platform(), sys.version[0:3]))
import ahocorasick
import ahocorasick.graphviz

sys.path.append( os.path.join( os.path.abspath(os.path.dirname(__file__)) , '../..'))
from glearn.sqlite import orm

reload(sys)                         #  
sys.setdefaultencoding('utf-8')     # 

class Stemmed(object):
	"""docstring for Stemmed"""
	def __init__(self):
		super(Stemmed, self).__init__()
		self.tree = ahocorasick.KeywordTree()
		self.word_stem_dict = collections.defaultdict(str)
		self.__load_crf_stemmed()
		self.stemmed_updatedTime = datetime(2000, 8, 6, 6, 29, 51, 144126)
		
	def __load_crf_stemmed(self):
		print('\n'+'=' * 80)
		print("Ahocorasick KeywordTree Making: ")
		print(self.tree)
		t0 = time()

		self.tree = ahocorasick.KeywordTree()

		self.word_stem_dict = orm.CrfStemmed.get_word_stem_dict()
		all_key_words = self.word_stem_dict.keys()
		for word in all_key_words:
			self.tree.add(word)
		self.tree.make()

	def stemming(self, doc):
		""" 广义的词干化 """
		# CrfStemmed_updatedTime = orm.CrfStemmed.fetch_latest_updated_time()
		# if CrfStemmed_updatedTime != self.stemmed_updatedTime:
		# 	self.__load_crf_stemmed()
		# 	self.stemmed_updatedTime = CrfStemmed_updatedTime

		doc_res = ''
		if isinstance(doc, unicode):
			doc = doc.encode('utf-8')
		left_margin = 0
		for match in self.tree.findall(doc):
			beg,end = int(match[0]),int(match[1])
			word = unicode(doc[beg:end].strip())
			stem = self.word_stem_dict[word]
			
			doc_res += doc[left_margin:beg]+stem
			left_margin = end
		
		doc_res += doc[left_margin:]
		return doc_res

	# def stemming_docs(self, docs):
	# 	""" 广义的词干化 """
	# 	CrfStemmed_updatedTime = orm.CrfStemmed.fetch_latest_updated_time()
	# 	if CrfStemmed_updatedTime != self.stemmed_updatedTime:
	# 		self.__load_crf_stemmed()
	# 		self.stemmed_updatedTime = CrfStemmed_updatedTime

	# 	docs = [self.stemming(docs[i]) for i in xrange(len(docs))]
	# 	return docs


def main():
	t0 = time()
	stem = Stemmed()
	print("Stemmed Instantiated done in %fs" % (time() - t0))

	doc = u'螺纹钢<ZJM>φ14mm</ZJM> <PH>HRB400</PH>' # 'utf-8'
	doc_res = stem.stemming(doc)# "螺纹钢Φ12mm"
	print doc_res

	doc = u'3×120+1' # 'utf-8'
	doc_res = stem.stemming(doc)# "螺纹钢Φ12mm"
	print doc_res
	


if __name__ == "__main__":
	main()