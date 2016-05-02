#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
The :mod:`sklearn.crf.crfpp` module implements Conditional Random Field algorithms. These
are supervised learning methods .
"""

import os
import sys
import commands
import tempfile 
import datetime
import fnmatch
import random

from logutil import logger

import crfpp_options
import conlleval
import global_variables as gv

sys.path.append( os.path.join( os.path.abspath(os.path.dirname(__file__)) , '../..'))
from glearn.crf.CRFPP_wrap import CRFPP
from glearn.crf.decode_platform import Decode
from glearn.crf.pattern import PatternMatchEngine
from glearn.crf.crfpputil import EncodeUtil,DecodeUtil


class CRF(object):
	""" docstring for crf """

	def __init__(self):
		self.tagger_pool = self.__load_model_files()

	def __load_model_files(self):
		tagger_pool = self.__traverse_directory_tree(gv.get_model_home())
		return tagger_pool

	def __traverse_directory_tree(self, root, patterns='*.train;*.model', single_level=False, yield_folders=False):
		locate_tagger_dict = dict()

		patterns = patterns.split(';')
		for path, subdirs, files in os.walk(root):
			if yield_folders:
			    files.extend(subdirs)
			files.sort()
			for name in files:
				for pattern in patterns:
					if fnmatch.fnmatch(name,pattern):
						model_file = os.path.join(path, name)
						# print model_file
						tagger = CRFPP.Tagger("-m "+model_file+"  -n2")
						locate_tagger_dict[name[0:(name.rindex('.'))]] = tagger
						break
			if single_level:
				break
		return locate_tagger_dict

	def __crfpp_learn(self,template_file,train_file,model_file):
		"""CRF training

		example:
		    crf_learn -c 4.0 template train.data model
		    (3 path):template_file train_file model_file 
		""" 
		# commandLine = gv.crfpp_path + '/' + 'crf_learn'
		commandLine = 'crf_learn'
		commandLine += ' -a '+ crfpp_options.ALGORITHM
		commandLine += ' -p '+ str(crfpp_options.THREAD_NUM)
		commandLine += ' -c '+ str(crfpp_options.HYPER_PARAMETER)
		commandLine += ' -f '+ str(crfpp_options.CUTOFF_HRESHOLD)
		commandLine += ' ' + template_file + " " + train_file + " " + model_file
		print commandLine
		(status, output)=commands.getstatusoutput(commandLine)
		print "status = %s"%status
		print output

		if status == 0:
			tagger = CRFPP.Tagger("-m "+model_file.encode("ascii")+"  -n2")
		else:
			tagger = None
		return (status, output, tagger)

	def crf_learn(self, identity, category_name, crf_tokenized_samples):
		""""""
		crf_conll_samples = crf_tokenized_samples
		if not crf_conll_samples:
			print '%s have no train_data',category_name
			return None,None,None

		train_file_tempfile = tempfile.NamedTemporaryFile()
		train_file_tempfile.write('\n'.join(crf_conll_samples))
		train_file_tempfile.flush() #将缓冲区中的数据立刻写入文件

		template_file = os.path.join( gv.templates_path , 'template' )
		train_file = train_file_tempfile.name
		
		model_file_target_dir = os.path.join(gv.get_model_home(),identity) 
		if not os.path.exists(model_file_target_dir):
			os.mkdir(model_file_target_dir)
		model_file = os.path.join( os.path.join(gv.get_model_home(),identity) , identity+ '@' + category_name + '.model' )

		try:
			starttime = datetime.datetime.now()
			status, output, tagger = self.__crfpp_learn(template_file,train_file,model_file)
			endtime = datetime.datetime.now()
			print 'crf_encoding cost %s seconds'%(endtime - starttime)
			
			if status != 0:
				logger.error("crf_encoding(%s) encountered an error"%crf_model_id)
				return None,None,None
			return status, output, tagger
		except Exception, e:
			return None,None,None
		finally:
			train_file_tempfile.close() # annotate for debug
		
	def crf_encode(self, identity, categoryName_docs_dict):
		categoryName_crfppModel_dict = dict()
		taggers_info = list()
		
		for (category_name, docs) in categoryName_docs_dict.items():
			crf_labeled_samples = docs
			(crf_labeled_samples_unqualified, crf_tokenized_samples) = EncodeUtil.tokenize_samples( crf_labeled_samples)
			print '\n'.join( crf_labeled_samples_unqualified )
			
			# 把从数据库中得到的训练数据保存到主目录的crf_learn_data目录下
			target_dir = os.path.join( gv.get_data_home(), identity)
			if not os.path.exists( target_dir ):
				os.mkdir( target_dir ) 
			train_corpus_file = os.path.join( target_dir, category_name+'.train')
			with open(train_corpus_file,'w') as outfile:
				outfile.write('\n'.join(crf_tokenized_samples))
			
			status, output, tagger = self.crf_learn(identity, category_name, crf_tokenized_samples)
			# -------------------------------------
			category = identity+ '@' + category_name
			categoryName_crfppModel_dict[ category ] = tagger
			# -------------------------------------
			taggers_info.append(
				{
					"status":status,
					"output":output,
					"tagger":str(tagger),
					"category":category
				}
			)
		
		self.tagger_pool.update(categoryName_crfppModel_dict)
		return taggers_info

	def crf_decode(self, identity, category_list, tokenizedDoc_list, gldjc_bool=False, initialDoc_list=None):
		locate_list = list()
		for category in category_list:
			locate_list.append( identity+ '@' +category )
		# assert len(locate_list)==len(tokenizedDoc_list)
		print "locate_list:",locate_list

		output_list = list()
		attr_value_dict_list = list()
		for i in xrange(len(locate_list)):
			loc = locate_list[i]
			doc = tokenizedDoc_list[i]

			try:
				tagger = self.tagger_pool[loc]
				output = Decode.decode(tagger, doc) 
				print "locate:",loc; print output

				if gldjc_bool:
					attr_value_dict = PatternMatchEngine.pattern_matching(output, category_list[i], initialDoc_list[i])
				else:
					attr_value_dict = PatternMatchEngine.structuring( output )
			except KeyError, e:
				print "the model:",loc,"not found"
				print "="*40
				output = '' 
				attr_value_dict={}
			except Exception, e:
				#raise error, "unmatched group"
				print 'raise error:',e
				print "="*40
				output = '' 
				attr_value_dict={}

			output_list.append(output)
			attr_value_dict_list.append(attr_value_dict)

		return output_list,attr_value_dict_list

	def crf_decode_extended(self, identity, category_list, tokenizedDoc_list, gldjc_bool=False, initialDoc_list=None):
		locate_list = list()
		for category in category_list:
			locate_list.append( identity+ '@' +category )
		print "locate_list:",locate_list

		output_list = list()
		attr_value_dict_list = list()
		for i in xrange(len(locate_list)):
			loc = locate_list[i]
			doc = tokenizedDoc_list[i]

			try:
				tagger = self.tagger_pool[loc]
				output = Decode.decode(tagger, doc) 
				print "locate:",loc; print output
				if gldjc_bool:
					attr_value_dict = PatternMatchEngine.pattern_matching(output, category_list[i], initialDoc_list[i])
				else:
					attr_value_dict = PatternMatchEngine.structuring( output )
			except KeyError, e:
				print "the model:",loc,"not found"
				print "="*40
				output = '' 
				attr_value_dict={}
			except Exception, e:
				#raise error, "unmatched group"
				print 'raise error:',e
				print "="*40
				output = '' 
				attr_value_dict={}

			output_list.append(output)
			attr_value_dict_list.append(attr_value_dict)

		return output_list,attr_value_dict_list


	def cross_validate(self, kfold, validate_dataset):
		""" kfold交叉验证 """
		category = validate_dataset['category']
		cross_validate_samples = validate_dataset['cross_validate_samples']

		proportion = 1.0/float(kfold)
		max_num = len(cross_validate_samples)
		output_file_list = list()
		for i in range(int(kfold)):
			random.shuffle(cross_validate_samples)
			train_validate_samples = cross_validate_samples[0:int(max_num*(1-proportion))]
			test_validate_samples = cross_validate_samples[int(max_num*(1-proportion)):]
			# 对训练验证样本处理，训练模型
			validate_model_file = self.__cross_validate_encode(category,train_validate_samples)		
			# 对测试验证样本decode处理，获得输出文件
			output_file_list.append( self.__cross_validate_decode(validate_model_file,test_validate_samples) )
			# import pdb;pdb.set_trace() ###
		
		output_file_tempfile = tempfile.NamedTemporaryFile(mode='a')
		for output_file in output_file_list:
			output_file_tempfile.write(output_file.read()+'\n\n')
			output_file_tempfile.flush() #将缓冲区中的数据立刻写入文件
			output_file.close()
		# perl脚本对测试结果文件进行评价
		(status,output) = conlleval.conlleval(output_file_tempfile.name)

		output_file_tempfile.close()
		return (status,output)
	
	def __cross_validate_encode(self,category,train_validate_samples):
		""""""
		train_file_tempfile = tempfile.NamedTemporaryFile()
		train_file_tempfile.write('\n'.join(train_validate_samples))
		train_file_tempfile.flush() #将缓冲区中的数据立刻写入文件

		template_file = os.path.join( gv.templates_path , 'template' )
		train_file = train_file_tempfile.name
		model_file = os.path.join( gv.validate_models_path , category + '.model' )

		try:
			starttime = datetime.datetime.now()
			# --------------------------------------------------------------------------
			status, output, _ = self.__crfpp_learn(template_file,train_file,model_file)
			# --------------------------------------------------------------------------
			endtime = datetime.datetime.now()
			print 'crf_learning cost %s seconds'%(endtime - starttime)

			if status != 0:
				raise Exception("crf_learn error:\n",output)
			return model_file
		except Exception, e:
			print e
			return None
		finally:
			train_file_tempfile.close()

	def __cross_validate_decode(self,validate_model_file,test_validate_samples):
		""""""
		test_file_tempfile = tempfile.NamedTemporaryFile()
		test_file_tempfile.write('\n'.join(test_validate_samples))
		test_file_tempfile.flush() #将缓冲区中的数据立刻写入文件

		output_file_tempfile = tempfile.NamedTemporaryFile()
		try:
			commandLine = 'crf_test'
			# commandLine += ' -v ' + str(crfpp_options.VERBOSE)
			# commandLine += ' -n ' + str(crfpp_options.NBEST)
			commandLine += ' -m ' + validate_model_file+" "+test_file_tempfile.name+" > "+output_file_tempfile.name
			print commandLine
			(status, output)=commands.getstatusoutput(commandLine)
			if status != 0:
				raise Exception("crf_test error:\n",output)
			return output_file_tempfile
		except Exception, e:
			print e
			return None
		finally:
			test_file_tempfile.close()
