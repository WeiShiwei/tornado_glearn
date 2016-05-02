#!/usr/bin/env python
# -*- coding: utf-8 -*- 
# Copyright (c) 2014 Qtrac Ltd. All rights reserved.
"""
This module provides a few CRF string manipulation functions.

"""
import os
import sys
import re
import string
import commands
import collections
import tempfile
import requests
import ujson

import datasets
import crfpp_options

import global_variables as gv
import jieba.posseg as pseg

WordFlag = collections.namedtuple("WordFlag","word flag")
from jpype_util import JPype
from stemmed import Stemmed

# ------------------------------------------------------------------------------
class CrfppUtil(object):
    """docstring for CrfppUtil"""
    ansj_seg = JPype()
    prog_chn = re.compile(ur'([\u4e00-\u9fa5]+)') #这里是精髓，[\u4e00-\u9fa5]是匹配所有中文的正则，因为是unicode形式，所以也要转为ur
    
    def __init__(self, arg):
        super(CrfppUtil, self).__init__()
        self.arg = arg
    
    @classmethod
    def section(self, doc_str):
        """ 电缆NHYJV-5*2.5 => '电缆 NHYJV-5*2.5' """
        # vi. 被切割成片；被分成部分
        # vt. 把…分段；将…切片；对…进行划分
        doc_content_origin = doc_str.decode('utf-8')
        doc_content_sectioned = ' '.join( CrfppUtil.prog_chn.split(doc_content_origin)).strip() #使用re库的split切割
        
        # print "doc_content_origin:",doc_content_origin
        # print "doc_content_sectioned",doc_content_sectioned
        return doc_content_sectioned

    @classmethod
    def __ansj_seg(self, content, tool = 'ansj_seg'):
        """ 默认使用ansj_seg分词工具 """
        if tool == 'ansj_seg':
            ws = CrfppUtil.ansj_seg.cut(content)
            return ws
        else:
            return pseg.cut( content )

    @classmethod
    def tokenize_with_unlabeled(self, unLabeledPhrase):
        """ '10KV铜芯电缆NH-VV22...'
            result:postag_file
            10    m 
            KV    eng 
            铜芯    bm 
            电缆    bm 
            NH    eng 
            -    x 
            VV22    eng 
            ...   
        """
        token_list = []
        # ws = pseg.cut( unLabeledPhrase )
        ws = CrfppUtil.__ansj_seg( unLabeledPhrase )
        for w in ws:
          if len(w.word.strip()) == 0:
            continue
          else:
            token = w.word +'\t'+ w.flag
            token_list.append(token)
        # import pdb;pdb.set_trace()
        return [token.encode('utf-8') for token in token_list]
        # return token_list

    @classmethod
    def tokenize_with_labeled(self, labeledPhrase):
        """
        labeledPhrase:
            <EDDY>10KV</EDDY><XXCZ>铜芯</XXCZ>电缆<GG>NH-VV22</GG> <GG>Q250</GG> (注意可以有空格)
        example:token_list
            10  m   B-EDDY
            KV  eng I-EDDY
            铜芯  bm  B-XXCZ
            电缆  bm  O
            NH  eng B-GG
            -   x   I-GG
            VV22    eng I-GG
            /   x   O
            @   x   O
            ...
        """
        token_list = []
        prog = re.compile(r"(<[/]?\w+>)")
        chunkList=prog.split(labeledPhrase)
        
        chunkTag = 'O'
        for chunk in chunkList:   
            if chunk.strip() == '':
                continue
            
            if not prog.match(chunk): # chunk = "10/m KV/eng"
                if chunkTag == 'O':
                    sen = chunk.strip().replace(" ","")
                    # ws = pseg.cut( sen ) 
                    ws = CrfppUtil.__ansj_seg( sen )
                    for w in ws:
                        token = w.word +'\t'+ w.flag +'\t'+'O'
                        token_list.append(token)             
                else:
                    sentinel = True
                    sen = chunk.strip().replace(" ","")
                    # ws = pseg.cut( sen ) 
                    ws = CrfppUtil.__ansj_seg( sen )
                    for w in ws:
                        if sentinel:
                            token = w.word +'\t'+ w.flag +'\t'+"B-"+ chunkTag  # B or I
                            sentinel = False
                        else:
                            token = w.word +'\t'+ w.flag +'\t'+"I-"+ chunkTag  # B or I 
                        token_list.append(token)
                continue

            m1=re.match('<(?P<tag>\w+)>',chunk) #chunk = "<DXTZ>"
            if m1:
                if chunkTag != 'O':
                    return None #format error(...<A>*<B>...)
                chunkTag=m1.group("tag") 
                continue
            
            m2=re.match('</(?P<tag>\w+)>',chunk) #chunk = "</DXTZ>"
            if m2:
                tag = m2.group("tag")
                if tag == chunkTag:                
                    chunkTag = 'O'
                    continue
                elif chunkTag == 'O':
                    return None #format error(...</A>*</B>...)
                else:
                    return None #format error(...<A>*</B>...)
        if chunkTag == 'O':
            return [token.encode('utf-8') for token in token_list]
            # return token_list
        else:
            return None #format error(...<A>*)

class EncodeUtil(CrfppUtil):
    """docstring for EncodeUtil
        训练模型应用到的结巴分词是本地的，加载词典所需时间相比于训练模型所需的时间很少
    """
    def __init__(self, arg):
        super(EncodeUtil, self).__init__()
        self.arg = arg

    @classmethod
    def tokenize(self, sentence): 
        sentence = unicode(Normalize.normalize( sentence )) ### 'unicode'=>'utf-8'

        prog = re.compile(ur"(<[/]?\w+>)",re.U)
        chunkList=prog.split(sentence)
        if len(chunkList) > 2:
            # -------------------------------------------------------------
            # 对于标注的语句格式可能存在错误，分为qualified and unqualified两种情况，后者要抛出异常
            # print sentence
            res = list()

            sentence = sentence.replace(u"，",' ')
            sentence = sentence.replace(u"。",' ')
            #\ sentence = '，'.join(sentence.split()) #这是中文的逗号(英文的'逗号'=',')
            #\ labeled_phrase_list = prog_sep.split(sentence) # unlabeled_phrase_list是历史遗留问题，暂时不改动名称了
            
            labeled_phrase_list=sentence.split()#这一部分需要把组块内部的空格去除，有可扩展的空间;但是不能让其报错出现中断 
            for labeled_phrase in labeled_phrase_list:
                if labeled_phrase == '':
                    continue
                token_list = super(EncodeUtil, self).tokenize_with_labeled(labeled_phrase) #'\x'->'\u'
                if token_list is None:
                    raise Exception()
                res.append('\n'.join(token_list)+'\n')
            # -------------------------------------------------------------
            if res:
                return '\n'.join(res)+'\n'
            else:
                return '\n'
        else:
            #这里视未标注的(但是labeled=True)语句的组块标示全为O
            token_list = super(EncodeUtil, self).tokenize_with_unlabeled(sentence)
            for i in range(len(token_list)):
                token_list[i] += '\tO'
            return '\n'.join(token_list)+'\n'

    @classmethod
    def tokenize_samples(self, crf_labeled_samples):
        """ """
        crf_tokenized_samples = list()
        crf_labeled_samples_unqualified = list()

        if crf_labeled_samples is None:
            return (list(),list())
        
        for i in range(len(crf_labeled_samples)):
            sample = crf_labeled_samples[i]
            # import pdb;pdb.set_trace()
            try:
                sample_tokenized = EncodeUtil.tokenize( sample )
            except Exception, e:
                crf_labeled_samples_unqualified.append( sample )
                continue
            crf_tokenized_samples.append(sample_tokenized)                         
        return crf_labeled_samples_unqualified, crf_tokenized_samples
    # -*- Discarded -*- #
    # @classmethod
    # def tokenize_for_encode(self, crf_labeled_samples):
    #     reload(sys)
    #     sys.setdefaultencoding( "utf-8" )

    #     crf_tokenized_samples = list()
    #     for line in crf_labeled_samples:
    #         line = line.strip()
    #         if line == '':
    #             continue
    #         # 我觉得好的编程实践不要把函数调用设计的太深
    #         # 一个函数做一件事，不要越俎代庖
    #         # ----------------------------------------------------------------------
    #         # 这里做一个基本的假设（同时也是对标注人员的要求）:标注的组块内部不能有空白符
    #         # <JB>III级 </JB>螺纹钢    <ZJM>φ12mm</ZJM>  <PH>HRB400</PH> -> 'error' labeling
    #         sentence = crf_uniformizer.uniformize(line)#替换特殊字符为自定义标准的一套字符
            
    #         # ----------------------------------------------------------------------
    #         phrase_granularity_train_corpus=''
    #         phrase_list=sentence.split()#这一部分需要把组块内部的空格去除，有可扩展的空间;但是不能让其报错出现中断    
    #         for phrase in phrase_list:
    #             phrase_granularity_train_corpus += EncodeUtil.tokenize(phrase)+'\n'
            
    #         # ----------------------------------------------------------------------
    #         crf_tokenized_samples.append(phrase_granularity_train_corpus+'\n')
    #     return crf_tokenized_samples

# 继承的意义不大
class DecodeUtil(CrfppUtil):
    """docstring for DecodeUtil
        解码操作通过tornado访问web服务的结巴分词
    """
    def __init__(self, arg):
        super(DecodeUtil, self).__init__()
        self.arg = arg
    
    @classmethod
    def tokenize(self, sentence):
        sentence = unicode(Normalize.normalize( sentence ))

        # sentence有两种形式：
        # （1）'III级铜芯聚氯乙烯绝缘聚氯乙烯护套控制电缆   KVV 0.6KV   4×1'=>
        #      'III级铜芯聚氯乙烯绝缘聚氯乙烯护套控制电缆，KVV，0.6KV，4×1'
        # （2）'陶象国在上海出生并在香港受教育，后来成了一名儿科医生。梁蕙兰是物理和数学专业的高才生，曾做过中学数学教师。'
        # -------------------------------------------------------------
        sentence = sentence.replace(u"，",' ')
        sentence = sentence.replace(u"。",' ')
        #\ sentence = '，'.join(sentence.split()) #这是中文的逗号(英文的'逗号'=',')
        #\ unlabeled_phrase_list = prog_sep.split(sentence) # unlabeled_phrase_list是历史遗留问题，暂时不改动名称了
        # import pdb;pdb.set_trace()###

        res = list()
        unlabeled_phrase_list=sentence.split() ###
        for unlabeled_phrase in unlabeled_phrase_list:
            if unlabeled_phrase == '':
                continue
            token_list = super(DecodeUtil, self).tokenize_with_unlabeled(unlabeled_phrase)
            # print '\n'.join(token_list)+'\n' # for debug
            res.append('\n'.join(token_list)+'\n')
        # -------------------------------------------------------------        
        if res:   
                return '\n'.join(res)+'\n'
        else:
            return '\n'

    @classmethod
    def tokenize_docs(self, sentences):
        res_list = list()
        for sentence in sentences:
            output_conll = DecodeUtil.tokenize(sentence)
            res_list.append(output_conll.strip())
        return res_list

class Normalize(object):
    """docstring for Normalize"""
    stem = Stemmed()
    def __init__(self, arg):
        super(Normalize, self).__init__()
        self.arg = arg
    
    @classmethod
    def normalize(self, doc):
        return Normalize.stem.stemming(doc)

    # @classmethod
    # def normalize_docs(self, docs):
    #     retunr Normalize.stem.stemming_docs(docs)



def main():
    ansj_seg = JPype()

    # content = u"合金圆锯片  50/100KW WQ100-App4mm"
    # content = u'S4 63ppr稳态管  公称外径：65（mm） 壁厚：7.4（mm）长度：4（m）产品规格：63'
    content = u'PVC排水管件-立体四通   φ200'


    # ws = ansj_seg.cut(content)
    # print ws 

    print DecodeUtil.tokenize(content)

    import pdb;pdb.set_trace()



if __name__ == "__main__":
    main()