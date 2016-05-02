#!/usr/bin/python
# -*- coding: utf-8 -*-
# 模拟crf_handler的执行环境

import os, sys
sys.path.append( os.path.join( os.path.abspath(os.path.dirname(__file__)) , '..'))

import jieba.posseg as pseg
# tornado_glearn/dependence目录下的Uniformizer
from uniform import Uniformizer

from glearn.crf.crfpp import crf
from glearn.crf.datasets import datasets,train_dataset,test_dataset,validate_dataset,testUnit
from glearn.crf.model import crf_model
from glearn.crf.crfpputil import EncodeUtil,DecodeUtil

def main():
	reload(sys)                         #  
	sys.setdefaultencoding('utf-8')     # 

	successful_training_crfModelId_list = list()
	failure_training_crfModelId_list = list()
	crfModelId_list = datasets.get_crfModelId_list() 
	
	for crf_model_id in crfModelId_list:
		crf_labeled_samples = datasets.load_labeld_samples(crf_model_id)
		(crf_labeled_samples_unqualified, crf_tokenized_samples) = datasets.uniformize_and_tokenize( \
				Uniformizer, crf_labeled_samples)
		
		#if len(crf_labeled_samples_unqualified) == 0:
		print '>>> crf_encoding %s ...:'%(crf_model_id),
			
		crf_model = crf.encode(train_dataset(crf_model_id, crf_tokenized_samples))
		if crf_model:
			print "Successful training"
			successful_training_crfModelId_list.append(crf_model_id)
		else:
			print "Failure training"
			failure_training_crfModelId_list.append(crf_model_id)
		#else:
		#	print "%s has unqualified datas"%(crf_model_id)
		#	print '\n'.join(crf_labeled_samples_unqualified)
		#	failure_training_crfModelId_list.append(crf_model_id)
		#	continue
	print "successful_training_crfModelId_list:",successful_training_crfModelId_list
	print "failure_training_crfModelId_list:",failure_training_crfModelId_list
if __name__ == "__main__":
	main()
