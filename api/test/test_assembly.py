# coding=utf-8
u"""
User: weihaixin
Date: 14-08-21
"""
import os, sys
sys.path.append( os.path.join( os.path.abspath(os.path.dirname(__file__)) , '../..'))

import requests
import ujson
import unittest

class TestApiFunctions(unittest.TestCase):

#------------------------------------------------------------------------------------------------------------------------------------#        
    # def test_api_CreateAssemblyTemplateHandler(self):
    #     """table base_material_type_attr_sets"""
    #     print 'test_api_CreateAssemblyTemplateHandler'
    #     data = {
    #         # 'first_type_code': '99',
    #         # 'second_type_code': '88',
    #         # 'assembly_attr_name': 'JYV300'
    #         'first_type_code': '25',
    #         'second_type_code': '11',
    #         'assembly_attr_name': 'KVV'
    #     }
    #     requests.post('http://127.0.0.1:9700/v1/assembly/create_template', data=data)

    def test_api_RetrieveAssemblyTemplateHandler(self):
        print 'test_api_RetrieveAssemblyTemplateHandler'
        data = {
            # 'first_type_code': '99',
            # 'second_type_code': '88',
            # 'assembly_attr_names': 'JYV300'#space split
            'first_type_code': '25',
            'second_type_code': '11',
            'assembly_attr_names': 'KVV'#space split
        }
        json_result = requests.get('http://127.0.0.1:9700/v1/assembly/retrieve_template', params=data)
        print ujson.loads(json_result.content)
        # url= 'http://127.0.0.1:9700/v1/assembly/retrieve?assembly_attr_name=JYV200&first_type_code=99&second_type_code=88'

    # def test_api_RetrieveLv2AssemblyTemplateHandler(self):
    #     """"""
    #     print 'RetrieveLv2AssemblyTemplateHandler'
    #     data = {
    #         'first_type_code': '99',
    #         'second_type_code': '88',
    #         'page':'1',
    #         'pagesize':'10'
    #     }
    #     json_result = requests.get('http://127.0.0.1:9700/v1/assembly/retrieve_lv2Template', params=data)
    #     print ujson.loads(json_result.content)
        # import pdb;pdb.set_trace()
        # http://127.0.0.1:9700/v1/assembly/retrieve_lv2Template?first_type_code=99&second_type_code=88&pagesize=10&page=0
        # {"pageNum":"1","first_type_code":"99","second_type_code":"88","lv2_id_attrValue_dict":{"1":"JYV200","2":"ABC300"}}

    # def test_api_DeleteAssemblyTemplateHandler(self):
    #     print 'test_api_DeleteAssemblyTemplateHandler'
    #     data = {
    #         'base_material_type_attr_set_id':'2'
    #         #\ 'assembly_attr_name': 'JYV200'
    #     }
    #     requests.post('http://127.0.0.1:9700/v1/assembly/delete_template', data=data)
# #------------------------------------------------------------------------#
    # def test_api_CreateAssemblyAttrValPairHandler(self):
    #     print 'CreateAssemblyAttrValPairHandler'
    #     data = {
    #         'base_material_type_attr_set_id':'1',
    #         'base_material_type_attr_id':'2',
    #         'assembly_attr_value':'300v'
    #     }
    #     requests.post('http://127.0.0.1:9700/v1/assembly/create_attrValPair',data=data)


    # def test_api_DeleteAssemblyAttrIdValPairHandler(self):
    #     """attr_set_value_id"""
    #     print 'DeleteAssemblyAttrIdValPairHandler'
    #     data = {
    #         'attr_set_value_id':'1'
    #     }
    #     requests.post('http://127.0.0.1:9700/v1/assembly/delete_attrIdValPair',data=data)



    # def test_api_RetrieveAssemblyAttrValPairsHandler(self):
    #     print 'RetrieveAssemblyAttrValPairsHandler'
    #     data = {
    #         'base_material_type_attr_set_id':'1',
    #         'page':'1',
    #         'pagesize':'10'
    #     }
    #     json_result = requests.get('http://127.0.0.1:9700/v1/assembly/retrieve_attrValPairs',params=data)
    #     print ujson.loads(json_result.content)
        # {"base_material_type_attr_set_id":"1","pageNum":"1","assembly_id_attrVal_dict":{"1":"\u805a\u6c2f\u4e59\u70ef(\u6750\u8d28)","2":"200V(\u989d\u5b9a\u7535\u538b)"}}
# #------------------------------------------------------------------------#


# Run test cases.
if __name__ == '__main__':
    unittest.main()




