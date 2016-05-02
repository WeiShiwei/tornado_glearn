#!/usr/bin/env python
# -*- coding: utf-8 -*- "
import sys
import getopt
import collections
import csv , json
import global_variables as gv

from logutil import logger

# 评价的对象是chunk（组块），符合要求的条件：chunk中满足阈值的token个数与chunk中token总数量的比值要大于THRESHOLD_CHUNK
THRESHOLD_TOKEN = 0.5 # token的阈值
THRESHOLD_CHUNK = 0.5 # chunk的阈值

# -------------------------------------------------------------------------------------------
def format_filter(tokenList):
    """"""
    # 不等边 B-PZ    0.976013985862
    # 角钢  I-PZ    0.834136196282
    # Q365    B-PH    0.463382254021
    # ∠   B-GG    0.982925221339
    # 32  I-GG    0.997434458493
    # ×   I-GG    0.997178886247
    # 20  I-GG    0.998746399377
    # ×   I-GG    0.997642501001
    # 3   I-GG    0.994130721613
    # 唐钢  B-PZ    0.411566090587
    # 9   B-JGHS  0.963501936894
    # #   I-JGHS  0.978756293914
    # 可能有空行

    # =>

    # 不等边    -    B-PZ/0.976013985862
    # 角钢    -    I-PZ/0.834136196282
    # Q365    -    B-PH/0.463382254021
    # ∠   -    B-GG/0.982925221339
    # 32    -    I-GG/0.997434458493
    # ×    -    I-GG/0.997178886247
    # 20    -    I-GG/0.998746399377
    # ×    -    I-GG/0.997642501001
    # 3    -    I-GG/0.994130721613
    # 唐钢    -    B-PZ/0.411566090587
    # 9    -    B-JGHS/0.963501936894
    # #    -    I-JGHS/0.978756293914

    tokenListBak = list()
    for token in tokenList:
        if token == '':
            continue
        elemList = token.split()
        if len(elemList) == 3:
            elemList[2] = elemList[1]+'/'+elemList[2]
            elemList[1] = '-'
        tokenListBak.append( '\t'.join(elemList) )
    return tokenListBak

def conlleval(tokenList , return_json=True):
    """tokenList是list[token1,token2,...]

    conlleval(para)有一个很隐秘的'错误'，就是同一个句子里面可能有2个或
    多个组块由同一个Chunk Tag，可能一个chunk不符合评价，但是被同chunk tag的
    其他chunk所影响，对该chunk tag而言符合评价。但是我想在某种角度上并不影响最终的抽取，
    留下token数量最长的组块就行了"""

    if tokenList == list():
        return None

    tag_prob_dict = collections.defaultdict(list)#字典{key=str，list[p1,p2...]}
    tag_word_dict = collections.defaultdict(list)    
    if tokenList[0].startswith('# 0'):
        tokenList = tokenList[1:] # tokenList的开头都有一个总体概率，即似[# 0.000061],舍弃之
    
    last_tag = ''
    for tokenstr in tokenList:
      if tokenstr.strip().startswith('# 0'):
        continue
      (word,pos,tagprob) = tokenstr.split()
      (tag,prob) = tagprob.lstrip("BI").lstrip("-").split("/")
      if tagprob.startswith("B") or len(tag_prob_dict[tag]) == 0 or (last_tag.startswith('I') and not tagprob.startswith('I')):
        tag_prob_dict[tag].append( [] )
        tag_word_dict[tag].append( [] )
      tag_prob_dict[tag][-1].append(float(prob))
      tag_word_dict[tag][-1].append(str(word))
      last_tag = tagprob    
    
    correct_dict = dict()
    error_dict = dict()
    
    #遍历tag_prob_dict
    for (key, prob_list) in tag_prob_dict.items():
      if not error_dict.has_key(key):
        error_dict[key] = []
      if not correct_dict.has_key(key):
        correct_dict[key] = []
      for i in range( len(prob_list) ):
        ave_prob = sum(prob_list[i])/len(prob_list[i])
        word = ''.join(tag_word_dict[key][i])
        if isQualified(prob_list[i]) == False:
            error_dict[key].append([word , ave_prob])
            continue
        correct_dict[key].append([word , ave_prob])
    
    if len([ v for v in error_dict.values() if len(v) > 0 ])>0:
        res = 'error'
    else:
        res = 'correct'
    if return_json:
      return [ res , json.dumps(correct_dict) , json.dumps(error_dict) , restore(tokenList) ]
    else:
      return [ res , correct_dict , error_dict , restore(tokenList) ]

def isQualified(probList):
    #例如key=JYCL,probList=[0.352625,0.333246]
    count = 0
    for f in probList:
        if(float(f) < THRESHOLD_TOKEN):
            count += 1
    if float(count)/float(len(probList)) >= THRESHOLD_CHUNK: #python2.7
        return False
    return True

def restore(tokenList):
  resultList = []
  i = 0
  while i < len(tokenList):
    tokenstr = tokenList[i]
    if tokenstr.strip().startswith('# 0'):
      i += 1
      continue
    (word,pos,tagprob) = tokenstr.split()
    (chunktag,prob) = tagprob.lstrip("BI").lstrip("-").split("/")

    if chunktag == 'O':
        if word == '@Sp':
            word = ' '
        resultList.append(word)
        i += 1
    else:
        chunkStr="<"+chunktag+">" #
        tag = chunktag # chunkTag is const in else branch
        while tag == chunktag:
            (word,pos,tagprob) = tokenList[i].split()
            chunkStr +=  word
            i += 1
            if i >= len(tokenList):
                break
            if tokenList[i].strip().startswith('# 0'):
              i += 1
            (word,pos,tagprob) = tokenList[i].split()
            (tag,prob) = tagprob.lstrip("BI").lstrip("-").split("/")
        chunkStr += "</"+chunktag+">"
        resultList.append(chunkStr)
  labeledline = "".join(resultList)
  return labeledline

if __name__ == "__main__":
    assessfile(u"/home/johnson/workspace/glodon/800w_classifier/crf_attrextractor/data/results/raw/c5f5d0a32ac4a200ae74ae1f62ea4b53.csv" , u"/home/johnson/workspace/glodon/800w_classifier/crf_attrextractor/data/results/parsed/c5f5d0a32ac4a200ae74ae1f62ea4b53.csv")
    # assessfile(r"../test.data" , model_file=r"../dldl-model")
