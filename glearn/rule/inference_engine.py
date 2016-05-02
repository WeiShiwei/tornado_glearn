# -*- coding:utf-8 -*-
import ujson
from production_memory import Rules
from working_memory import Facts

class PatternMatcher(object):
	"""docstring for PatternMatcher"""

	@classmethod
	def match(self, category, doc):
		""" 正则匹配和精确匹配的接口 """
		# rules = Rules.fetch_rules_set( category )
		# conflicts = list()
		# for rule in rules: #遍历规则集
		# 	prog = rule.prog
		# 	substitute = rule.substitute

		# 	match = prog.search( doc )
		# 	if match:
		# 		print match.group(),substitute,rule.regrex
		# 		prog_dict = ujson.loads( prog.subn( substitute, match.group())[0] )
		# 		print prog_dict
		# 		conflicts.append( {'rule':rule, 'result':prog_dict, 'doc':doc} )
		# 		# return prog_dict
		# if len(conflicts) == 0:
		# 	return dict()
		# if len(conflicts) == 1:
		# 	return conflicts[0]['result']

		# regex_match_dict = Agenda.conflict_resolution( conflicts )

		regex_match_dict = Rules.regex_matcher.matching(category, doc)
		exact_match_dict = Rules.exact_matcher.matching(category, doc) #精确匹配
		match_dict = dict()
		match_dict.update(regex_match_dict)
		match_dict.update(exact_match_dict)
		return match_dict


class Agenda(object):
	"""docstring for Agenda"""
	
	@classmethod
	def conflict_resolution(self, conflicts):
		print 'conflict_resolution:'
		for conflict in conflicts:
			# print 'rule:',conflict['rule']
			# print 'result:',conflict['result']
			# print 'doc',conflict['doc']
			return conflict['result']
		# for key,value in conflicts.items():
		# 	print key
		# 	print value
		return None

def main():
	category = u'25.11'
	doc = '铝芯交联聚氯乙烯绝缘聚氯乙烯钢带铠装护套电力电缆  VLV2-22 3*300+1*150'
	result = PatternMatcher.match( category,doc )
	# return agenda.conflict_resolution()
	print 'result:',result

if __name__ == '__main__':
	main()