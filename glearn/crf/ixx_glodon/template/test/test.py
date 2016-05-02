# coding=utf-8
u"""
Description: Test the main functions of template.
User: Jerry.Fang
Date: 13-12-30
"""
import os, sys
sys.path.append( os.path.join( os.path.abspath(os.path.dirname(__file__)) , '../..'))

import requests
import ujson
import unittest

from template.basic_template_generator import BasicTemplate
from template.basic_template_updater import TemplateUpdater
from model.session import *
from model.basic_element import BasicElement
from model.base_material_type import *
from model.base_material_type_attr import *
from model.base_material_type_attr_value import *
from model.base_material_type_attr_rule import *
from model.base_material_type_attr_key_word import *
from sqlalchemy.orm import aliased

class TestTemplateFunctions(unittest.TestCase):

    def setUp(self):
        # Initial test database.
        self.m_basic_template = BasicTemplate()
        self.m_basic_template.set_primary_path( os.path.join( os.path.abspath(os.path.dirname(__file__)) , 'primary_rule_test.xls') )
        self.m_basic_template.clean_table()

    def test_template_gen_ele_dic(self):
        actual_result = BasicElement()
        base_material_type = BaseMaterialType()
        input_list = [u'99', u'88', u'测试类别1', u'测试类别2', u' 标称截面（m㎡）  ', u'2']
        BasicTemplate.generate_ele_dic(actual_result, input_list, 0)
        expect_result = BasicElement()
        expect_result.lv1_id = u'99'
        expect_result.lv2_id = u'88'
        expect_result.lv1_name = u'测试类别1'
        expect_result.lv2_name = u'测试类别2'
        expect_result.attr_name = u'标称截面(mm2)'
        expect_result.attr_val = u'2mm2'

        self.assertEqual(expect_result.lv1_id, actual_result.lv1_id)
        self.assertEqual(expect_result.lv2_id, actual_result.lv2_id)
        self.assertEqual(expect_result.lv1_name, actual_result.lv1_name)
        self.assertEqual(expect_result.lv2_name, actual_result.lv2_name)
        self.assertEqual(expect_result.attr_name, actual_result.attr_name)
        self.assertEqual(expect_result.attr_val, actual_result.attr_val)

    def test_template_gen_template_by_xls(self):
        self.m_basic_template.generate_basic_template()

        with get_session() as session:
            be_pool = session.query(BaseMaterialType).filter_by(code=25).all()
        self.assertEqual(1, len(be_pool))
        self.assertEqual(2, len(be_pool[0].children))

    def test_template_gen_template_rule(self):
        self.m_basic_template.generate_basic_template()

        # Generate attribute rule.
        actual_template_dic_pool = {}
        actual_template_dic_pool[u'99#88'] = {}
        actual_template_dic_pool[u'99#88'][u'标称截面(mm2)'] = []
        actual_template_dic_pool[u'99#88'][u'标称截面(mm2)'].append(u'2mm2')
        self.m_basic_template.gen_attr_rule_in_template(actual_template_dic_pool[u'99#88'])

        #check result.
        expect_template_dic_pool = {}
        expect_template_dic_pool[u'99#88'] = {}
        expect_template_dic_pool[u'99#88'][u'标称截面(mm2)'] = []
        expect_template_dic_pool[u'99#88'][u'标称截面(mm2)'].append(u'2mm2')
        expect_template_dic_pool[u'99#88'][u'标称截面(mm2)'].append(u'-attr_rule;-all_value;-str_format;\d+[.]{0,1}\d*[/]{0,1}\d*mm2;re.I;')
        self.assertEqual(actual_template_dic_pool, expect_template_dic_pool)

        # Submit attribute rule to database and check result.
        with get_session() as session:
            base_material_type = BaseMaterialType()
            base_material_type.code = u'99'
            base_material_type.description = u'测试类别1'
            base_material_type_attr = BaseMaterialTypeAttr(description=u'标称截面(mm2)')
            base_material_type_attr.base_material_type_attr_values.append(BaseMaterialTypeAttrValue(description=u'2mm2'))
            base_material_type.children.append(BaseMaterialType(code=u'88',description=u'测试类别2',))
            base_material_type.children[0].base_material_type_attrs.append(base_material_type_attr)
            # m_basic_element = BasicElement()
            # m_basic_element.lv1_id = 99
            # m_basic_element.lv2_id = 88
            # m_basic_element.lv1_name = u'测试类别1'
            # m_basic_element.lv2_name = u'测试类别2'
            # m_basic_element.attr_name = u'标称截面(mm2)'
            # m_basic_element.attr_val = u'2mm2'
            # session.add(m_basic_element)
            session.add(base_material_type)
            session.commit()
        self.m_basic_template.submit_all_attr_rule_to_database(actual_template_dic_pool)
        parent_bmt = aliased(BaseMaterialType)
        with get_session() as session:
            be = session.query(BaseMaterialType, parent_bmt).join((parent_bmt, parent_bmt.id == BaseMaterialType.parent_id))\
            .filter(BaseMaterialType.code == u'88', parent_bmt.code == u'99').all()
            self.assertEqual(1, len(be))

            self.assertEqual(1, len(be[0][0].base_material_type_attrs))
            self.assertEqual(2, len(be[0][0].base_material_type_attrs[0].base_material_type_attr_rules))
            self.assertEqual(0, len(be[0][0].base_material_type_attrs[0].base_material_type_attr_key_words))

        # delete attribute rule to database and check result.
        self.m_basic_template.clean_attr_rule_by_class_id(u'99#88')
        with get_session() as session:
            be = session.query(BaseMaterialType, parent_bmt).join((parent_bmt, parent_bmt.id == BaseMaterialType.parent_id))\
            .filter(BaseMaterialType.code == u'88', parent_bmt.code == u'99').all()
            self.assertEqual(0, len(be[0][0].base_material_type_attrs[0].base_material_type_attr_rules))
            self.assertEqual(0, len(be[0][0].base_material_type_attrs[0].base_material_type_attr_key_words))

        # Regenerate all attribute rule and check result.
        self.m_basic_template.gen_attr_rule_in_all_basic_template()
        with get_session() as session:
            be = session.query(BaseMaterialType, parent_bmt).join((parent_bmt, parent_bmt.id == BaseMaterialType.parent_id))\
            .filter(BaseMaterialType.code == u'88', parent_bmt.code == u'99').all()
            self.assertEqual(1, len(be))

        with get_session() as session:
            be = session.query(BaseMaterialType, parent_bmt, BaseMaterialTypeAttr, BaseMaterialTypeAttrRule).join((parent_bmt, parent_bmt.id == BaseMaterialType.parent_id)).join(BaseMaterialType.base_material_type_attrs).join(BaseMaterialTypeAttr.base_material_type_attr_rules)\
            .filter(BaseMaterialType.code == u'88', parent_bmt.code == u'99', BaseMaterialTypeAttrRule.rule_description == u'\d+[.]{0,1}\d*[/]{0,1}\d*mm2').all()
            self.assertEqual(1, len(be))

    def test_template_update_template(self):
        self.m_basic_template.generate_basic_template()
        self.m_basic_template.gen_attr_rule_in_all_basic_template()

        # update template.
        m_template_updater = TemplateUpdater()
        m_template_updater.set_input_file(os.path.join( os.path.abspath(os.path.dirname(__file__)) , u'result_test.xls'))
        m_template_updater.update_templates()

        parent_bmt = aliased(BaseMaterialType)
        ######### Check new element result.
        with get_session() as session:
            be = session.query(BaseMaterialType, parent_bmt, BaseMaterialTypeAttr, BaseMaterialTypeAttrValue).join((parent_bmt, parent_bmt.id == BaseMaterialType.parent_id)).join(BaseMaterialType.base_material_type_attrs).join(BaseMaterialTypeAttr.base_material_type_attr_values)\
            .filter(BaseMaterialType.code == u'11', parent_bmt.code == u'25', BaseMaterialTypeAttr.description==u'标称截面(mm2)', BaseMaterialTypeAttrValue.description==u'25mm2').all()
            self.assertEqual(1, len(be))

        with get_session() as session:
            be = session.query(BaseMaterialType, parent_bmt, BaseMaterialTypeAttr, BaseMaterialTypeAttrValue).join((parent_bmt, parent_bmt.id == BaseMaterialType.parent_id)).join(BaseMaterialType.base_material_type_attrs).join(BaseMaterialTypeAttr.base_material_type_attr_values)\
            .filter(BaseMaterialType.code == u'11', parent_bmt.code == u'25', BaseMaterialTypeAttr.description==u'绝缘材料', BaseMaterialTypeAttrValue.description==u'YJ交联聚乙烯绝缘').all()           
            self.assertEqual(1, len(be))

        with get_session() as session:
            be = session.query(BaseMaterialType, parent_bmt, BaseMaterialTypeAttr, BaseMaterialTypeAttrValue).join((parent_bmt, parent_bmt.id == BaseMaterialType.parent_id)).join(BaseMaterialType.base_material_type_attrs).join(BaseMaterialTypeAttr.base_material_type_attr_values)\
            .filter(BaseMaterialType.code == u'11', parent_bmt.code == u'25', BaseMaterialTypeAttr.description==u'内护层材料', BaseMaterialTypeAttrValue.description==u'V聚氯乙烯护套').all()
            self.assertEqual(1, len(be))

        with get_session() as session:
            be = session.query(BaseMaterialType, parent_bmt, BaseMaterialTypeAttr, BaseMaterialTypeAttrValue).join((parent_bmt, parent_bmt.id == BaseMaterialType.parent_id)).join(BaseMaterialType.base_material_type_attrs).join(BaseMaterialTypeAttr.base_material_type_attr_values)\
            .filter(BaseMaterialType.code == u'11', parent_bmt.code == u'25', BaseMaterialTypeAttr.description==u'额定电压(KV)', BaseMaterialTypeAttrValue.description==u'8.7/15kV').all()
            self.assertEqual(1, len(be))

        with get_session() as session:
            be = session.query(BaseMaterialType, parent_bmt, BaseMaterialTypeAttr, BaseMaterialTypeAttrValue).join((parent_bmt, parent_bmt.id == BaseMaterialType.parent_id)).join(BaseMaterialType.base_material_type_attrs).join(BaseMaterialTypeAttr.base_material_type_attr_values)\
            .filter(BaseMaterialType.code == u'11', parent_bmt.code == u'25', BaseMaterialTypeAttr.description==u'芯数', BaseMaterialTypeAttrValue.description==u'一芯').all()
            self.assertEqual(1, len(be))

        with get_session() as session:
            be = session.query(BaseMaterialType, parent_bmt, BaseMaterialTypeAttr, BaseMaterialTypeAttrValue).join((parent_bmt, parent_bmt.id == BaseMaterialType.parent_id)).join(BaseMaterialType.base_material_type_attrs).join(BaseMaterialTypeAttr.base_material_type_attr_values)\
            .filter(BaseMaterialType.code == u'03', parent_bmt.code == u'25', BaseMaterialTypeAttr.description==u'绝缘材料', BaseMaterialTypeAttrValue.description==u'B棉纱编制绝缘').all()
            self.assertEqual(1, len(be))

        with get_session() as session:
            be = session.query(BaseMaterialType, parent_bmt, BaseMaterialTypeAttr, BaseMaterialTypeAttrValue).join((parent_bmt, parent_bmt.id == BaseMaterialType.parent_id)).join(BaseMaterialType.base_material_type_attrs).join(BaseMaterialTypeAttr.base_material_type_attr_values)\
            .filter(BaseMaterialType.code == u'03', parent_bmt.code == u'25', BaseMaterialTypeAttr.description==u'护套材料', BaseMaterialTypeAttrValue.description==u'V聚氯乙稀护套').all()
            self.assertEqual(1, len(be))

        with get_session() as session:
            be = session.query(BaseMaterialType, parent_bmt, BaseMaterialTypeAttr, BaseMaterialTypeAttrValue).join((parent_bmt, parent_bmt.id == BaseMaterialType.parent_id)).join(BaseMaterialType.base_material_type_attrs).join(BaseMaterialTypeAttr.base_material_type_attr_values)\
            .filter(BaseMaterialType.code == u'03', parent_bmt.code == u'25', BaseMaterialTypeAttr.description==u'标称截面(mm2)', BaseMaterialTypeAttrValue.description==u'120mm2').all()
            self.assertEqual(1, len(be))

        with get_session() as session:
            be = session.query(BaseMaterialType, parent_bmt, BaseMaterialTypeAttr, BaseMaterialTypeAttrValue).join((parent_bmt, parent_bmt.id == BaseMaterialType.parent_id)).join(BaseMaterialType.base_material_type_attrs).join(BaseMaterialTypeAttr.base_material_type_attr_values)\
            .filter(BaseMaterialType.code == u'03', parent_bmt.code == u'25', BaseMaterialTypeAttr.description==u'额定电压(KV)', BaseMaterialTypeAttrValue.description==u'450/750V').all()
            self.assertEqual(1, len(be))

        ########## Check new attribute rule result.
        with get_session() as session:
            be = session.query(BaseMaterialType, parent_bmt, BaseMaterialTypeAttr).join((parent_bmt, parent_bmt.id == BaseMaterialType.parent_id)).join(BaseMaterialType.base_material_type_attrs)\
            .filter(BaseMaterialType.code == u'11', BaseMaterialTypeAttr.is_all_match == True, parent_bmt.code == u'25', BaseMaterialTypeAttr.description==u'标称截面(mm2)').all()
            self.assertEqual(1, len(be))

        with get_session() as session:
             be = session.query(BaseMaterialType, parent_bmt, BaseMaterialTypeAttr, BaseMaterialTypeAttrRule).join((parent_bmt, parent_bmt.id == BaseMaterialType.parent_id)).join(BaseMaterialType.base_material_type_attrs).join(BaseMaterialTypeAttr.base_material_type_attr_rules)\
             .filter(BaseMaterialType.code == u'11', parent_bmt.code == u'25', BaseMaterialTypeAttr.description==u'标称截面(mm2)', BaseMaterialTypeAttrRule.rule_description==u'\d+[.]{0,1}\d*[/]{0,1}\d*mm2').all()
             self.assertEqual(1, len(be))
             be = session.query(BaseMaterialType, parent_bmt, BaseMaterialTypeAttr, BaseMaterialTypeAttrRule).join((parent_bmt, parent_bmt.id == BaseMaterialType.parent_id)).join(BaseMaterialType.base_material_type_attrs).join(BaseMaterialTypeAttr.base_material_type_attr_rules)\
             .filter(BaseMaterialType.code == u'11', parent_bmt.code == u'25', BaseMaterialTypeAttr.description==u'标称截面(mm2)', BaseMaterialTypeAttrRule.rule_description==u're.I').all()
             self.assertEqual(1, len(be))

        with get_session() as session:
            be = session.query(BaseMaterialType, parent_bmt, BaseMaterialTypeAttr).join((parent_bmt, parent_bmt.id == BaseMaterialType.parent_id)).join(BaseMaterialType.base_material_type_attrs)\
            .filter(BaseMaterialType.code == u'11', BaseMaterialTypeAttr.is_all_match == True, parent_bmt.code == u'25', BaseMaterialTypeAttr.description==u'绝缘材料').all()
            self.assertEqual(1, len(be))

        with get_session() as session:
            be = session.query(BaseMaterialType, parent_bmt, BaseMaterialTypeAttr, BaseMaterialTypeAttrKeyWord).join((parent_bmt, parent_bmt.id == BaseMaterialType.parent_id)).join(BaseMaterialType.base_material_type_attrs).join(BaseMaterialTypeAttr.base_material_type_attr_key_words)\
            .filter(BaseMaterialType.code == u'11', parent_bmt.code == u'25', BaseMaterialTypeAttr.description==u'绝缘材料', BaseMaterialTypeAttrKeyWord.key_words==u'HE_HE乙丙橡胶绝缘').all()
            self.assertEqual(1, len(be))
            be = session.query(BaseMaterialType, parent_bmt, BaseMaterialTypeAttr, BaseMaterialTypeAttrKeyWord).join((parent_bmt, parent_bmt.id == BaseMaterialType.parent_id)).join(BaseMaterialType.base_material_type_attrs).join(BaseMaterialTypeAttr.base_material_type_attr_key_words)\
            .filter(BaseMaterialType.code == u'11', parent_bmt.code == u'25', BaseMaterialTypeAttr.description==u'绝缘材料', BaseMaterialTypeAttrKeyWord.key_words==u'YJ_YJ交联聚乙烯绝缘').all()
            self.assertEqual(1, len(be))

        with get_session() as session:
            be = session.query(BaseMaterialType, parent_bmt, BaseMaterialTypeAttr).join((parent_bmt, parent_bmt.id == BaseMaterialType.parent_id)).join(BaseMaterialType.base_material_type_attrs)\
            .filter(BaseMaterialType.code == u'11', BaseMaterialTypeAttr.is_all_match == True, parent_bmt.code == u'25', BaseMaterialTypeAttr.description==u'内护层材料').all()
            self.assertEqual(1, len(be))

        with get_session() as session:
            be = session.query(BaseMaterialType, parent_bmt, BaseMaterialTypeAttr, BaseMaterialTypeAttrKeyWord).join((parent_bmt, parent_bmt.id == BaseMaterialType.parent_id)).join(BaseMaterialType.base_material_type_attrs).join(BaseMaterialTypeAttr.base_material_type_attr_key_words)\
            .filter(BaseMaterialType.code == u'11', parent_bmt.code == u'25', BaseMaterialTypeAttr.description==u'内护层材料', BaseMaterialTypeAttrKeyWord.key_words==u'V_V聚氯乙烯护套').all()
            self.assertEqual(1, len(be))

        with get_session() as session:
            be = session.query(BaseMaterialType, parent_bmt, BaseMaterialTypeAttr).join((parent_bmt, parent_bmt.id == BaseMaterialType.parent_id)).join(BaseMaterialType.base_material_type_attrs)\
            .filter(BaseMaterialType.code == u'11', BaseMaterialTypeAttr.is_all_match == True, parent_bmt.code == u'25', BaseMaterialTypeAttr.description==u'额定电压(KV)').all()
            self.assertEqual(1, len(be))

        with get_session() as session:
            be = session.query(BaseMaterialType, parent_bmt, BaseMaterialTypeAttr, BaseMaterialTypeAttrRule).join((parent_bmt, parent_bmt.id == BaseMaterialType.parent_id)).join(BaseMaterialType.base_material_type_attrs).join(BaseMaterialTypeAttr.base_material_type_attr_rules)\
            .filter(BaseMaterialType.code == u'11', parent_bmt.code == u'25', BaseMaterialTypeAttr.description==u'额定电压(KV)', BaseMaterialTypeAttrRule.rule_description==u'\d+[.]{0,1}\d*[/]{0,1}\d*KV').all()
            self.assertEqual(1, len(be))
            be = session.query(BaseMaterialType, parent_bmt, BaseMaterialTypeAttr, BaseMaterialTypeAttrRule).join((parent_bmt, parent_bmt.id == BaseMaterialType.parent_id)).join(BaseMaterialType.base_material_type_attrs).join(BaseMaterialTypeAttr.base_material_type_attr_rules)\
            .filter(BaseMaterialType.code == u'11', parent_bmt.code == u'25', BaseMaterialTypeAttr.description==u'额定电压(KV)', BaseMaterialTypeAttrRule.rule_description==u're.I').all()
            self.assertEqual(2, len(be))
            be = session.query(BaseMaterialType, parent_bmt, BaseMaterialTypeAttr, BaseMaterialTypeAttrRule).join((parent_bmt, parent_bmt.id == BaseMaterialType.parent_id)).join(BaseMaterialType.base_material_type_attrs).join(BaseMaterialTypeAttr.base_material_type_attr_rules)\
            .filter(BaseMaterialType.code == u'11', parent_bmt.code == u'25', BaseMaterialTypeAttr.description==u'额定电压(KV)', BaseMaterialTypeAttrRule.rule_description==u'\d+[/]{1}\d+V').all()
            self.assertEqual(1, len(be))

        with get_session() as session:
            be = session.query(BaseMaterialType, parent_bmt, BaseMaterialTypeAttr).join((parent_bmt, parent_bmt.id == BaseMaterialType.parent_id)).join(BaseMaterialType.base_material_type_attrs)\
            .filter(BaseMaterialType.code == u'11', BaseMaterialTypeAttr.is_all_match == True, parent_bmt.code == u'25', BaseMaterialTypeAttr.description==u'芯数').all()
            self.assertEqual(1, len(be))

        with get_session() as session:
            be = session.query(BaseMaterialType, parent_bmt, BaseMaterialTypeAttr, BaseMaterialTypeAttrRule).join((parent_bmt, parent_bmt.id == BaseMaterialType.parent_id)).join(BaseMaterialType.base_material_type_attrs).join(BaseMaterialTypeAttr.base_material_type_attr_rules)\
            .filter(BaseMaterialType.code == u'11', parent_bmt.code == u'25', BaseMaterialTypeAttr.description==u'芯数', BaseMaterialTypeAttrRule.rule_description==u'.+芯[加]{0,1}[大]{0,1}[地]{0,1}[线]{0,1}').all()
            self.assertEqual(1, len(be))

        with get_session() as session:
            be = session.query(BaseMaterialType, parent_bmt, BaseMaterialTypeAttr).join((parent_bmt, parent_bmt.id == BaseMaterialType.parent_id)).join(BaseMaterialType.base_material_type_attrs)\
            .filter(BaseMaterialType.code == u'03', BaseMaterialTypeAttr.is_all_match == True, parent_bmt.code == u'25', BaseMaterialTypeAttr.description==u'绝缘材料').all()
            self.assertEqual(1, len(be))

        with get_session() as session:
            be = session.query(BaseMaterialType, parent_bmt, BaseMaterialTypeAttr, BaseMaterialTypeAttrKeyWord).join((parent_bmt, parent_bmt.id == BaseMaterialType.parent_id)).join(BaseMaterialType.base_material_type_attrs).join(BaseMaterialTypeAttr.base_material_type_attr_key_words)\
            .filter(BaseMaterialType.code == u'03', parent_bmt.code == u'25', BaseMaterialTypeAttr.description==u'绝缘材料', BaseMaterialTypeAttrKeyWord.key_words==u'B_B棉纱编制绝缘').all()
            self.assertEqual(1, len(be))

        with get_session() as session:
            be = session.query(BaseMaterialType, parent_bmt, BaseMaterialTypeAttr).join((parent_bmt, parent_bmt.id == BaseMaterialType.parent_id)).join(BaseMaterialType.base_material_type_attrs)\
            .filter(BaseMaterialType.code == u'03', BaseMaterialTypeAttr.is_all_match == True, parent_bmt.code == u'25', BaseMaterialTypeAttr.description==u'护套材料').all()
            self.assertEqual(1, len(be))

        with get_session() as session:
            be = session.query(BaseMaterialType, parent_bmt, BaseMaterialTypeAttr, BaseMaterialTypeAttrKeyWord).join((parent_bmt, parent_bmt.id == BaseMaterialType.parent_id)).join(BaseMaterialType.base_material_type_attrs).join(BaseMaterialTypeAttr.base_material_type_attr_key_words)\
            .filter(BaseMaterialType.code == u'03', parent_bmt.code == u'25', BaseMaterialTypeAttr.description==u'护套材料', BaseMaterialTypeAttrKeyWord.key_words==u'V22_V22钢带铠装聚氯乙稀护套').all()
            self.assertEqual(1, len(be))
            be = session.query(BaseMaterialType, parent_bmt, BaseMaterialTypeAttr, BaseMaterialTypeAttrKeyWord).join((parent_bmt, parent_bmt.id == BaseMaterialType.parent_id)).join(BaseMaterialType.base_material_type_attrs).join(BaseMaterialTypeAttr.base_material_type_attr_key_words)\
            .filter(BaseMaterialType.code == u'03', parent_bmt.code == u'25', BaseMaterialTypeAttr.description==u'护套材料', BaseMaterialTypeAttrKeyWord.key_words==u'Y_Y聚乙烯护套').all()
            self.assertEqual(1, len(be))
            be = session.query(BaseMaterialType, parent_bmt, BaseMaterialTypeAttr, BaseMaterialTypeAttrKeyWord).join((parent_bmt, parent_bmt.id == BaseMaterialType.parent_id)).join(BaseMaterialType.base_material_type_attrs).join(BaseMaterialTypeAttr.base_material_type_attr_key_words)\
            .filter(BaseMaterialType.code == u'11', parent_bmt.code == u'25', BaseMaterialTypeAttr.description==u'内护层材料', BaseMaterialTypeAttrKeyWord.key_words==u'V_V聚氯乙烯护套').all()
            self.assertEqual(1, len(be))

        with get_session() as session:
            be = session.query(BaseMaterialType, parent_bmt, BaseMaterialTypeAttr).join((parent_bmt, parent_bmt.id == BaseMaterialType.parent_id)).join(BaseMaterialType.base_material_type_attrs)\
            .filter(BaseMaterialType.code == u'03', BaseMaterialTypeAttr.is_all_match == True, parent_bmt.code == u'25', BaseMaterialTypeAttr.description==u'标称截面(mm2)').all()
            self.assertEqual(1, len(be))

        with get_session() as session:
            be = session.query(BaseMaterialType, parent_bmt, BaseMaterialTypeAttr, BaseMaterialTypeAttrRule).join((parent_bmt, parent_bmt.id == BaseMaterialType.parent_id)).join(BaseMaterialType.base_material_type_attrs).join(BaseMaterialTypeAttr.base_material_type_attr_rules)\
            .filter(BaseMaterialType.code == u'03', parent_bmt.code == u'25', BaseMaterialTypeAttr.description==u'标称截面(mm2)', BaseMaterialTypeAttrRule.rule_description==u'\d+[.]{0,1}\d*[/]{0,1}\d*mm2').all()
            self.assertEqual(1, len(be))
            be = session.query(BaseMaterialType, parent_bmt, BaseMaterialTypeAttr, BaseMaterialTypeAttrRule).join((parent_bmt, parent_bmt.id == BaseMaterialType.parent_id)).join(BaseMaterialType.base_material_type_attrs).join(BaseMaterialTypeAttr.base_material_type_attr_rules)\
            .filter(BaseMaterialType.code == u'03', parent_bmt.code == u'25', BaseMaterialTypeAttr.description==u'标称截面(mm2)', BaseMaterialTypeAttrRule.rule_description==u're.I').all()
            self.assertEqual(1, len(be))

        with get_session() as session:
            be = session.query(BaseMaterialType, parent_bmt, BaseMaterialTypeAttr).join((parent_bmt, parent_bmt.id == BaseMaterialType.parent_id)).join(BaseMaterialType.base_material_type_attrs)\
            .filter(BaseMaterialType.code == u'03', BaseMaterialTypeAttr.is_all_match == True, parent_bmt.code == u'25', BaseMaterialTypeAttr.description==u'额定电压(KV)').all()
            self.assertEqual(1, len(be))

        with get_session() as session:
            be = session.query(BaseMaterialType, parent_bmt, BaseMaterialTypeAttr, BaseMaterialTypeAttrRule).join((parent_bmt, parent_bmt.id == BaseMaterialType.parent_id)).join(BaseMaterialType.base_material_type_attrs).join(BaseMaterialTypeAttr.base_material_type_attr_rules)\
            .filter(BaseMaterialType.code == u'03', parent_bmt.code == u'25', BaseMaterialTypeAttr.description==u'额定电压(KV)', BaseMaterialTypeAttrRule.rule_description==u'\d+[.]{0,1}\d*[/]{0,1}\d*KV').all()
            self.assertEqual(1, len(be))
            be = session.query(BaseMaterialType, parent_bmt, BaseMaterialTypeAttr, BaseMaterialTypeAttrRule).join((parent_bmt, parent_bmt.id == BaseMaterialType.parent_id)).join(BaseMaterialType.base_material_type_attrs).join(BaseMaterialTypeAttr.base_material_type_attr_rules)\
            .filter(BaseMaterialType.code == u'03', parent_bmt.code == u'25', BaseMaterialTypeAttr.description==u'额定电压(KV)', BaseMaterialTypeAttrRule.rule_description==u're.I').all()
            self.assertEqual(2, len(be))
            be = session.query(BaseMaterialType, parent_bmt, BaseMaterialTypeAttr, BaseMaterialTypeAttrRule).join((parent_bmt, parent_bmt.id == BaseMaterialType.parent_id)).join(BaseMaterialType.base_material_type_attrs).join(BaseMaterialTypeAttr.base_material_type_attr_rules)\
            .filter(BaseMaterialType.code == u'03', parent_bmt.code == u'25', BaseMaterialTypeAttr.description==u'额定电压(KV)', BaseMaterialTypeAttrRule.rule_description==u'\d+[/]{1}\d+V').all()
            self.assertEqual(1, len(be))

    def test_xxxxx(self):
        templates = ujson.dumps([
            {
                'first_type_code': '99',
                'second_type_code': '88',
                'first_type_name': '测试类lv1',
                'second_type_name': '测试类lv2',
                'attr_name': '测试类attr_name1(mm2)',
                'attr_val': '15mm2',
            },
            {
                'first_type_code': '99',
                'second_type_code': '88',
                'first_type_name': '测试类lv1',
                'second_type_name': '测试类lv2',
                'attr_name': '测试类attr_name2(mm2)',
                'attr_val': '16',
            },
        ])
        template_list = ujson.loads(templates)
        BasicTemplate.check_new_template_ind_list(template_list)
        BasicTemplate.create_new_template_by_ind_list(template_list)

    def test_retrieve_template_attr_by_api_ind(self):
        self.m_basic_template.generate_basic_template()
        self.m_basic_template.gen_attr_rule_in_all_basic_template()
        ind_info = {}
        ind_info[u'first_type_code'] = u'25'
        ind_info[u'second_type_code'] = u'11'
        ind_info[u'page'] = 1
        ind_info[u'page_size'] = 5
        result = TemplateUpdater.retrieve_template_attr_by_api_ind(ind_info)
        expect_result = {
           u'total': 13,
           u'rows':[{u'id': 8, u'attr_name': u'内护层材料'},
                   {u'id': 9, u'attr_name': u'品种'},
                   {u'id': 10, u'attr_name': u'工作温度'},
                   {u'id': 11, u'attr_name': u'工作类型'},
                   {u'id': 12, u'attr_name': u'护套材料'}]
        }
        self.assertEqual(expect_result, result)
        ind_info[u'page'] = 2
        result_2 = TemplateUpdater.retrieve_template_attr_by_api_ind(ind_info)
        expect_result_2 = {
           u'total': 13,
           u'rows':[{u'id': 13, u'attr_name': u'标称截面(mm2)'},
                   {u'id': 14, u'attr_name': u'标称直径(mm)'},
                   {u'id': 15, u'attr_name': u'电线特征'},
                   {u'id': 16, u'attr_name': u'线芯材质'},
                   {u'id': 17, u'attr_name': u'绝缘材料'}]
        }
        self.assertEqual(expect_result_2, result_2)

    def test_retrieve_template_attr_value_by_api_ind(self):
        self.m_basic_template.generate_basic_template()
        self.m_basic_template.gen_attr_rule_in_all_basic_template()
        ind_info = {}
        ind_info[u'base_material_type_attr_id'] = 9
        ind_info[u'page'] = 1
        ind_info[u'page_size'] = 1
        result = TemplateUpdater.retrieve_template_attr_value_by_api_ind(ind_info)
        expect_result = {
           u'total': 2,
           u'rows':[{u'id': 12, u'attr_value': u'橡皮绝缘电力电缆'}]
        }
        self.assertEqual(expect_result, result)
        ind_info[u'page'] = 2
        result = TemplateUpdater.retrieve_template_attr_value_by_api_ind(ind_info)
        expect_result = {
           u'total': 2,
           u'rows':[{u'id': 13, u'attr_value': u'塑料绝缘电力电缆'}]
        }
        self.assertEqual(expect_result, result)

    def test_retrieve_template_attr_rule_by_api_ind(self):
        self.m_basic_template.generate_basic_template()
        self.m_basic_template.gen_attr_rule_in_all_basic_template()
        ind_info = {}
        ind_info[u'base_material_type_attr_id'] = 10
        ind_info[u'page'] = 1
        ind_info[u'page_size'] = 1
        result = TemplateUpdater.retrieve_template_attr_rule_by_api_ind(ind_info)
        expect_result = {
           u'total': 1,
           u'rows':[{u'id': 1, u'attr_rule': u'\d+[.]{0,1}\d*℃'}]
        }
        self.assertEqual(expect_result, result)
        ind_info[u'base_material_type_attr_id'] = 20
        ind_info[u'page_size'] = 10
        result = TemplateUpdater.retrieve_template_attr_rule_by_api_ind(ind_info)
        expect_result = {
           u'total': 4,
           u'rows':[{u'id': 5, u'attr_rule': u'\d+[.]{0,1}\d*[/]{0,1}\d*KV'},
                   {u'id': 6, u'attr_rule': u're.I'},
                   {u'id': 7, u'attr_rule': u'\d+[/]{1}\d+V'},
                   {u'id': 8, u'attr_rule': u're.I'}]
        }
        self.assertEqual(expect_result, result)

    def test_retrieve_template_attr_key_word_by_api_ind(self):
        self.m_basic_template.generate_basic_template()
        self.m_basic_template.gen_attr_rule_in_all_basic_template()
        ind_info = {}
        ind_info[u'base_material_type_attr_id'] = 8
        ind_info[u'page'] = 1
        ind_info[u'page_size'] = 1
        result = TemplateUpdater.retrieve_template_attr_key_word_by_api_ind(ind_info)
        expect_result = {
           u'total': 1,
           u'rows':[{u'id': 5, u'key_word': u'V_V聚氯乙烯护套'}]
        }
        self.assertEqual(expect_result, result)
        ind_info[u'base_material_type_attr_id'] = 11
        ind_info[u'page_size'] = 10
        result = TemplateUpdater.retrieve_template_attr_key_word_by_api_ind(ind_info)
        expect_result = {
           u'total': 1,
           u'rows':[{u'id': 2, u'key_word': u'WL_WL无卤低烟'}]
        }
        self.assertEqual(expect_result, result)

    def test_del_template_attr(self):
        self.m_basic_template.generate_basic_template()
        self.m_basic_template.gen_attr_rule_in_all_basic_template()
        ind_info = {}
        ind_info[u'base_material_type_attr_id'] = 8
        result = TemplateUpdater.del_template_attr(ind_info)
        parent_bmt = aliased(BaseMaterialType)
        with get_session() as session:
           be = session.query(BaseMaterialType, parent_bmt, BaseMaterialTypeAttr).join((parent_bmt, parent_bmt.id == BaseMaterialType.parent_id)).join(BaseMaterialType.base_material_type_attrs)\
           .filter(BaseMaterialType.code == u'11', parent_bmt.code == u'25', BaseMaterialTypeAttr.description==u'内护层材料').all()
           self.assertEqual(0, len(be))
           be = session.query(BaseMaterialType, parent_bmt, BaseMaterialTypeAttr, BaseMaterialTypeAttrValue).join((parent_bmt, parent_bmt.id == BaseMaterialType.parent_id)).join(BaseMaterialType.base_material_type_attrs).join(BaseMaterialTypeAttr.base_material_type_attr_values)\
           .filter(BaseMaterialType.code == u'11', parent_bmt.code == u'25', BaseMaterialTypeAttr.description==u'内护层材料').all()
           self.assertEqual(0, len(be))
           be = session.query(BaseMaterialType, parent_bmt, BaseMaterialTypeAttr, BaseMaterialTypeAttrKeyWord).join((parent_bmt, parent_bmt.id == BaseMaterialType.parent_id)).join(BaseMaterialType.base_material_type_attrs).join(BaseMaterialTypeAttr.base_material_type_attr_key_words)\
           .filter(BaseMaterialType.code == u'11', parent_bmt.code == u'25', BaseMaterialTypeAttr.description==u'内护层材料').all()
           self.assertEqual(0, len(be))
           be = session.query(BaseMaterialType, parent_bmt, BaseMaterialTypeAttr, BaseMaterialTypeAttrRule).join((parent_bmt, parent_bmt.id == BaseMaterialType.parent_id)).join(BaseMaterialType.base_material_type_attrs).join(BaseMaterialTypeAttr.base_material_type_attr_rules)\
           .filter(BaseMaterialType.code == u'11', parent_bmt.code == u'25', BaseMaterialTypeAttr.description==u'内护层材料').all()
           self.assertEqual(0, len(be))

    def test_del_template_attr_value(self):
        self.m_basic_template.generate_basic_template()
        self.m_basic_template.gen_attr_rule_in_all_basic_template()
        ind_info = {}
        ind_info[u'base_material_type_attr_value_id'] = 11
        result = TemplateUpdater.del_template_attr_value(ind_info)
        parent_bmt = aliased(BaseMaterialType)
        with get_session() as session:
             be = session.query(BaseMaterialType, parent_bmt, BaseMaterialTypeAttr, BaseMaterialTypeAttrValue).join((parent_bmt, parent_bmt.id == BaseMaterialType.parent_id)).join(BaseMaterialType.base_material_type_attrs).join(BaseMaterialTypeAttr.base_material_type_attr_values)\
             .filter(BaseMaterialType.code == u'11', parent_bmt.code == u'25', BaseMaterialTypeAttr.description==u'内护层材料', BaseMaterialTypeAttrValue.description==u'V聚氯乙烯护套').all()
             self.assertEqual(0, len(be))

    def test_del_template_attr_rule(self):
        self.m_basic_template.generate_basic_template()
        self.m_basic_template.gen_attr_rule_in_all_basic_template()
        ind_info = {}
        ind_info[u'base_material_type_attr_rule_id'] = 5
        result = TemplateUpdater.del_template_attr_rule(ind_info)
        parent_bmt = aliased(BaseMaterialType)
        with get_session() as session:
             be = session.query(BaseMaterialType, parent_bmt, BaseMaterialTypeAttr, BaseMaterialTypeAttrRule).join((parent_bmt, parent_bmt.id == BaseMaterialType.parent_id)).join(BaseMaterialType.base_material_type_attrs).join(BaseMaterialTypeAttr.base_material_type_attr_rules)\
             .filter(BaseMaterialType.code == u'11', parent_bmt.code == u'25', BaseMaterialTypeAttr.description==u'内护层材料', BaseMaterialTypeAttrRule.rule_description==u'\d+[.]{0,1}\d*[/]{0,1}\d*KV').all()
             self.assertEqual(0, len(be))

    def test_del_template_attr_key_word(self):
        self.m_basic_template.generate_basic_template()
        self.m_basic_template.gen_attr_rule_in_all_basic_template()
        ind_info = {}
        ind_info[u'base_material_type_attr_key_word_id'] = 5
        result = TemplateUpdater.del_template_attr_key_word(ind_info)
        parent_bmt = aliased(BaseMaterialType)
        with get_session() as session:
             be = session.query(BaseMaterialType, parent_bmt, BaseMaterialTypeAttr, BaseMaterialTypeAttrKeyWord).join((parent_bmt, parent_bmt.id == BaseMaterialType.parent_id)).join(BaseMaterialType.base_material_type_attrs).join(BaseMaterialTypeAttr.base_material_type_attr_values)\
             .filter(BaseMaterialType.code == u'11', parent_bmt.code == u'25', BaseMaterialTypeAttr.description==u'内护层材料', BaseMaterialTypeAttrKeyWord.key_words==u'V_V聚氯乙烯护套').all()
             self.assertEqual(0, len(be))

    def test_update_template_attr(self):
        self.m_basic_template.generate_basic_template()
        self.m_basic_template.gen_attr_rule_in_all_basic_template()
        ind_info = {}
        ind_info[u'base_material_type_attr_id'] = 8
        ind_info[u'description'] = u'内护层材料_修改'
        result = TemplateUpdater.update_template_attr(ind_info)
        parent_bmt = aliased(BaseMaterialType)
        with get_session() as session:
             be = session.query(BaseMaterialType, parent_bmt, BaseMaterialTypeAttr).join((parent_bmt, parent_bmt.id == BaseMaterialType.parent_id)).join(BaseMaterialType.base_material_type_attrs)\
             .filter(BaseMaterialType.code == u'11', parent_bmt.code == u'25', BaseMaterialTypeAttr.description==u'内护层材料_修改').all()
             self.assertEqual(1, len(be))

    def test_update_template_attr_value(self):
        self.m_basic_template.generate_basic_template()
        self.m_basic_template.gen_attr_rule_in_all_basic_template()
        ind_info = {}
        ind_info[u'base_material_type_attr_value_id'] = 11
        ind_info[u'description'] = u'V聚氯乙烯护套_修改'
        result = TemplateUpdater.update_template_attr_value(ind_info)
        parent_bmt = aliased(BaseMaterialType)
        with get_session() as session:
             be = session.query(BaseMaterialType, parent_bmt, BaseMaterialTypeAttr, BaseMaterialTypeAttrValue).join((parent_bmt, parent_bmt.id == BaseMaterialType.parent_id)).join(BaseMaterialType.base_material_type_attrs).join(BaseMaterialTypeAttr.base_material_type_attr_values)\
             .filter(BaseMaterialType.code == u'11', parent_bmt.code == u'25', BaseMaterialTypeAttr.description==u'内护层材料', BaseMaterialTypeAttrValue.description==u'V聚氯乙烯护套_修改').all()
             self.assertEqual(1, len(be))

    def test_update_template_attr_rule(self):
        self.m_basic_template.generate_basic_template()
        self.m_basic_template.gen_attr_rule_in_all_basic_template()
        ind_info = {}
        ind_info[u'base_material_type_attr_rule_id'] = 5
        ind_info[u'rule_description'] = u'\d+[.]{0,1}\d*[/]{0,1}\d*KV_修改'
        result = TemplateUpdater.update_template_attr_rule(ind_info)
        parent_bmt = aliased(BaseMaterialType)
        with get_session() as session:
             be = session.query(BaseMaterialType, parent_bmt, BaseMaterialTypeAttr, BaseMaterialTypeAttrRule).join((parent_bmt, parent_bmt.id == BaseMaterialType.parent_id)).join(BaseMaterialType.base_material_type_attrs).join(BaseMaterialTypeAttr.base_material_type_attr_rules)\
             .filter(BaseMaterialType.code == u'11', parent_bmt.code == u'25', BaseMaterialTypeAttr.description==u'额定电压(KV)', BaseMaterialTypeAttrRule.rule_description==u'\d+[.]{0,1}\d*[/]{0,1}\d*KV_修改').all()
             self.assertEqual(1, len(be))

    def test_update_template_attr_key_word(self):
        self.m_basic_template.generate_basic_template()
        self.m_basic_template.gen_attr_rule_in_all_basic_template()
        ind_info = {}
        ind_info[u'base_material_type_attr_key_word_id'] = 5
        ind_info[u'key_word'] = u'V_V聚氯乙烯护套_修改'
        result = TemplateUpdater.update_template_attr_key_word(ind_info)
        parent_bmt = aliased(BaseMaterialType)
        with get_session() as session:
             be = session.query(BaseMaterialType, parent_bmt, BaseMaterialTypeAttr, BaseMaterialTypeAttrKeyWord).join((parent_bmt, parent_bmt.id == BaseMaterialType.parent_id)).join(BaseMaterialType.base_material_type_attrs).join(BaseMaterialTypeAttr.base_material_type_attr_key_words)\
             .filter(BaseMaterialType.code == u'11', parent_bmt.code == u'25', BaseMaterialTypeAttr.description==u'内护层材料', BaseMaterialTypeAttrKeyWord.key_words==u'V_V聚氯乙烯护套_修改').all()
             self.assertEqual(1, len(be))

    def test_add_template_attr(self):
        self.m_basic_template.generate_basic_template()
        self.m_basic_template.gen_attr_rule_in_all_basic_template()
        ind_info = {}
        ind_info[u'code'] = u'2511'
        ind_info[u'description'] = u'增加属性'
        result = TemplateUpdater.add_template_attr(ind_info)
        parent_bmt = aliased(BaseMaterialType)
        with get_session() as session:
             be = session.query(BaseMaterialType, parent_bmt, BaseMaterialTypeAttr).join((parent_bmt, parent_bmt.id == BaseMaterialType.parent_id)).join(BaseMaterialType.base_material_type_attrs)\
             .filter(BaseMaterialType.code == u'11', parent_bmt.code == u'25', BaseMaterialTypeAttr.description==u'增加属性').all()
             self.assertEqual(1, len(be))
             ind_info[u'base_material_type_attr_id'] = be[0][2].id
             ind_info[u'description'] = u'增加属性值'
             result = TemplateUpdater.add_template_attr_value(ind_info)
             be = session.query(BaseMaterialType, parent_bmt, BaseMaterialTypeAttr, BaseMaterialTypeAttrValue).join((parent_bmt, parent_bmt.id == BaseMaterialType.parent_id)).join(BaseMaterialType.base_material_type_attrs).join(BaseMaterialTypeAttr.base_material_type_attr_values)\
             .filter(BaseMaterialType.code == u'11', parent_bmt.code == u'25', BaseMaterialTypeAttr.description==u'增加属性', BaseMaterialTypeAttrValue.description==u'增加属性值').all()
             self.assertEqual(1, len(be))
             ind_info[u'rule_description'] = u'增加规则'
             result = TemplateUpdater.add_template_attr_rule(ind_info)
             be = session.query(BaseMaterialType, parent_bmt, BaseMaterialTypeAttr, BaseMaterialTypeAttrRule).join((parent_bmt, parent_bmt.id == BaseMaterialType.parent_id)).join(BaseMaterialType.base_material_type_attrs).join(BaseMaterialTypeAttr.base_material_type_attr_rules)\
             .filter(BaseMaterialType.code == u'11', parent_bmt.code == u'25', BaseMaterialTypeAttr.description==u'增加属性', BaseMaterialTypeAttrRule.rule_description==u'增加规则').all()
             self.assertEqual(1, len(be))
             ind_info[u'key_word'] = u'增加关键字'
             result = TemplateUpdater.add_template_attr_key_word(ind_info)
             be = session.query(BaseMaterialType, parent_bmt, BaseMaterialTypeAttr, BaseMaterialTypeAttrKeyWord).join((parent_bmt, parent_bmt.id == BaseMaterialType.parent_id)).join(BaseMaterialType.base_material_type_attrs).join(BaseMaterialTypeAttr.base_material_type_attr_key_words)\
             .filter(BaseMaterialType.code == u'11', parent_bmt.code == u'25', BaseMaterialTypeAttr.description==u'增加属性', BaseMaterialTypeAttrKeyWord.key_words==u'增加关键字').all()
             self.assertEqual(1, len(be))

# Run test cases.
if __name__ == '__main__':
    unittest.main()
