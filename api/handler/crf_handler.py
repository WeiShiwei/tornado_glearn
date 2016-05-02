#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import ujson

from glearn.crf.datasets import datasets
from glearn.crf.model import crf_model
from glearn.crf.crfpputil import EncodeUtil,DecodeUtil
import glearn.crf.global_variables as gv

import traceback
from api.handler.base_handler import BaseHandler

class TrainCrfModelHandler(BaseHandler):
    _label = "TrainCrfModelHandler"
    
    def post(self):
        try:
            crf_model_id = ujson.loads(self.get_argument('crf_model_id', default='')) 
            crf_labeled_samples = datasets.load_labeld_samples(crf_model_id)

            identity = gv.GLDJC_IDENTITY
            category = datasets.fetch_category( crf_model_id )
            categoryName_docs_dict = { category:crf_labeled_samples }
            
            json_result = {
                "status":'',
                "taggers":None
            }

            # 训练模型
            taggers = self.application.crf.crf_encode(identity, categoryName_docs_dict)
            if taggers:
                json_result["status"] = 'Successful training'
                json_result["taggers"] = taggers
                self._json_response(json_result)
            else:
                json_result["status"] = 'Failure training'
                self._json_response(json_result)
        except Exception, e:
            self.send_error()
            self._app_logger.error(traceback.format_exc())

class DecodeHandler(BaseHandler):
    _label = "DecodeHandler"
    
    def post(self):
        try:            
            decode_datas = self.get_argument('decode_datas',default='')

            id_list = list()
            crf_model_id_list = list()
            category_list = list()
            doc_list = list()    
            
            for line in decode_datas.split('\n'):
                line = line.strip()
                if line == '':
                    continue
                try:
                    pos1 = line.index(' ')
                    id = line[0:pos1]
                    pos2 = line.index(' ',pos1+1)
                    crf_model_id = line[pos1+1:pos2] 
                    
                    int(crf_model_id) # ValueError: invalid literal for int() with base 10: '0521a'               
                    
                    content = line[pos2+1:].strip("'")
                except Exception, e:
                    print "'%s' does not meet the requirements"%(line)
                    continue
                
                id_list.append(id)
                crf_model_id_list.append(crf_model_id)
                # 当crf_model_id非法时，赋给category为0000,这里认为0000为非法的类别
                category_list.append( datasets.crfModelId_category_dict.get(crf_model_id, '0000') )
                doc_list.append( content )

            tokenizedDoc_list = DecodeUtil.tokenize_docs(doc_list)
            output_list,attr_value_dict_list = self.application.crf.crf_decode(gv.GLDJC_IDENTITY, category_list, tokenizedDoc_list, gldjc_bool=True, initialDoc_list=doc_list)

            json_result = list()
            for i in xrange(len(output_list)):
                res_dict = {
                        "id":id_list[i],
                        "crf_model_id":crf_model_id_list[i],
                        "output_str":output_list[i],
                        "attr_value_dict":attr_value_dict_list[i]
                }
                json_result.append(res_dict)
            self._json_response(json_result)
        except:
            self.send_error()
            self._app_logger.error(traceback.format_exc())   

class CrossValidateHandler(BaseHandler):
    _label = "CrossValidateHandler"
    def get(self):
        reload(sys)                         #  
        sys.setdefaultencoding('utf-8')     # 

        try:
            first_type_code = self.get_argument('first_type_code',default='')
            second_type_code = self.get_argument('second_type_code',default='')
            kfold = self.get_argument('kfold',default='')

            (status,output)=('','')

            crf_model_id = datasets.get_crfModelId(first_type_code, second_type_code)
            if crf_model_id:
                cross_validate_samples = datasets.load_validate_samples(crf_model_id)
                if len(cross_validate_samples) == 0:
                    logger.error("(first_type_code=%s,second_type_code=%s) hava no data!"%(first_type_code,second_type_code))
                    (status,output) = ('-1','NO_DATA_ERROR')
                else:
                    
                    crf_labeled_samples_unqualified, crf_tokenized_samples = EncodeUtil.tokenize_samples(cross_validate_samples)
                    validate_dataset = {
                        "category":'.'.join([first_type_code,second_type_code]),
                        "cross_validate_samples":crf_tokenized_samples
                    }
                    (status,output) = self.application.crf.cross_validate(kfold,validate_dataset)
            else:
                logger.error("(first_type_code=%s,second_type_code=%s) not exsit!"%(first_type_code,second_type_code))
                (status,output) = ('-1','NO_CODE_ERROR')

            print status 
            print output
            json_result = {
                "status":status,
                "output":output
            }

            self._json_response(json_result)
        except:
            self.send_error()
            self._app_logger.error(traceback.format_exc())
