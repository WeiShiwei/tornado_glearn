# coding=utf-8
u"""
User: xulin
      Jerry.Fang
Date: 13-12-19
"""
import os, sys
sys.path.append( os.path.join( os.path.abspath(os.path.dirname(__file__)) , '../..'))
sys.path.append( os.path.join( os.path.abspath(os.path.dirname(__file__)) , '../../glearn/crf/ixx_glodon'))

import requests
import ujson
import unittest
from template.basic_template_generator import BasicTemplate
from extractor.data_extractor import template_redis
from model.session import *
from model.basic_element import BasicElement
from statistic.stat_info_querier import StatInfoQuerier
from model.base_material_type import *
from model.base_material_type_attr import *
from model.base_material_type_attr_value import *
from model.base_material_type_attr_rule import *
from model.base_material_type_attr_key_word import *
from sqlalchemy.orm import aliased

class TestApiFunctions(unittest.TestCase):

    # def setUp(self):
    #     # Initial test database.
    #     m_basic_template = BasicTemplate()
    #     m_basic_template.set_primary_path('../../../InputFile_test/primary_rule.xls')
    #     m_basic_template.clean_table()
    ### 增删改查template
    # def test_api_add_all_value_template(self):
    #     data = {
    #         'templates': ujson.dumps([
    #             {
    #                 'first_type_code': '99',
    #                 'second_type_code': '88',
    #                 'first_type_name': '测试类lv1',
    #                 'second_type_name': '测试类lv2',
    #                 'attr_name': '测试类attr_name1(mm2)',
    #                 'attr_val': '15mm2',
    #             },
    #             {
    #                 'first_type_code': '99',
    #                 'second_type_code': '88',
    #                 'first_type_name': '测试类lv1',
    #                 'second_type_name': '测试类lv2',
    #                 'attr_name': '测试类attr_name2(mm2)',
    #                 'attr_val': '16',
    #             },
    #         ])
    #     }
    #     requests.post('http://127.0.0.1:9700/v1/template/create', data=data)#>
    #     parent_bmt = aliased(BaseMaterialType)
    #     with get_session() as session:
    #         be = session.query(BaseMaterialType, parent_bmt, BaseMaterialTypeAttr, BaseMaterialTypeAttrValue).join((parent_bmt, parent_bmt.id == BaseMaterialType.parent_id)).join(BaseMaterialType.base_material_type_attrs).join(BaseMaterialTypeAttr.base_material_type_attr_values)\
    #         .filter(BaseMaterialType.code == u'88', parent_bmt.code == u'99', BaseMaterialTypeAttr.description==u'测试类attr_name1(mm2)', BaseMaterialTypeAttrValue.description==u'15mm2').all()
    #         self.assertEqual(1, len(be))
        
    #     with get_session() as session:
    #         be = session.query(BaseMaterialType, parent_bmt, BaseMaterialTypeAttr, BaseMaterialTypeAttrValue).join((parent_bmt, parent_bmt.id == BaseMaterialType.parent_id)).join(BaseMaterialType.base_material_type_attrs).join(BaseMaterialTypeAttr.base_material_type_attr_values)\
    #         .filter(BaseMaterialType.code == u'88', parent_bmt.code == u'99', BaseMaterialTypeAttr.description==u'测试类attr_name2(mm2)', BaseMaterialTypeAttrValue.description==u'16mm2').all()
    #         self.assertEqual(1, len(be))

    #     with get_session() as session:
    #         be = session.query(BaseMaterialType, parent_bmt, BaseMaterialTypeAttr).join((parent_bmt, parent_bmt.id == BaseMaterialType.parent_id)).join(BaseMaterialType.base_material_type_attrs)\
    #         .filter(BaseMaterialType.code == u'88', parent_bmt.code == u'99', BaseMaterialTypeAttr.description==u'测试类attr_name1(mm2)', BaseMaterialTypeAttr.is_all_match==True).all()
    #         self.assertEqual(1, len(be))

    #     with get_session() as session:
    #         be = session.query(BaseMaterialType, parent_bmt, BaseMaterialTypeAttr, BaseMaterialTypeAttrRule).join((parent_bmt, parent_bmt.id == BaseMaterialType.parent_id)).join(BaseMaterialType.base_material_type_attrs).join(BaseMaterialTypeAttr.base_material_type_attr_rules)\
    #         .filter(BaseMaterialType.code == u'88', parent_bmt.code == u'99', BaseMaterialTypeAttr.description==u'测试类attr_name2(mm2)', BaseMaterialTypeAttrValue.description==u'16mm2', BaseMaterialTypeAttrRule.rule_description==u'\d+[.]{0,1}\d*[/]{0,1}\d*mm2').all()
    #         self.assertEqual(1, len(be))
    #         be = session.query(BaseMaterialType, parent_bmt, BaseMaterialTypeAttr, BaseMaterialTypeAttrRule).join((parent_bmt, parent_bmt.id == BaseMaterialType.parent_id)).join(BaseMaterialType.base_material_type_attrs).join(BaseMaterialTypeAttr.base_material_type_attr_rules)\
    #         .filter(BaseMaterialType.code == u'88', parent_bmt.code == u'99', BaseMaterialTypeAttr.description==u'测试类attr_name2(mm2)', BaseMaterialTypeAttrValue.description==u'16mm2', BaseMaterialTypeAttrRule.rule_description==u're.I').all()
    #         self.assertEqual(1, len(be))
    #     with get_session() as session:
    #         be = session.query(BaseMaterialType, parent_bmt, BaseMaterialTypeAttr, BaseMaterialTypeAttrRule).join((parent_bmt, parent_bmt.id == BaseMaterialType.parent_id)).join(BaseMaterialType.base_material_type_attrs).join(BaseMaterialTypeAttr.base_material_type_attr_rules)\
    #         .filter(BaseMaterialType.code == u'88', parent_bmt.code == u'99', BaseMaterialTypeAttr.description==u'测试类attr_name1(mm2)', BaseMaterialTypeAttrValue.description==u'15mm2', BaseMaterialTypeAttrRule.rule_description==u'\d+[.]{0,1}\d*[/]{0,1}\d*mm2').all()
    #         self.assertEqual(1, len(be))
    #         be = session.query(BaseMaterialType, parent_bmt, BaseMaterialTypeAttr, BaseMaterialTypeAttrRule).join((parent_bmt, parent_bmt.id == BaseMaterialType.parent_id)).join(BaseMaterialType.base_material_type_attrs).join(BaseMaterialTypeAttr.base_material_type_attr_rules)\
    #         .filter(BaseMaterialType.code == u'88', parent_bmt.code == u'99', BaseMaterialTypeAttr.description==u'测试类attr_name1(mm2)', BaseMaterialTypeAttrValue.description==u'15mm2', BaseMaterialTypeAttrRule.rule_description==u're.I').all()
    #         self.assertEqual(1, len(be))

    def test_api_retrieve_template(self):
        data = {
            'templates': ujson.dumps([
                {
                    'first_type_code': '99',
                    'second_type_code': '88',
                    'first_type_name': '测试类lv1',
                    'second_type_name': '测试类lv2',
                    'attr_name': '测试类attr_name3',
                    'attr_val': 'V聚氯乙烯护套',
                },
                {
                    'first_type_code': '99',
                    'second_type_code': '88',
                    'first_type_name': '测试类lv1',
                    'second_type_name': '测试类lv2',
                    'attr_name': '测试类attr_name3',
                    'attr_val': 'JY聚氯乙烯绝缘',
                },
            ])
        }
        requests.post('http://127.0.0.1:9700/v1/template/create', data=data)

    #     # Check result 1.
    #     data = {
    #         'first_type_code': '99',
    #         'second_type_code': '88',
    #         'attr_name': '',
    #         'page': '1',
    #         'page_size': '5'
    #     }
    #     res = requests.get('http://127.0.0.1:9700/v1/template/retrieve', params=data)
    #     actual_result = ujson.loads(res.content)
    #     expect_result = {
    #         u'total': 1,
    #         u'rows': {
    #             u'attr_name': [u'测试类attr_name3']
    #         }
    #     }
    #     self.assertEqual(expect_result, actual_result)

    #     # Check result 2.
    #     data = {
    #         'first_type_code': '99',
    #         'second_type_code': '88',
    #         'attr_name': '测试类attr_name3',
    #         'page': '1',
    #         'page_size': '3'
    #     }
    #     res = requests.get('http://127.0.0.1:9700/v1/template/retrieve', params=data)
    #     actual_result = ujson.loads(res.content)
    #     expect_result = {
    #         u'total': 2,
    #         u'rows': {
    #             u'V聚氯乙烯护套': 1,
    #             u'JY聚氯乙烯绝缘': 2,
    #             u'attr_rule': [
    #                 u'-attr_rule;-all_value;',
    #                 0,
    #                 u'-attr_rule;-key_word;JY_JY聚氯乙烯绝缘;V_V聚氯乙烯护套;',
    #                 0
    #             ]
    #         }
    #     }
    #     self.assertEqual(expect_result, actual_result)

    #     # Check result 3.
    #     data = {
    #         'first_type_code': '99',
    #         'second_type_code': '88',
    #         'attr_name': '测试类attr_name3',
    #         'page': '3',
    #         'page_size': '3'
    #     }
    #     res = requests.get('http://127.0.0.1:9700/v1/template/retrieve', params=data)
    #     actual_result = ujson.loads(res.content)
    #     expect_result = {
    #         u'total': 2,
    #         u'rows': {
    #             u'attr_rule': [
    #                 u'-attr_rule;-all_value;',
    #                 0,
    #                 u'-attr_rule;-key_word;JY_JY聚氯乙烯绝缘;V_V聚氯乙烯护套;',
    #                 0
    #             ]
    #         }
    #     }
    #     self.assertEqual(expect_result, actual_result)

    # def test_api_update_template(self):
    #     data = {
    #         'templates': ujson.dumps([
    #             {
    #                 'first_type_code': '99',
    #                 'second_type_code': '88',
    #                 'first_type_name': '测试类lv1',
    #                 'second_type_name': '测试类lv2',
    #                 'attr_name': '测试类attr_name1(mm2)',
    #                 'attr_val': '15mm2',
    #             },
    #             {
    #                 'first_type_code': '99',
    #                 'second_type_code': '88',
    #                 'first_type_name': '测试类lv1',
    #                 'second_type_name': '测试类lv2',
    #                 'attr_name': '测试类attr_name3',
    #                 'attr_val': 'JY聚氯乙烯绝缘',
    #             },
    #         ])
    #     }
    #     requests.post('http://127.0.0.1:9700/v1/template/create', data=data)

    #     parent_bmt = aliased(BaseMaterialType)
    #     data = {
    #         'unique_id': '',
    #         'first_type_code': '99',
    #         'second_type_code': '88',
    #         'first_type_name': '测试类lv1',
    #         'second_type_name': '测试类lv2',
    #         'attr_name': '测试类attr_name1(mm2)',
    #         'attr_val': '测试类attr_name2(mm2)',
    #     }
    #     requests.post('http://127.0.0.1:9700/v1/template/update', data=data)
    #     with get_session() as session:
    #          be = session.query(BaseMaterialType, parent_bmt, BaseMaterialTypeAttr).join((parent_bmt, parent_bmt.id == BaseMaterialType.parent_id)).join(BaseMaterialType.base_material_type_attrs)\
    #          .filter(BaseMaterialType.code == u'88', parent_bmt.code == u'99', BaseMaterialTypeAttr.description==u'测试类attr_name2(mm2)').all()
    #          self.assertEqual(1, len(be))

    #     data = {
    #         'unique_id': '1',
    #         'first_type_code': '99',
    #         'second_type_code': '88',
    #         'first_type_name': '测试类lv1',
    #         'second_type_name': '测试类lv2',
    #         'attr_name': '测试类attr_name1(mm2)',
    #         'attr_val': '18mm2',
    #      }
    #     requests.post('http://127.0.0.1:9700/v1/template/update', data=data)
    #     data = {
    #         'unique_id': '2',
    #         'first_type_code': '99',
    #         'second_type_code': '88',
    #         'first_type_name': '测试类lv1',
    #         'second_type_name': '测试类lv2',
    #         'attr_name': '测试类attr_name3',
    #         'attr_val': 'YJV聚氯乙烯绝缘',
    #     }
    #     requests.post('http://127.0.0.1:9700/v1/template/update', data=data)

    #     # check result.
    #     with get_session() as session:
    #         be = session.query(BaseMaterialType, parent_bmt, BaseMaterialTypeAttr, BaseMaterialTypeAttrValue).join((parent_bmt, parent_bmt.id == BaseMaterialType.parent_id)).join(BaseMaterialType.base_material_type_attrs).join(BaseMaterialTypeAttr.base_material_type_attr_values)\
    #         .filter(BaseMaterialType.code == u'88', parent_bmt.code == u'99', BaseMaterialTypeAttrValue.description==u'18mm2').all()
    #         self.assertEqual(1, len(be))

    #     with get_session() as session:
    #         be = session.query(BaseMaterialType, parent_bmt, BaseMaterialTypeAttr, BaseMaterialTypeAttrValue).join((parent_bmt, parent_bmt.id == BaseMaterialType.parent_id)).join(BaseMaterialType.base_material_type_attrs).join(BaseMaterialTypeAttr.base_material_type_attr_values)\
    #         .filter(BaseMaterialType.code == u'88', parent_bmt.code == u'99', BaseMaterialTypeAttr.description==u'测试类attr_name3', BaseMaterialTypeAttrValue.description==u'YJV聚氯乙烯绝缘').all()
    #         self.assertEqual(1, len(be))

    #     with get_session() as session:
    #         be = session.query(BaseMaterialType, parent_bmt, BaseMaterialTypeAttr).join((parent_bmt, parent_bmt.id == BaseMaterialType.parent_id)).join(BaseMaterialType.base_material_type_attrs)\
    #         .filter(BaseMaterialType.code == u'88', parent_bmt.code == u'99', BaseMaterialTypeAttr.description==u'测试类attr_name2(mm2)').all()
    #         self.assertEqual(True, be[0][2].is_all_match)

    #     with get_session() as session:
    #         be = session.query(BaseMaterialType, parent_bmt, BaseMaterialTypeAttr, BaseMaterialTypeAttrRule).join((parent_bmt, parent_bmt.id == BaseMaterialType.parent_id)).join(BaseMaterialType.base_material_type_attrs).join(BaseMaterialTypeAttr.base_material_type_attr_rules)\
    #         .filter(BaseMaterialType.code == u'88', parent_bmt.code == u'99', BaseMaterialTypeAttr.description==u'测试类attr_name2(mm2)', BaseMaterialTypeAttrRule.rule_description==u'\d+[.]{0,1}\d*[/]{0,1}\d*mm2').all()
    #         self.assertEqual(1, len(be))
    #         be = session.query(BaseMaterialType, parent_bmt, BaseMaterialTypeAttr, BaseMaterialTypeAttrRule).join((parent_bmt, parent_bmt.id == BaseMaterialType.parent_id)).join(BaseMaterialType.base_material_type_attrs).join(BaseMaterialTypeAttr.base_material_type_attr_rules)\
    #         .filter(BaseMaterialType.code == u'88', parent_bmt.code == u'99', BaseMaterialTypeAttr.description==u'测试类attr_name2(mm2)', BaseMaterialTypeAttrRule.rule_description==u're.I').all()
    #         self.assertEqual(1, len(be))

    #     with get_session() as session:
    #         be = session.query(BaseMaterialType, parent_bmt, BaseMaterialTypeAttr, BaseMaterialTypeAttrKeyWord).join((parent_bmt, parent_bmt.id == BaseMaterialType.parent_id)).join(BaseMaterialType.base_material_type_attrs).join(BaseMaterialTypeAttr.base_material_type_attr_key_words)\
    #         .filter(BaseMaterialType.code == u'88', parent_bmt.code == u'99', BaseMaterialTypeAttr.description==u'测试类attr_name3', BaseMaterialTypeAttrKeyWord.key_words==u'YJV_YJV聚氯乙烯绝缘').all()
    #         self.assertEqual(1, len(be))

    # def test_api_delete_template(self):
    #     data = {
    #         'templates': ujson.dumps([
    #             {
    #                 'first_type_code': '99',
    #                 'second_type_code': '88',
    #                 'first_type_name': '测试类lv1',
    #                 'second_type_name': '测试类lv2',
    #                 'attr_name': '测试类attr_name1(mm2)',
    #                 'attr_val': '15mm2',
    #             },
    #             {
    #                 'first_type_code': '99',
    #                 'second_type_code': '88',
    #                 'first_type_name': '测试类lv1',
    #                 'second_type_name': '测试类lv2',
    #                 'attr_name': '测试类attr_name3',
    #                 'attr_val': 'JY聚氯乙烯绝缘',
    #             },
    #         ])
    #     }

    #     requests.post('http://127.0.0.1:9700/v1/template/create', data=data)

    #     # delete attribute name.
    #     data = {
    #         'unique_id': '',
    #         'first_type_code': '99',
    #         'second_type_code': '88',
    #         'attr_name': '测试类attr_name1(mm2)'
    #     }
    #     requests.post('http://127.0.0.1:9700/v1/template/delete', data=data)

    #     # Check
    #     parent_bmt = aliased(BaseMaterialType)
    #     with get_session() as session:
    #         be = session.query(BaseMaterialType, parent_bmt, BaseMaterialTypeAttr, BaseMaterialTypeAttrValue).join((parent_bmt, parent_bmt.id == BaseMaterialType.parent_id)).join(BaseMaterialType.base_material_type_attrs).join(BaseMaterialTypeAttr.base_material_type_attr_values)\
    #         .filter(BaseMaterialType.code == u'88', parent_bmt.code == u'99', BaseMaterialTypeAttr.description==u'测试类attr_name1(mm2)').all()
    #         self.assertEqual(0, len(be))

    #     # delete attribute rule.
    #     data = {
    #         'unique_id': '2',
    #         'first_type_code': '99',
    #         'second_type_code': '88',
    #         'attr_name': '测试类attr_name3'
    #     }
    #     requests.post('http://127.0.0.1:9700/v1/template/delete', data=data)

    #     # Check.
    #     with get_session() as session:
    #         be = session.query(BaseMaterialType, parent_bmt, BaseMaterialTypeAttr).join((parent_bmt, parent_bmt.id == BaseMaterialType.parent_id)).join(BaseMaterialType.base_material_type_attrs)\
    #         .filter(BaseMaterialType.code == u'88', parent_bmt.code == u'99', BaseMaterialTypeAttr.description==u'测试类attr_name1(mm2)', BaseMaterialTypeAttrValue.description==u'JY聚氯乙烯绝缘').all()
    #         self.assertEqual(0, len(be))

    #     # delete attribute rule.
    #     data = {
    #         'unique_id': '2',
    #         'first_type_code': '99',
    #         'second_type_code': '88',
    #         'attr_name': '测试类attr_name3'
    #     }
    ### 
    # def test_api_extract_template(self):
        # data = {
        #     'templates': ujson.dumps([
        #         {
        #             'first_type_code': '99',
        #             'second_type_code': '88',
        #             'first_type_name': '测试类lv1',
        #             'second_type_name': '测试类lv2',
        #             'attr_name': '测试类attr_name1(mm2)',
        #             'attr_val': '15mm2',
        #         },
        #         {
        #             'first_type_code': '99',
        #             'second_type_code': '88',
        #             'first_type_name': '测试类lv1',
        #             'second_type_name': '测试类lv2',
        #             'attr_name': '测试类attr_name3',
        #             'attr_val': 'JY聚氯乙烯绝缘',
        #         },
        #         {
        #             'first_type_code': '99',
        #             'second_type_code': '88',
        #             'first_type_name': '测试类lv1',
        #             'second_type_name': '测试类lv2',
        #             'attr_name': 'assemblyAttrName',
        #             'attr_val': "JYV200|{'聚氯':'J','乙烯':'v','绝缘':'v','额定电压':'200'}",
        #         },
        #     ])
        # }
        # requests.post('http://127.0.0.1:9700/v1/template/create', data=data) ### 向表中插入相应的数据
        # import pdb;pdb.set_trace()
        #-------------------------------------------------------------------------------------
        # # extract info.
        # data = {
        #     'first_type_code': '25',
        #     'second_type_code': '88',
        #     'product_info': '8.7/15kV\tJYV\t一芯  15m㎡\t结构7\tBB'
        # }
        # res = requests.post('http://127.0.0.1:9700/v1/extract', data=data)
        
        # # Check result.
        # actual_result = ujson.loads(res.content)
        # expect_result = {
        #     u'first_type_code': u'25',
        #     u'second_type_code': u'88',
        #     u'product_info': u'8.7/15kV\tJYV\t一芯  15m㎡\t结构7\tBB',
        #     u'result': {}
        # }
        # self.assertEqual(expect_result, actual_result)
        #-------------------------------------------------------------------------------------
        # extract info.
        # data = {
        #     'first_type_code': '99',
        #     'second_type_code': '88',
        #     'product_info': '8.7/15kV\tJYV200\t一芯  15m㎡\t结构7\tBB' ###JYV<->JYV200
        # }
        # res = requests.post('http://127.0.0.1:9700/v1/extract', data=data)
        # import pdb;pdb.set_trace()
        # #-----------------------------------------------------------------------------------------------
        # #(Pdb) actual_result
        # # {u'product_info': u'8.7/15kV\tJYV200\t\u4e00\u82af  15m\u33a1\t\u7ed3\u67847\tBB', u'first_type_code': u'99', u'second_type_code': u'88', u'result': {u'\u6d4b\u8bd5\u7c7battr_name1(mm2)': u'\u805a\u6c2f\u4e59\u70ef(\u6750\u8d28)', u'\u6d4b\u8bd5\u7c7battr_name3': u'200V(\u989d\u5b9a\u7535\u538b)', u'\u65e0\u6cd5\u89e3\u6790\u90e8\u5206': u'8.7/15kV\tV200\t\u4e00\u82af\t\u7ed3\u67847\tBB\t'}}
        # #-----------------------------------------------------------------------------------------------
        # # Check result.
        # actual_result = ujson.loads(res.content)
        # expect_result = {
        #     u'first_type_code': u'99',
        #     u'second_type_code': u'88',
        #     u'product_info': u'8.7/15kV\tJYV\t一芯  15m㎡\t结构7\tBB',
        #     u'result': {
        #         u'测试类attr_name1(mm2)': u'15mm2\t',
        #         u'测试类attr_name3': u'JY聚氯乙烯绝缘',
        #         u'无法解析部分': u'8.7/15kV\tV\t一芯\t结构7\tBB\t',
        #     }
        # }
        # self.assertEqual(expect_result, actual_result)
        # pass

    # def test_api_stat_heart(self):
    #     data = {
    #         'heart_request': 1,
    #     }
    #     res = requests.get('http://127.0.0.1:9700/v1/stat/heart', params=data)
    #     actual_result = ujson.loads(res.content)
    #     expect_result = {
    #         u'heart_response': u'OK',
    #     }
    #     self.assertEqual(expect_result, actual_result)

    # def test_api_stat_query(self):
    #     # initial
    #     template_redis.flushdb()
    #     data = {
    #         'query_msg_count': 1,
    #         'query_extract_rate': 1,
    #         'query_extract_time': 1,
    #     }
    #     res = requests.get('http://127.0.0.1:9700/v1/stat/query', params=data)
    #     actual_result = ujson.loads(res.content)
    #     expect_result = {
    #         u'msg_count': 0,
    #         u'extract_rate': u'0.0%',
    #         u'extract_time': u'0ms',
    #     }
    #     self.assertEqual(expect_result, actual_result)

    #     # record and query.
    #     StatInfoQuerier.store_val(
    #         u'msg_total_time', StatInfoQuerier.get_val(u'msg_total_time')+1000
    #     )
    #     StatInfoQuerier.store_val(
    #         u'msg_count', StatInfoQuerier.get_val(u'msg_count')+20
    #     )
    #     StatInfoQuerier.store_val(
    #         u'msg_total_len', StatInfoQuerier.get_val(u'msg_total_len')+300000
    #     )
    #     StatInfoQuerier.store_val(
    #         u'msg_extract_len', StatInfoQuerier.get_val(u'msg_extract_len')+289000
    #     )
    #     data = {
    #         'query_msg_count': 1,
    #         'query_extract_rate': 1,
    #         'query_extract_time': 1,
    #         'query_msg_count_error1': 2,
    #         'query_msg_count_error2': u'',
    #     }
    #     expect_result1 = {
    #         u'msg_count': 20,
    #         u'extract_rate': u'96.3333333333%',
    #         u'extract_time': u'50ms',
    #     }
    #     res = requests.get('http://127.0.0.1:9700/v1/stat/query', params=data)
    #     actual_result = ujson.loads(res.content)
    #     self.assertEqual(expect_result1, actual_result)

# Run test cases.
if __name__ == '__main__':
    unittest.main()




