# -*- coding: utf-8 -*-
import orm
import collections

from crfpputil import EncodeUtil,DecodeUtil


class datasets(object):
	"""docstring for datasets"""
	def __init__(self, arg):
		super(datasets, self).__init__()
		self.arg = arg

	crfModelId_category_dict = orm.CrfModel.fetch_crfModelId_category_dict()

	@classmethod
	def load_labeld_samples(self, crf_model_id, db_source = 'ml_2013'):

		crf_labeled_samples = orm.CrfTrainSampleItem.contents_for_train( crf_model_id )
		if len(crf_labeled_samples) == 0:
			return None
		return crf_labeled_samples
	
	@classmethod
	def fetch_category(self, crf_model_id):
		first_type_code,second_type_code = orm.CrfModel.get_code_tuple( crf_model_id )
		category = first_type_code + '.' +second_type_code
		return category

	@classmethod
	def fetch_complete_info(self, category):
		first_type_code,second_type_code = category.split('.')
		crf_model_id = orm.CrfModel.get_crf_model_id(first_type_code,second_type_code[0:2])
		return crf_model_id,first_type_code,second_type_code

	# @classmethod
	# def uniformize_and_tokenize(self, Uniformizer, crf_labeled_samples):
	# 	crf_tokenized_samples = list()
	# 	crf_labeled_samples_unqualified = list()

	# 	if crf_labeled_samples is None:
	# 		return (list(),list())
		
	# 	for i in range(len(crf_labeled_samples)):
	# 		# content_uniformized = Uniformizer.uniformize(crf_labeled_samples[i])
	# 		content_uniformized = crf_labeled_samples[i]
	# 		try:
	# 			content_tokenized = EncodeUtil.tokenize(content_uniformized)
	# 		except Exception, e:
	# 			crf_labeled_samples_unqualified.append(crf_labeled_samples[i])
	# 			continue
	# 		crf_tokenized_samples.append(content_tokenized)							
	# 	return crf_labeled_samples_unqualified, crf_tokenized_samples
	# @classmethod
	# def tokenize(self, crf_labeled_samples):
	# 	crf_tokenized_samples = list()
	# 	crf_labeled_samples_unqualified = list()

	# 	if crf_labeled_samples is None:
	# 		return (list(),list())
		
	# 	for i in range(len(crf_labeled_samples)):
	# 		content_uniformized = crf_labeled_samples[i]
	# 		try:
	# 			content_tokenized = EncodeUtil.tokenize(content_uniformized)
	# 		except Exception, e:
	# 			crf_labeled_samples_unqualified.append(crf_labeled_samples[i])
	# 			continue
	# 		crf_tokenized_samples.append(content_tokenized)							
	# 	return crf_labeled_samples_unqualified, crf_tokenized_samples

	@classmethod
	def load_labeld_samples_form_txtFile(self, train_file_path):
		with open(train_file_path) as fin:
			crf_labeled_samples = fin.readlines()
			if len(crf_labeled_samples) == 0:
				return None
			return crf_labeled_samples

	# -*- Discarded -*- #
	# @classmethod
	# def load_train_dataset(self,crf_model_id):
	# 	""""""
	# 	crf_labeled_samples = orm.CrfTrainSampleItem.contents_for_train( crf_model_id )
	# 	if len(crf_labeled_samples) == 0:
	# 		return None
	# 	crf_tokenized_samples = EncodeUtil.tokenize_for_encode( crf_labeled_samples)
	# 	return train_dataset(crf_model_id,crf_tokenized_samples)

	@classmethod
	def get_crfModelId_list(self):
		crfModelId_list = list()
		models = orm.session.query(orm.CrfModel.id).order_by(orm.CrfModel.id).all()
		for model in models:
			crfModelId_list.append(model.id)
		return crfModelId_list
	
	# -*- Discarded -*- #
	# @classmethod
	# def load_train_dataset_fromFile(self,crf_model_id,train_file):
	# 	with open(train_file) as fin:
	# 		crf_labeled_samples = fin.readlines()
	# 		if len(crf_labeled_samples) == 0:
	# 			return None
	# 		crf_tokenized_samples = crfpputil.tokenize_for_encode( crf_labeled_samples)
	# 		return train_dataset(crf_model_id,crf_tokenized_samples)

	# -*- Discarded -*- #
	# def load_test_dataset(self,test_file):
	# 	"""test_file的格式一定要规范"""		
	# 	testUnit_list = list()

	# 	fin = open(test_file,'r')
	# 	line = fin.readline()
	# 	while line:
	# 		elemlist = line.strip().split() ###不一定是制表符，可能是多个空格
	# 		if elemlist:
	# 			print elemlist ###
				
	# 			id = elemlist[0]
	# 			crfModelId = elemlist[1]
	# 			content = ('\t'.join(elemlist[2:]) ).strip('"') ### attention

	# 			testUnit_list.append( testUnit(id,crfModelId,content) )
	# 		line = fin.readline()
	# 	fin.close()

	# 	crf_tokenized_dataset = DecodeUtil.tokenize_for_decode(testUnit_list)		
	# 	return test_dataset(crf_tokenized_dataset)

	@classmethod
	def tokenize_for_decode(self,testUnit_list):
		crf_testUnit_list = DecodeUtil.tokenize_for_decode(testUnit_list)
		return test_dataset(crf_testUnit_list)

	# ----------------------------------------------------------------------------------
	@classmethod
	def get_crfModelId(self,first_type_code,second_type_code):
		crf_model = orm.session.query(orm.CrfModel).filter(orm.CrfModel.first_type_code==first_type_code,\
			orm.CrfModel.second_type_code==second_type_code).first()
		
		if crf_model:
			return crf_model.id
		else:
			return None

	@classmethod
	def load_validate_samples(self, crf_model_id):
		cross_validate_samples = orm.CrfTrainSampleItem.contents_for_train( crf_model_id )
		if len(cross_validate_samples) == 0:
			return None
		return cross_validate_samples
	# ----------------------------------------------------------------------------------
	@classmethod
	def fetch_all_code(self):
		code_tuple_list = orm.CrfModel.fetch_all_code()
		return code_tuple_list
	# ----------------------------------------------------------------------------------



class train_dataset(object):
	"""train_dataset类必须带有crf_model_id，这是数据一种身份上的认同"""
	def __init__(self,crf_model_id,crf_conll_samples,db_source='ml_2013'):
		self.crf_model_id = crf_model_id
		self.crf_conll_samples = crf_conll_samples

class test_dataset(object):
	"""docstring for test_dataset

	crf_testUnit_list的数据格式:
	[testUnit(id,crf_model_id,unlabeledLine & labeledLine),...]
	"""
	def __init__(self,crf_testUnit_list):
		self.crf_testUnit_list = crf_testUnit_list

class output_dataset(test_dataset):
	"""docstring for output_dataset

	crf_testUnit_list的数据格式:
	[testUnit(id,crf_model_id,outputLine),...]
	outputLine的数据格式示例:
		不等边 B-PZ    0.976013985862
	    角钢  I-PZ    0.834136196282
	    Q365    B-PH    0.463382254021
	    ...
	"""
	def __init__(self,crf_testUnit_list):
		test_dataset.__init__(self,crf_testUnit_list)

class validate_dataset(object):
	"""docstring for validate_dataset"""
	def __init__(self,crf_model_id, cross_validate_samples):
		super(validate_dataset, self).__init__()
		self.crf_model_id = crf_model_id
		self.cross_validate_samples = cross_validate_samples

class testUnit(object):
	"""docstring for testUnit"""
	def __init__(self, id,crfModelId,content):
		super(testUnit, self).__init__()
		self.id = id
		self.crfModelId = crfModelId
		self.content = content

class testBucket(object):
	""" 类似testUnit,最终返回的 & 被规范的数据类型
		attr_value_dict是属性名和属性值对的字典
	"""
	def __init__(self, id, crf_model_id, output_str, attr_value_dict):
		self.id = id
		self.crf_model_id = crf_model_id
		self.output_str = output_str
		self.attr_value_dict = attr_value_dict