# coding:utf-8
import os
import sys
from time import time
import collections

import ujson
import redis
sys.path.append( os.path.join( os.path.abspath(os.path.dirname(__file__)), '../..') )
from glearn.specification.config import config

from glearn.crf.ixx_glodon.template.assembly_template import AssemblyTemplate
from glearn.crf.ixx_glodon.model.session import get_session

##
#Description: product template will be store in redis.
#             If the template can not be found in redis, function will
#             search template in database and store in redis.

# template_redis.get(name)
# template_redis.set(name, value)
template_redis = redis.StrictRedis(
    host=config.REDIS_HOST,
    port=config.REDIS_PORT,
    db=config.REDIS_DB
)
if template_redis.flushdb(): #删除当前数据库的所有数据
	print "template redis flushdb"

class specificationTemplate(object):
	"""docstring for specificationTemplate"""
	template_dic_pool = collections.defaultdict(dict)
	template_list_pool = collections.defaultdict(list)
	
	def __init__(self, arg):
		super(specificationTemplate, self).__init__()
		self.arg = arg

	@classmethod
	def retrieve_templates(self, category):
		""" template_list_pool['25.11'] = [ 'AGR', 'AVVR', 'BLV', 'BLVV', 'BLVVB', 'BLX', 'BLXF',...] """
		template_list_pool = self.template_list_pool
		from_redis = False
		class_id = category + '#*'
		first_type_code,second_type_code = category.split('.')

		# if class_id not in template_dic_pool.keys():
		# Get template from redis at first.
		if template_redis.get(class_id) is not None:
			template_list_pool[class_id] = ujson.loads(template_redis.get(class_id))
			from_redis = True
		else:
			template_list_pool[class_id] = None

		# Search template from database when template is not in redis.
		if template_list_pool[class_id] is None:
			templates = AssemblyTemplate.retrieve_lv2assembly_template_list( category )
			template_list_pool[class_id] = templates

			# Store template in redis.
			template_redis.delete(class_id)
			template_redis.set(class_id, ujson.dumps(template_list_pool[class_id]))

		return template_list_pool[class_id],from_redis

	@classmethod
	def retrieve_template_dict(self, category, spec):
		""" template_dic_pool['25.11'] = {'工作类型':'ZC(阻燃C级)', '护套材料':'Y聚乙烯护套',...} """
		template_dic_pool = self.template_dic_pool

		first_type_code,second_type_code = category.split('.')
		class_id = '#'.join( [category, spec] )
		
		# if class_id not in template_dic_pool.keys():
		# Get template from redis at first.
		if template_redis.get(class_id) is not None: ### template_redis
			template_dic_pool[class_id] = ujson.loads(template_redis.get(class_id))
		else:
			template_dic_pool[class_id] = None

		# Search template from database when template is not in redis.
		if template_dic_pool[class_id] is None:
			with get_session() as session:
				attrName_value_dict = AssemblyTemplate.retrieve_attrName_value_dict(
									session, first_type_code, second_type_code, spec)
				template_dic_pool[class_id] = attrName_value_dict

			# Store template in redis.
			template_redis.delete(class_id)
			template_redis.set(class_id, ujson.dumps(template_dic_pool[class_id]))

		return template_dic_pool[class_id]


def main():
	t0 = time()
	st = specificationTemplate.retrieve_template_dict('25.11','BLV')
	print("done in %fs" % (time() - t0))
	print st

	t0 = time()
	templates = specificationTemplate.retrieve_templates('25.11')
	print("done in %fs" % (time() - t0))
	
	print templates

if __name__ == '__main__':
	main()