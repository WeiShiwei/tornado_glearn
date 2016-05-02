#!/usr/bin/python
# -*- coding: utf-8 -*-
import os, sys
sys.path.append( os.path.join( os.path.abspath(os.path.dirname(__file__)) , '../..'))

import requests
import ujson
import unittest
import datetime

class TestApiFunctions(unittest.TestCase):

    def test_api_CrfPredictHandler(self):
        print "test_api_CrfPredictHandler"
        
        data = {
            "identity":"gcj",
            'docs': ujson.dumps([
                {
                    "category":'alt.atheism',
                    'doc':'III级螺纹钢    Φ12mm  HRB400'
                },
                {
                    "category":'alt.atheism',
                    'doc':'III级螺纹钢    Φ12mm  HRB400'
                },
                {
                    "category":'alt.atheism',
                    'doc':'III级螺纹钢    Φ12mm  HRB400'
                }
            ])
        }
        json_result = requests.post('http://127.0.0.1:9700/crf/predict', params=data)
        print ujson.loads(json_result.content)

# Run test cases.
if __name__ == '__main__':
    unittest.main()