# coding=utf-8
u"""
Description: Test the main functions of extract.
User: Jerry.Fang
Date: 13-12-30
"""
import os, sys
sys.path.append( os.path.join( os.path.abspath(os.path.dirname(__file__)) , '../..'))

import requests
import ujson
import unittest
from template.basic_template_generator import BasicTemplate
from extractor.data_extractor import DataExtractor
from model.session import *
from model.basic_element import BasicElement
from xlrd import open_workbook
from model.basic_element import BasicElement
from model.base_material_type import *
from model.base_material_type_attr import *
from model.base_material_type_attr_value import *
from model.base_material_type_attr_rule import *
from model.base_material_type_attr_key_word import *
from sqlalchemy.orm import aliased


class TestExtractorFunctions(unittest.TestCase):
    def setUp(self):
        # Initial test database.
        self.m_basic_template = BasicTemplate()
        self.m_basic_template.set_primary_path( os.path.join( os.path.abspath(os.path.dirname(__file__)) , 'primary_rule_test2.xls') )
        self.m_basic_template.clean_table()
        self.m_basic_template.generate_basic_template()
        self.m_basic_template.gen_attr_rule_in_all_basic_template()

    def test_extract_fun(self):

        # Extract product information.
        m_data_extractor = DataExtractor()
        m_data_extractor.open_xls_input_file( os.path.join( os.path.abspath(os.path.dirname(__file__)) , 'input_1_test.xls') )
        m_data_extractor.create_xls_output_file_handle( os.path.join( os.path.abspath(os.path.dirname(__file__)) ,'extract_result_test.xls') )
        m_data_extractor.extract_product_info()

        # Check sheet name.
        actual_result_file_handle = open_workbook( os.path.join( os.path.abspath(os.path.dirname(__file__)) , 'extract_result_test.xls'))
        actual_sheet_names_list = actual_result_file_handle.sheet_names()
        expect_sheet_names_list = [u'25#11', u'25#03', u'25#01']
        self.assertEqual(expect_sheet_names_list, actual_sheet_names_list)

        # Check sheet 25#11.
        actual_sheet_handle = actual_result_file_handle.sheet_by_name(u'25#11')
        self.assertEqual(4, actual_sheet_handle.nrows)
        actual_rd_line = actual_sheet_handle.row_values(0)
        expect_rd_line = [u'输入信息', u'', u'', u'', u'', u'', u'', u'', u'', u'', u'解析结果', u'', u'', u'',
                          u'', u'', u'', u'', u'', u'', u'', u'', u'', u'']
        self.assertListEqual(expect_rd_line, actual_rd_line)
        actual_rd_line = actual_sheet_handle.row_values(1)
        expect_rd_line = [u'是否是杂志数据', u'定额编码', u'类别编码', u'公司名称', u'产品名称', u'规格型号', u'品牌', u'计量单位', u'价格', u'备注',
                          u'标称截面(mm2)', u'工作类型', u'绝缘材料', u'品种', u'电线特征', u'工作温度', u'标称直径(mm)', u'内护层材料', u'护套材料', u'芯数*标称截面', u'额定电压(KV)', u'线芯材质', u'芯数', u'无法解析部分']
        self.assertListEqual(expect_rd_line, actual_rd_line)
        actual_rd_line = actual_sheet_handle.row_values(2)
        expect_rd_line = [u'', u'', u'2511', u'广东远光电缆实业有限公司', u'高压交联电力电缆', u'  8.7/15kV  VV22  一芯  25m㎡', u'远光', u'千米', u'65377.8', u'',
                          u'25mm2', u'', u'V聚氯乙稀绝缘', u'', u'', u'', u'', u'', u'V22钢带铠装聚氯乙稀护套', u'', u'8.7/15kV', u'', u'一芯', u'']
        self.assertListEqual(expect_rd_line, actual_rd_line)
        actual_rd_line = actual_sheet_handle.row_values(3)
        expect_rd_line = [u'', u'', u'2511', u'广东远光电缆实业有限公司', u'固定敷设用电线电缆、多股软线', u'RVV  四芯  6.0m㎡', u'远光', u'千米', u'37624.5', u'',
                          u'6.0mm2', u'', u'V聚氯乙稀绝缘', u'', u'', u'', u'', u'V聚氯乙烯护套', u'', u'', u'', u'', u'四芯', u'R']
        self.assertListEqual(expect_rd_line, actual_rd_line)

        # Check sheet 25#03.
        actual_sheet_handle = actual_result_file_handle.sheet_by_name(u'25#03')
        self.assertEqual(3, actual_sheet_handle.nrows)
        actual_rd_line = actual_sheet_handle.row_values(0)
        expect_rd_line = [u'输入信息', u'', u'', u'', u'', u'', u'', u'', u'', u'', u'解析结果', u'', u'', u'',
                          u'', u'', u'', u'', u'', u'', u'']
        self.assertListEqual(expect_rd_line, actual_rd_line)
        actual_rd_line = actual_sheet_handle.row_values(1)
        expect_rd_line = [u'是否是杂志数据', u'定额编码', u'类别编码', u'公司名称', u'产品名称', u'规格型号', u'品牌', u'计量单位', u'价格', u'备注',
                          u'工作类型', u'绝缘材料', u'品种', u'电线特征', u'工作温度', u'护套材料', u'标称截面(mm2)', u'额定电压(KV)', u'线芯材质', u'芯数', u'无法解析部分']
        self.assertListEqual(expect_rd_line, actual_rd_line)
        actual_rd_line = actual_sheet_handle.row_values(2)
        expect_rd_line = [u'', u'', u'2503', u'广东远光电缆实业有限公司', u'固定敷设用电线电缆、多股软线', u'RVSV  一芯  0.5m㎡', u'远光', u'千米', u'1709.1', u'',
                          u'', u'S丝绝缘', u'', u'R软结构', u'', u'V聚氯乙稀护套', u'0.5mm2', u'', u'', u'一芯', u'V']
        self.assertListEqual(expect_rd_line, actual_rd_line)

        # Check sheet 25#01.
        actual_sheet_handle = actual_result_file_handle.sheet_by_name(u'25#01')
        self.assertEqual(3, actual_sheet_handle.nrows)
        actual_rd_line = actual_sheet_handle.row_values(0)
        expect_rd_line = [u'输入信息', u'', u'', u'', u'', u'', u'', u'', u'', u'',
                          u'解析结果', u'', u'', u'', u'', u'']
        self.assertListEqual(expect_rd_line, actual_rd_line)
        actual_rd_line = actual_sheet_handle.row_values(1)
        expect_rd_line = [u'是否是杂志数据', u'定额编码', u'类别编码', u'公司名称', u'产品名称', u'规格型号', u'品牌', u'计量单位', u'价格', u'备注',
                          u'截面形状', u'单线直径(mm)', u'品种', u'软硬度', u'标称截面(mm2)', u'无法解析部分']
        self.assertListEqual(expect_rd_line, actual_rd_line)
        actual_rd_line = actual_sheet_handle.row_values(2)
        expect_rd_line = [u'', u'', u'2501', u'广东远光电缆实业有限公司', u'钢芯耐热铝合金绞线', u'NRLH58J、NRLH60J  1440/120', u'远光', u't', u'32618.7', u'',
                          u'', u'', u'', u'', u'', u'NRLH58J、NRLH60J  1440/120']
        self.assertListEqual(expect_rd_line, actual_rd_line)

        from statistic.stat_info_querier import StatInfoQuerier
        self.assertEqual(True, StatInfoQuerier.get_val(u'msg_total_time') > 0)
        self.assertEqual(4, StatInfoQuerier.get_val(u'msg_count'))
        self.assertEqual(80, StatInfoQuerier.get_val(u'msg_total_len'))
        self.assertEqual(55, StatInfoQuerier.get_val(u'msg_extract_len'))
        pass

# Run test cases.
if __name__ == '__main__':
    unittest.main()
