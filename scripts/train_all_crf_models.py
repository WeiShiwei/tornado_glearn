#!/usr/bin/python
# -*- coding: utf-8 -*-
# 因为ansj_seg加载字典的原因,需要在tornado_glearn/为当前目录下，执行python scripts/train_all_crf_modles.py

import os
import sys

sys.path.append( os.path.join( os.path.abspath(os.path.dirname(__file__)) , '..'))
from glearn.crf.datasets import datasets
from glearn.crf import orm
import glearn.crf.global_variables as gv
from glearn.crf.crfpp_platform import CRF

crf = CRF()

def main():
	all_model_ids = orm.CrfModel.fetch_all_model_ids()	

	for crf_model_id in all_model_ids:
		try:
			crf_labeled_samples = datasets.load_labeld_samples(crf_model_id)

			identity = gv.GLDJC_IDENTITY
			category = datasets.fetch_category( crf_model_id )
			categoryName_docs_dict = {
			                        category:crf_labeled_samples
			}

			json_result = {
			    "status":'',
			    "taggers":None
			}

			# 训练模型
			taggers = crf.crf_encode(identity, categoryName_docs_dict)
			if taggers:
			    json_result["status"] = 'Successful training'
			    json_result["taggers"] = taggers
			    self._json_response(json_result)
			else:
			    json_result["status"] = 'Failure training'
			    self._json_response(json_result)

			print json_result
		except Exception, e:
			continue 

if __name__ == '__main__':
	main()