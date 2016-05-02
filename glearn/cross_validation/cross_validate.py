#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, sys
sys.path.append( os.path.join( os.path.abspath(os.path.dirname(__file__)) , '../..'))
from lib.log_util import create_log
from glearn.crf.crfpp import crf
from glearn.crf.datasets import datasets,train_dataset,test_dataset,validate_dataset,testUnit
from glearn.crf.model import crf_model
from glearn.crf.crfpputil import EncodeUtil,DecodeUtil

sys.path.append( os.path.join( os.path.abspath(os.path.dirname(__file__)) , '../../dependence'))
from uniform import Uniformizer

reload(sys)                         #  
sys.setdefaultencoding('utf-8')     # 

infile = open('./cross_validate.txt','w')

def cross_validate(first_type_code, second_type_code, kfold=5):
	crf_model_id = datasets.get_crfModelId(first_type_code, second_type_code)

	(status,output)=('','')
	if crf_model_id:
	    cross_validate_samples = datasets.load_validate_samples(crf_model_id)
	    # if len(cross_validate_samples) == 0:
	    if not cross_validate_samples:
	        # logger.error("(first_type_code=%s,second_type_code=%s) hava no data!"%(first_type_code,second_type_code))
	        infile.write("(first_type_code=%s,second_type_code=%s) hava no data!"%(first_type_code,second_type_code))
	        (status,output) = ('-1','NO_DATA_ERROR')
	    else:
	        crf_tokenized_samples = list()
	        for i in range(len(cross_validate_samples)):
	            content_uniformized = Uniformizer.uniformize(cross_validate_samples[i])
	            try:
	                content_tokenized = EncodeUtil.tokenize(content_uniformized)
	            except Exception, e:
	                continue
	            crf_tokenized_samples.append(content_tokenized)

	        try:
	        	(status,output) = crf.cross_validate( kfold, validate_dataset(crf_model_id, crf_tokenized_samples) )
	        except Exception, e:
	        	infile.write("cross_validate failed!")
	        
	else:
		infile.write("(first_type_code=%s,second_type_code=%s) not exsit!"%(first_type_code,second_type_code))
		# logger.error("(first_type_code=%s,second_type_code=%s) not exsit!"%(first_type_code,second_type_code))
		(status,output) = ('-1','NO_CODE_ERROR')

	infile.write(first_type_code+second_type_code+'\n')
	infile.write(output+'\n')
	infile.write("="*80+'\n')


if __name__ == "__main__":

	# cross_validate('56','01')
	code_tuple_list = datasets.fetch_all_code()
	for code_tuple in code_tuple_list:
		print code_tuple
		cross_validate(code_tuple[0],code_tuple[1])
	print code_tuple_list