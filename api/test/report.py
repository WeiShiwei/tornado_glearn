#!/usr/bin/python
# -*- coding: utf-8 -*-
import os, sys
sys.path.append( os.path.join( os.path.abspath(os.path.dirname(__file__)) , '../..'))

import requests
import ujson
import unittest
import datetime
import csv
import glob

reload(sys)                         #  
sys.setdefaultencoding('utf-8')     # 
# -------------------------------------------------------
from glearn.crf.crfpp_platform import CRF
from glearn.crf.crfpputil import DecodeUtil,CrfppUtil
from glearn.datasets.base import load_files
import glearn.crf.global_variables as gv
# ----------------------------------------------------
from glearn.crf.crfpp_platform import CRF
crf = CRF()


def predict(identity, docs):
	# identity = self.get_argument('identity', default='')
	# docs = ujson.loads(self.get_argument('docs', default=''))

	category_list = list()
	doc_list = list()
	for doc in docs:
	    category_list.append(doc["category"])
	    doc_list.append(doc["doc"])

	tokenizedDoc_list = DecodeUtil.tokenize_docs(doc_list)
	if identity==gv.GLDJC_IDENTITY:
	    output_list,attr_value_dict_list = crf.crf_decode(gv.GLDJC_IDENTITY, category_list, tokenizedDoc_list, gldjc_bool=True, initialDoc_list=doc_list)
	else:
	    output_list,attr_value_dict_list = crf.crf_decode(identity, category_list, tokenizedDoc_list)

	json_result = list()
	for i in xrange(len(output_list)):
	    res_dict = {
	                "category":category_list[i],
	                "output":output_list[i],
	                "attr_value_dict":attr_value_dict_list[i]
	    }
	    json_result.append(res_dict)
	return json_result


# crf_files = glob.glob( os.path.join( os.path.abspath(os.path.dirname(__file__)) , 'fengwan','*.txt'))
# for crf_file in crf_files:
crf_file = sys.argv[1]
doc_list = list()
with open( crf_file , 'rb') as infile:
    lines = infile.readlines()
    for line in lines:
        line = line.strip()
        doc_list.append({"category":'25.11','doc':line})

# data = {
#     "identity":"gldjc",
#     'docs':ujson.dumps(doc_list[0:10])
# }
results = predict("gldjc", doc_list[0:10])
# json_result = requests.post('http://127.0.0.1:9700/crf/predict', params=data)
# results = ujson.loads(json_result.content)

csv_file = os.path.join(os.path.abspath(os.path.dirname(__file__)) , 'fengwan',os.path.basename(crf_file)+'.csv')
writer = csv.writer(file(csv_file, 'wb'), quoting=csv.QUOTE_ALL)
# writer.writerow(['doc','attr_value','output'])
attr_names = ['工作类型','芯数×标称截面','芯数','电线特征','护套材料','工作温度',
	'标称截面(mm²)','额定电压（KV）','内护层材料','绝缘材料','线芯材质','品种','标称直径(mm)']
header = ['doc']+attr_names
writer.writerow( header )
# 1. (GZLX) 工作类型
# 2. (XSBCJM) 芯数×标称截面
# 3. (XS) 芯数
# 4. (DXTZ) 电线特征
# 5. (HTCL) 护套材料
# 6. (GZWD) 工作温度
# 7. (BCJMM) 标称截面(mm²)
# 8. (EDDYK) 额定电压（KV）
# 9. (NHCCL) 内护层材料
# 0. (JYCL) 绝缘材料
# Q. (XXCZ) 线芯材质
# W. (PZ) 品种
# E. (BCZJM) 标称直径(mm)


# for i,res in enumerate(results):
#     doc = doc_list[i]['doc']
#     output = res['output']            
#     attr_value_dict = res['attr_value_dict']
#     attr_value_list = list()
#     for key,value in attr_value_dict.items():
#         attr_value_list.append( key+':'+value )
#     attr_value_res = '\n'.join(sorted(attr_value_list))
#     print doc, output, attr_value_res
    
#     writer.writerow([doc,attr_value_res, output])

for i,res in enumerate(results):
    doc = doc_list[i]['doc']
    output = res['output']            
    attr_value_dict = res['attr_value_dict']
    attr_values = [attr_value_dict[attr_name] for attr_name in attr_names]
    attr_values = list()
    for attr_name in attr_names:
    	try:
    		attr_value = attr_value_dict[attr_name]
    		attr_values.append(attr_value)
    	except Exception, e:
    		attr_values.append('')
    writer.writerow( [doc]+attr_values )
