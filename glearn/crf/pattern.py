#!/usr/bin/env python
# -*- coding: utf-8 -*- "
import os
import sys
import getopt
import collections
import csv , json
import re
from time import time

from logutil import logger
import global_variables as gv
import orm

from glearn.crf.datasets import datasets
from glearn.crf.crfpputil import Normalize
from glearn.rule.inference_engine import PatternMatcher
from glearn.specification.spec_template import specificationTemplate


class PatternMatchEngine(object):
    """ 模式匹配引擎 """
    
    @classmethod
    def __packing(self,tokenList):
        """
        tokenList:
			橡套	O	0.999437782462
			电缆	O	0.999528699368
			YC	B-XXX	0.999724657583
			5	B-XS	0.999244194846
			#	I-XS	0.999244194846 =>为了试验鲁棒性,自己填的一行
			*	O	0.999995518173
			78	B-BCJMM	0.979645961503
			+	O	0.999998658246
			3	B-XS	0.999511994139
			*	O	0.999999890698
			25	B-BCJMM	0.999750221636
        
        =>
        word_list=[橡套 电缆 YC 5# * 78 + 3 * 25]
        chunktag_list=[O O XXX XS O BCJMM O XS O BCJMM]
        """
        word_list = list()
        chunktag_list = list()
        prob_list = list()
        index = 0
        previous_chunktag = ''

        for token in tokenList:
            if token.strip() == '':
                continue
            
            items = token.split()
            if len(items)==3:
                chunktag = ''
                BITag = items[1].split('-')
                if len(BITag)>1:
                    chunktag = BITag[1]
                else:
                    chunktag = 'O'
                (word,chunktag,prob) = (items[0],chunktag,items[2])
                
                if chunktag == previous_chunktag and BITag[0]=='I': ###
                    word_list[len(word_list)-1] += word                    
                    prob_list[len(prob_list)-1] += '+'+prob ###
                else:
                    word_list.append(word)
                    chunktag_list.append(chunktag)
                    prob_list.append(prob) #
                    previous_chunktag = chunktag
            else:
                logger.error("matching encountered an error,output_str=\n%s"%('\n'.join(tokenList)))

        return (word_list,chunktag_list,prob_list)

    @classmethod
    def __sub_boundary(self,match_list,chunktag_list,word_list):
    	"""
    	['XS', '*', 'BCJMM', '+', 'XS', '*', 'BCJMM']
    	=>match_list = ['XS', 'O', 'BCJMM', 'O', 'XS', 'O', 'BCJMM']

    	word_list = [橡套 电缆 YC 5# * 34 + 6 * 45]
		chunktag_list = [O O XXX XS O BCJMM O XS O BCJMM]
    	"""
    	(beg,end) = (-1,-1)
    	for i in range(len(chunktag_list)):
    		if chunktag_list[i:i+len(match_list)] == match_list:
    			(beg,end) = (i,i+len(match_list))
    			break
    	return (beg,end)	

    @classmethod
    def __matching(self, crf_model_id, first_type_code, second_type_code, output_str):
        """ output_str:
            橡套	O	0.999437782462
			电缆	O	0.999528699368
			YC	B-XXX	0.999724657583
			5	B-XS	0.999244194846
			#	I-XS	0.999244194846 =>自己填的一行
			*	O	0.999995518173
			78	B-BCJMM	0.979645961503
			+	O	0.999998658246
			3	B-XS	0.999511994139
			*	O	0.999999890698
			25	B-BCJMM	0.999750221636
        """
        tokenList = output_str.split('\n')
        (word_list,chunktag_list,prob_list) = PatternMatchEngine.__packing(tokenList)
        
        attr_value_dict = collections.defaultdict(str) # {非集合属性:属性值}
        # xxx_attr_value_dict = dict() # {集合属性:属性值} # ----------
        chunktag_prob_dict = dict() # 相关概率值
        for i in range(len(chunktag_list)):
            chunktag = chunktag_list[i]
            assembly_attr_name = word_list[i]
            # -----------------------------------------------------------
            if chunktag == 'O' or chunktag == 'XXX':
                continue
            # if chunktag == 'O':
            #     continue
            # if chunktag == 'XXX':
            #     集成属性扩展code
            #     continue
            # -----------------------------------------------------------

            if attr_value_dict.get(chunktag) is None:
                attr_value_dict[chunktag] = word_list[i]
                chunktag_prob_dict[chunktag] = prob_list[i]
            else:
                # 如果字典中已经存在chunktag项，则比较对应的概率，取概率较大的项
                current_average_prob = eval(prob_list[i])/len(prob_list[i].split('+'))
                previous_average_prob = eval(chunktag_prob_dict[chunktag])/len(chunktag_prob_dict[chunktag].split('+'))
                if current_average_prob > previous_average_prob:
                    attr_value_dict[chunktag] = word_list[i]
                    chunktag_prob_dict[chunktag] = prob_list[i]
        
        # 把属性字符简写(chunkTag)过滤为二级类别标准属性描述
        chunkTag_attrName_dict = PatternMatchEngine.expand_chunkTag(first_type_code,second_type_code)
        attrDesc_value_dict = dict()
        for (key,value) in attr_value_dict.items():
            attrDesc_value_dict[chunkTag_attrName_dict.get(key,'')] = value        
        
        # 扩展集合属性，优先级最高
        # attrDesc_value_dict.update(xxx_attr_value_dict) # ----------
        
        for (key,value) in attrDesc_value_dict.items():
            attrDesc_value_dict[key] = value.strip()
        
        return attrDesc_value_dict

    baseMaterialTypeAttr_cache = dict()
    @classmethod
    def expand_chunkTag(self,first_type_code,second_type_code):
        chunkTag_attrName_dict = PatternMatchEngine.baseMaterialTypeAttr_cache.get(first_type_code+second_type_code,None)
        if chunkTag_attrName_dict:
            return chunkTag_attrName_dict
        else:
            chunkTag_attrName_dict = orm.BaseMaterialTypeAttr.get_chunkTag_attrName_dict(first_type_code,second_type_code)
            PatternMatchEngine.baseMaterialTypeAttr_cache[first_type_code+second_type_code] = chunkTag_attrName_dict
            return chunkTag_attrName_dict

    @classmethod
    def pattern_matching(self, output_str, category, initial_doc):
        crf_model_id, first_type_code, second_type_code = datasets.fetch_complete_info(category)
        chunkTag_attrName_dict = PatternMatchEngine.expand_chunkTag(first_type_code,second_type_code)
        
        # 结构化CRF处理后output文本
        attr_value_dict = PatternMatchEngine.__matching( crf_model_id, first_type_code, second_type_code, output_str)

        # 初始文档的规范化
        normalized_doc = Normalize.normalize(initial_doc)
        # 
        match_dict = PatternMatcher.match(category=category, doc=normalized_doc)
        # 基于完全匹配
        xxx_attr_value_dict = dict() # {集合属性:属性值}
        try:
            assembly_attr_name = match_dict['XXX']
            del match_dict['XXX']
            # xxx_attr_value_dict.update( specificationTemplate.retrieve_template_dict(category,assembly_attr_name) )
            xxx_attr_value_dict['型号'] = assembly_attr_name
            print "型号的完全匹配:",xxx_attr_value_dict
        except Exception, e:
            raise e
        # 基于正则匹配
        attrDesc_value_dict = dict()
        regex_match_dict = match_dict
        for (key,value) in regex_match_dict.items():
            attrDesc_value_dict[chunkTag_attrName_dict.get(key,'')] = value   
        print "正则匹配:",attrDesc_value_dict

        attrDesc_value_dict.update(xxx_attr_value_dict)
        # --------------------------------------------------------
        # 正则匹配 done in 0.000320s
        # 正则匹配: {u'\u6807\u79f0\u622a\u9762(mm\xb2)': u'1', u'\u82af\u6570': u'4'}
        # 正则匹配 done in 0.000060s
        # 完全匹配 done in 0.000020s
        # 完全匹配: {'XXX': u'KVV'}
        # 完全匹配 done in 0.021801s => 0.000019s(加缓存)
        # --------------------------------------------------------

        attr_value_dict.update( attrDesc_value_dict )
        
        return dict((k, v) for k, v in attr_value_dict.items() if k!='')

    @classmethod
    def structuring(self,output_str):
        """ output_str:
            橡套  O   0.999437782462
            电缆  O   0.999528699368
            YC  B-XXX   0.999724657583
            5   B-XS    0.999244194846
            #   I-XS    0.999244194846 =>自己填的一行
            *   O   0.999995518173
            78  B-BCJMM 0.979645961503
            +   O   0.999998658246
            3   B-XS    0.999511994139
            *   O   0.999999890698
            25  B-BCJMM 0.999750221636
        """ 
        attr_value_dict = collections.defaultdict(str)
        tokenList = output_str.split('\n')
        (word_list,chunktag_list,prob_list) = PatternMatchEngine.__packing(tokenList)

        chunktag_prob_dict = dict()
        for i in range(len(chunktag_list)):
            chunktag = chunktag_list[i]
            if chunktag == 'O':
                continue

            if attr_value_dict.get(chunktag) is None:
                attr_value_dict[chunktag] = word_list[i]
            else:
                attr_value_dict[chunktag] = attr_value_dict[chunktag]+ ' ' + word_list[i]
        return attr_value_dict