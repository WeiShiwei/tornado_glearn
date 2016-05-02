#!/usr/bin/python
# -*- coding: utf-8 -*-
import os, sys
sys.path.append( os.path.join( os.path.abspath(os.path.dirname(__file__)) , '../..'))

import requests
import ujson
import unittest

class TestApiFunctions(unittest.TestCase):
    
    @unittest.skip("skip")
    def test_api_TrainCrfModelHandler(self):
        #根据模型id获取验证过后的训练样本并'全量'训练crf模型
        print 'test_api_TrainCrfModelHandler'
        data = {
            "crf_model_id":'1027'#1339,1491,1138,1445,1031
        }
        json_result = requests.post('http://127.0.0.1:9700/crf/train_model',data =data)
        print ujson.loads(json_result.content)
    #--------------------------------------------------------------------------------------------------------------
    @unittest.skip("skip")
    def test_api_DecodeHandler(self):
        print "test_api_DecodeHandler"
        data = {
            "decode_datas":
                "1 1491 '铝芯交联聚氯乙烯绝缘聚氯乙烯钢带铠装护套电力电缆  VLV2-22 3*300+1*150'\n"+
                "2 1491 '铜芯聚氯乙烯绝缘聚氯乙烯护套控制电缆   KVV 0.6KV   3*120+1'\n"+
                "3 1027 'PVC排水管件-立体四通   φ200'\n"+
                "4 858 '不等边角钢 Q365∠32×20×3 唐钢 9#'\n"+
                "5 1339 '三级螺纹钢  20 材质: HRB400E'\n"
                "6 3 '三级螺纹钢  20 材质: HRB400E'"
        }
        # data= {"decode_datas":"1 1131 '铜芯聚氯乙烯绝缘包铝电线 ZR-BVC 金川 百米 70mm²'"}
        # data = {"decode_datas":"1 1435 湿式自动喷水报警阀 HT300材料(外部平衡) 西安消防 套 ZFSZ-150"}
        # data = {"decode_datas":"1 1131 '铜芯聚氯乙烯绝缘包铝电线 ZR-BVC 金川 百米 70mm²'"}
        # data = {"decode_datas":"1 1491 '铝芯交联聚氯乙烯绝缘聚氯乙烯钢带铠装护套电力电缆  VLV2-22 3*300+1*150'"}
        json_result = requests.post('http://127.0.0.1:9700/crf/decode', params=data)
        results = ujson.loads(json_result.content)
        for res in results:
            print res['output_str']
            for key,value in res['attr_value_dict'].items():
                print key,':',value
            print 
        return 
    #------------------------------------------------------------------------------------------------------------------------------------        
    # @unittest.skip("skip")
    def test_api_CrossValidateHandler(self):
        """
        要求安装perl
        processed 67077 tokens with 17939 phrases; found: 17961 phrases; correct: 17629.
        accuracy:  99.50%; precision:  98.15%; recall:  98.27%; FB1:  98.21
                    BCJMM: precision:  96.22%; recall:  99.52%; FB1:  97.84  3863
                    EDDYK: precision: 100.00%; recall: 100.00%; FB1: 100.00  1047
                       PZ: precision: 100.00%; recall:  69.51%; FB1:  82.01  310
                       XS: precision:  99.63%; recall:  97.56%; FB1:  98.58  4894
                     XXCZ: precision:  96.40%; recall: 100.00%; FB1:  98.17  3780
                      XXX: precision:  99.21%; recall:  99.16%; FB1:  99.19  4067
        """
        print 'test_api_CrossValidateHandler'
        data = {
            "first_type_code":'25',# "crf_model_id"='1491'
            "second_type_code":'11',         
            'kfold':'5'
        }
        json_result = requests.get('http://127.0.0.1:9700/crf/cross_validate',params =data)
        print ujson.loads(json_result.content['output'])
    
        



# Run test cases.
if __name__ == '__main__':
    unittest.main()




