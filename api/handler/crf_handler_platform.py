#!/usr/bin/python
# -*- coding: utf-8 -*-
import traceback
from api.handler.base_handler import BaseHandler
import ujson
import collections

import os,sys
from os import environ
from os.path import dirname
from os.path import join
from os.path import exists
from os.path import expanduser
from os.path import isdir
from os import listdir
from os import makedirs

import datetime

import pickle
import shutil
import re
import codecs
import tarfile
import zipfile
import shutil
import glob

from glearn.crf.crfpp_platform import CRF
from glearn.crf.crfpputil import DecodeUtil,CrfppUtil
from glearn.datasets.base import load_files
import glearn.crf.global_variables as gv


class CrfPredictHandler(BaseHandler):
    """docstring for CrfPredictHandler"""

    def post(self):
        try:
            identity = self.get_argument('identity', default='')
            docs = ujson.loads(self.get_argument('docs', default=''))
            
            category_list = list()
            doc_list = list()
            for doc in docs:
                category_list.append(doc["category"])
                doc_list.append(doc["doc"])

            tokenizedDoc_list = DecodeUtil.tokenize_docs(doc_list)
            if identity==gv.GLDJC_IDENTITY:
                output_list,attr_value_dict_list = self.application.crf.crf_decode(gv.GLDJC_IDENTITY, category_list, tokenizedDoc_list, gldjc_bool=True, initialDoc_list=doc_list)
            else:
                output_list,attr_value_dict_list = self.application.crf.crf_decode(identity, category_list, tokenizedDoc_list)

            json_result = list()
            for i in xrange(len(output_list)):
                res_dict = {
                            "category":category_list[i],
                            "output":output_list[i],
                            "attr_value_dict":attr_value_dict_list[i]
                }
                json_result.append(res_dict)
            self._json_response(json_result)
        except:
            self.send_error()
            self._app_logger.error(traceback.format_exc())  

class CrfPredictExtendedHandler(BaseHandler):
    """docstring for CrfPredictExtendedHandler"""

    def post(self):
        try:
            # idx = self.get_argument('id', default='')
            identity = self.get_argument('identity', default='')
            docs = ujson.loads(self.get_argument('docs', default=''))
            
            idxs = list()
            category_list = list()
            doc_list = list()
            for doc in docs:
                idxs.append(doc["id"])
                category_list.append(doc["category"])
                doc_content_sectioned = CrfppUtil.section( doc["doc"] ) ###
                doc_list.append( doc_content_sectioned )


            tokenizedDoc_list = DecodeUtil.tokenize_docs(doc_list)
            if identity==gv.GLDJC_IDENTITY:
                output_list,attr_value_dict_list = self.application.crf.crf_decode_extended(gv.GLDJC_IDENTITY, category_list, tokenizedDoc_list, gldjc_bool=True, initialDoc_list=doc_list)
            else:
                output_list,attr_value_dict_list = self.application.crf.crf_decode_extended(identity, category_list, tokenizedDoc_list)

            json_result = list()
            for i in xrange(len(output_list)):
                res_dict = {
                            "id":idxs[i],
                            "category":category_list[i],
                            "output":output_list[i],
                            "attr_value_dict":attr_value_dict_list[i]
                }
                json_result.append(res_dict)
            self._json_response(json_result)
        except:
            self.send_error()
            self._app_logger.error(traceback.format_exc())  


class UploadFileHandler(BaseHandler):
    _label = "UploadFileHandler"

    @classmethod
    def __rmtree_common(self, identity):
        target_dir = os.path.join( gv.get_model_home(), identity)
        if os.path.exists( target_dir ):
            shutil.rmtree( target_dir )

    @classmethod
    def __uncompress_common(self, identity, archive_file_name):
        """ __uncompress_common """
        data_home = os.path.join( gv.get_data_home(), identity)
        archive_path=os.path.join(data_home, archive_file_name)
        try:
            if archive_file_name.endswith('.zip'):
                archive_name = archive_file_name.rstrip('.zip') 
                target_dir = os.path.join( data_home, archive_name)
                zipfile.ZipFile(archive_path).extractall(path=target_dir)
            elif archive_file_name.endswith('.tar.gz'):
                archive_name = archive_file_name.rstrip('.tar.gz') 
                target_dir = os.path.join(data_home, archive_name)
                tarfile.open(archive_path, "r:gz").extractall(path=target_dir)
            elif os.path.isdir( archive_path ): # for gldjc
                target_dir = archive_path
            else:
                print 'archive_file_name is not .zip & .tar.gz & directory'
                return None,None

            train_folder = glob.glob( os.path.join(target_dir,'*train'))[0]
            #\ test_folder = glob.glob( os.path.join(target_dir,'*test'))[0]
        except Exception, e:
            raise e
        return target_dir,train_folder
    
    def get(self):
        self.render('index.html')
 
    def post(self):
        try: 
            data_home = gv.get_data_home()#文件的暂存路径
            identity = self.get_argument('identity', default='')
            
            if identity not in gv.AUTHENTICATED_IDENTITIS:
                self.write('Authentication failed!')
                self.finish() 
                return 

            file_metas=self.request.files['file']    #提取表单中‘name’为‘file’的文件元数据
            for meta in file_metas:
                archive_file_name=meta['filename'] # meta <= <class 'tornado.httputil.HTTPFile'>
                
                identity_home = os.path.join( data_home, identity )
                if os.path.exists( identity_home ):
                    shutil.rmtree( identity_home )
                os.makedirs( identity_home )

                archive_path=os.path.join(identity_home, archive_file_name)
                with open(archive_path,'wb') as up:   # 有些文件需要已二进制的形式存储，实际中可以更改
                    up.write(meta['body'])
                
                # 解压缩
                target_dir, train_folder = UploadFileHandler.__uncompress_common(identity, archive_file_name)
                UploadFileHandler.__rmtree_common( identity )
                cache = load_files(train_folder, encoding='utf-8')                
                
                # 重新组织训练数据，方便于训练
                categoryName_docs_dict = collections.defaultdict(list)
                data = cache.data
                target = cache.target
                target_names = cache.target_names
                for i in xrange(len(target)):
                    category_name = target_names[ target[i] ]
                    docs = data[i].split('\n')
                    categoryName_docs_dict[category_name].extend(docs)
                print "categoryName_docs_dict.keys():",categoryName_docs_dict.keys()
                
                # 训练所有类别的crf模型
                taggers = self.application.crf.crf_encode(identity,categoryName_docs_dict)

                self.write('finished!') 
                self._json_response(taggers)                
        except:
            self.send_error()
            self._app_logger.error(traceback.format_exc())  