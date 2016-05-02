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

class TestApiFunctions(unittest.TestCase):

    @unittest.skip("skip")
    def test_api_EncodeCrfModelHandler(self):
        #根据模型id获取验证过后的训练样本并'全量'训练crf模型

        print 'test_api_EncodeCrfModelHandler'
        data = {
            "crf_model_id":'1491'#1339,1491,1138,1445,1031
        }
        json_result = requests.post('http://127.0.0.1:9700/crf/train_model',data =data)
        print ujson.loads(json_result.content)

    @unittest.skip("skip")
    def test_api_DecodeCrfModelHandler(self):
        print "test_api_DecodeCrfModelHandler"
        
        data = {
            "identity":"gldjc",
            'docs': ujson.dumps([
                # {
                #     "category":'01.01',
                #     'doc':'III级螺纹钢    Φ12mm  HRB400'
                # },
                {
                    "category":'25.11',
                    'doc':'铜芯聚氯乙烯绝缘聚氯乙烯护套控制电缆   KVV 0.6KV   4×1 0.6/1KV'
                }
            ])
        }
        json_result = requests.post('http://127.0.0.1:9700/crf/predict', params=data)
        # print ujson.loads(json_result.content)

    # @unittest.skip("skip")
    def test_api_CrfPredictExtendedHandler(self):
        print "test_api_CrfPredictExtendedHandler"
        
        data = {
            "identity":"gldjc",
            'docs': ujson.dumps([
                {
                    "id":'1',
                    "category":'16.03',
                    'doc':'法兰铜截止阀 DN100 低压 '
                },
                {
                    "id":'2',
                    "category":'25.11',
                    'doc':'电力电缆YJV22-8.7/12KV(3*120)'
                },
                {
                    "id":'3',
                    "category":'25.11',
                    'doc':'铜芯聚氯乙烯绝缘聚氯乙烯护套控制电缆   KVV0.6KV   4×1'
                }
            ])
        }
        json_result = requests.post('http://127.0.0.1:9700/crf/predict', params=data)
        # json_result = requests.post('http://crf.gldjc.com/crf/predict', params=data)
        results = ujson.loads(json_result.content)
        for res in results:
            print 'id:',res['id']
            print 'category',res['category']
            print res['output']
            for key,value in res['attr_value_dict'].items():
                print key,':',value
            print 
        return 

    @unittest.skip("skip")
    def test_api_CrfPredictExtendedHandler_localReport(self):
        crf_files = glob.glob( os.path.join( os.path.abspath(os.path.dirname(__file__)) , 'fengwan','*.txt'))
        for crf_file in crf_files:

            doc_list = list()
            with open( crf_file , 'rb') as infile:
                lines = infile.readlines()
                for line in lines:
                    line = line.strip()
                    doc_list.append({"category":'25.11','doc':line})

            data = {
                "identity":"gldjc",
                'docs':ujson.dumps(doc_list[0:10])
            }
            json_result = requests.post('http://127.0.0.1:9700/crf/predict', params=data)

            results = ujson.loads(json_result.content)
            csv_file = os.path.join(os.path.abspath(os.path.dirname(__file__)) , 'fengwan','上上1.csv') 
            csv_file = os.path.join(os.path.abspath(os.path.dirname(__file__)) , 'fengwan',os.path.basename(crf_file)+'.csv')
            writer = csv.writer(file(csv_file, 'wb'), quoting=csv.QUOTE_ALL)
            writer.writerow(['doc','attr_value','output'])
            for i,res in enumerate(results):
                doc = doc_list[i]['doc']
                output = res['output']            
                attr_value_dict = res['attr_value_dict']
                attr_value_list = list()
                for key,value in attr_value_dict.items():
                    attr_value_list.append( key+':'+value )
                attr_value_res = '\n'.join(sorted(attr_value_list))
                print doc, output, attr_value_res
                writer.writerow([doc,attr_value_res, output])

# Run test cases.
if __name__ == '__main__':
    unittest.main()




