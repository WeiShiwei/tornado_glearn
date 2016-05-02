# coding=utf-8
u"""
Description: Extract data from the product information file.
             Store result in the result file.
User: Jerry.Fang
Date: 13-12-09
"""

from datetime import datetime
from xlrd import open_workbook
from xlwt import *
from model.session import *
from template.match_rule import MatchRule
from template.logger import logger
from model.basic_element import BasicElement
import copy
import redis
from extractor.config import config
import ujson
import time
from sqlalchemy.orm import aliased
from model.base_material_type import *
from model.base_material_type_attr import *
from model.base_material_type_attr_value import *
from model.base_material_type_attr_key_word import *
from model.base_material_type_attr_rule import *

##
#Description: product template will be store in redis.
#             If the template can not be found in redis, function will
#             search template in database and store in redis.

# template_redis.get(name)
# template_redis.set(name, value)
template_redis = redis.StrictRedis(
    host=config.REDIS_HOST,
    port=config.REDIS_PORT,
    db=config.REDIS_DB
)

class ExtractResult():
    def __init__(self):
        self.class_id = 0
        self.original_str = []
        self.result_attr = {}
        self.unknown_str = []

##
#Description: Extract product information from file.
#             All result will be stored in other file..


class DataExtractor():

    def __init__(self):
        self._input_file_handle = []
        self._output_file_handle = []
        self._output_sheet_handle = {}
        pass

    # Source xls file's location.
    input_file = "../../InputFile_test/input_1.xls"
    output_file = "../../InputFile_test/output_1.xls"

    # Open source xls file.
    def open_xls_input_file(self, path=input_file):
        try:
            self._input_file_handle = open_workbook(path)
            logger.info('Open file successfully: "%s" ' % path)
            self.input_file = path
        except Exception as exc:
            logger.error('Can not open file: "%s" Info: %s' % (path, exc))
            exit()

    # Create xls file used to store result.
    def create_xls_output_file_handle(self, path=output_file):
        try:
            #self.output_file = path.replace('.xls', '_result_') + datetime.now().strftime("%Y%m%d_%H_%M_%S") + '.xls'
            self.output_file = path
            self._output_file_handle = Workbook(encoding='utf-8')
            logger.info('Create file handle successfully: "%s" ' % path)
        except Exception as exc:
            logger.error('Can not create file: "%s" Info: %s' % (path, exc))
            exit()

    # Generate class id list.
    @staticmethod
    def gen_class_id_list(class_id_list):
        parent_bmt = aliased(BaseMaterialType)        
        with get_session() as session:
            be = session.query(BaseMaterialType, parent_bmt).join((parent_bmt, parent_bmt.id == BaseMaterialType.parent_id)).all()
            if 0 != len(be):
                for i in be:
                    class_id = MatchRule.encode_class_id(i[1].code, i[0].code)
                    class_id_list.append(class_id)

    # Find products' template and store it in the template dictionary.
    @staticmethod
    def find_template_pool_in_db(class_id, template_dic_pool):
        lv1_id, lv2_id = MatchRule.decode_class_id(class_id)
        parent_bmt = aliased(BaseMaterialType)
        if class_id not in template_dic_pool.keys():

            # Get template from redis at first.
            if template_redis.get(class_id) is not None: ### template_redis
                template_dic_pool[class_id] = ujson.loads(template_redis.get(class_id))
            else:
                template_dic_pool[class_id] = None

            # Search template from database when template is not in redis.
            if template_dic_pool[class_id] is None:
                with get_session() as session:
                    be = session.query(BaseMaterialType, parent_bmt).join((parent_bmt, parent_bmt.id == BaseMaterialType.parent_id))\
                    .filter(BaseMaterialType.code == lv2_id, parent_bmt.code == lv1_id).all()
                    if 0 == len(be):
                        del template_dic_pool[class_id]
                        pass
                        #logger.warning('Can not find basic template. lv1_id = %d, lv2_id = %d' % (lv1_id, lv2_id))
                    else:
                        template_dic_pool[class_id] = {}
                        attr_rule_dic = {}
                        for attr in be[0][0].base_material_type_attrs:
                            template_dic_pool[class_id][attr.description] = []
                            attr_rule_dic[attr.description] = u'-attr_rule;'
                            if attr.is_all_match:
                               attr_rule_dic[attr.description] += u'-all_value;'
                            str_rule = u''
                            str_key_word = u''
                            if 0 < len(attr.base_material_type_attr_rules):
                               str_rule = u'-str_format;'
                               for rule in attr.base_material_type_attr_rules:
                                   str_rule += (rule.rule_description + u';')
                            if 0 < len(attr.base_material_type_attr_key_words):
                               str_key_word = u'-key_word;'
                               for key_word in attr.base_material_type_attr_key_words:
                                   str_key_word += (key_word.key_words + u';')
                            attr_rule_dic[attr.description] += (str_key_word + str_rule)
                            for value in attr.base_material_type_attr_values:
                                template_dic_pool[class_id][attr.description].append(value.description)
                        # Store attribute rule to template pool.
                        for attr_name, attr_val in attr_rule_dic.items():
                            if attr_name not in template_dic_pool[class_id].keys():
                                template_dic_pool[class_id][attr_name] = []
                            template_dic_pool[class_id][attr_name].append(attr_val)

                        # Log all detail information.
                        logger.info('Find basic template. lv1_id = %s, lv2_id = %s,' % (lv1_id, lv2_id))
                        for k, m in template_dic_pool[class_id].iteritems():
                            attr_val_str = ''
                            for n in range(0, len(m)):
                                attr_val_str += m[n] + ','
                            logger.debug('+-%s : %s' % (k, attr_val_str))
                        # Store template in redis.
                        template_redis.delete(class_id)
                        template_redis.set(class_id, ujson.dumps(template_dic_pool[class_id]))

    # find name's column number.
    @staticmethod
    def find_col_num_by_name(col_name, rd_line):
        col_num = 0
        for j in range(0, len(rd_line)):
            if col_name == rd_line[j]:
                col_num = j
                break
        return col_num

    # Record max column length.
    @staticmethod
    def record_max_col_width(max_col_width_list, col_idx, col_width):
        if col_idx >= len(max_col_width_list) and col_idx >= 0:
            for i in range(len(max_col_width_list), col_idx+1):
                max_col_width_list.append(4)
        max_col_width_list[col_idx] = col_width if col_width > max_col_width_list[col_idx] \
            else max_col_width_list[col_idx]

    # Record max column length.
    def sheet_cell_wt(self, worksheet, raw, col, cell_info, font, max_col_width_list):
        worksheet.write(raw, col, cell_info, font)
        self.record_max_col_width(max_col_width_list, col, len(cell_info))

    # Output all result to xls file.
    def output_all_result_to_xls(self, extract_result_list, title_line):
        last_wt_row = {}
        sheet_num_map = {}
        max_col_width_dic = {}

        # back ground color.
        org_bkgc = easyxf('border: left thin, top thin, right thin, bottom thin; '
                          'pattern: pattern solid, fore_colour white; ')
        res_bkgc = easyxf('border: left thin, top thin, right thin, bottom thin; '
                          'pattern: pattern solid, fore_colour light_turquoise; ')
        unk_bkgc = easyxf('border: left thin, top thin, right thin, bottom thin; '
                          'pattern: pattern solid, fore_colour light_yellow; ')

        for i in range(0, len(extract_result_list)):
            class_id = extract_result_list[i].class_id
            # Create new sheet.
            if class_id not in last_wt_row.keys():
                last_wt_row[class_id] = 0
                sheet_num_map[class_id] = len(sheet_num_map)
                max_col_width_dic[class_id] = []
                worksheet = self._output_file_handle.add_sheet(str(class_id))
            # Find already exist sheet.
            else:
                # Find sheet number.
                sheet_number = sheet_num_map[class_id]
                worksheet = self._output_file_handle.get_sheet(sheet_number)

            # Write title line.
            if 0 == last_wt_row[class_id]:
                col = 0
                self.sheet_cell_wt(worksheet, 0, 0, u'输入信息', org_bkgc, max_col_width_dic[class_id])
                for j in range(0, len(title_line)):
                    self.sheet_cell_wt(worksheet, 1, col, title_line[j], org_bkgc, max_col_width_dic[class_id])
                    col += 1
                self.sheet_cell_wt(worksheet, 0, col, u'解析结果', res_bkgc, max_col_width_dic[class_id])
                for attr_name in extract_result_list[i].result_attr.keys():
                    self.sheet_cell_wt(worksheet, 1, col, attr_name, res_bkgc, max_col_width_dic[class_id])
                    col += 1
                self.sheet_cell_wt(worksheet, 1, col, u'无法解析部分', unk_bkgc, max_col_width_dic[class_id])
                last_wt_row[class_id] = 2

            # Write result.
            row = last_wt_row[class_id]
            col = 0
            unknown_info_str = u''
            for org_str in extract_result_list[i].original_str:
                org_str = org_str.replace(u'\t', u'  ')
                self.sheet_cell_wt(worksheet, row, col, org_str, org_bkgc, max_col_width_dic[class_id])
                col += 1
            for attr_val in extract_result_list[i].result_attr.values():
                attr_val = attr_val.replace(u'\t', u'  ')
                self.sheet_cell_wt(worksheet, row, col, attr_val, res_bkgc, max_col_width_dic[class_id])
                col += 1
            for unknown_info in extract_result_list[i].unknown_str:
                unknown_info_str += unknown_info if unknown_info_str == u'' else u'  ' + unknown_info
            self.sheet_cell_wt(worksheet, row, col, unknown_info_str, unk_bkgc, max_col_width_dic[class_id])
            last_wt_row[class_id] += 1

        # Set col width.
        for class_id in sheet_num_map.keys():
            sheet_number = sheet_num_map[class_id]
            worksheet = self._output_file_handle.get_sheet(sheet_number)
            for col_idx in range(0, len(max_col_width_dic[class_id])):
                if max_col_width_dic[class_id][col_idx]*400 > 30000:
                    col_width = 30000
                else:
                    col_width = max_col_width_dic[class_id][col_idx]*400
                worksheet.col(col_idx).width = col_width

        # Save xls file.
        self._output_file_handle.save(self.output_file)

    # Create attr_name <-> rule map.
    @staticmethod
    def gen_attr_name_rule_map(class_id, template_dic_pool, attr_name_rule_map):
        if class_id not in attr_name_rule_map.keys():
            attr_name_rule_map[class_id] = {}
            logger.info('Create rule map: class_id %s' % class_id)
            for attr_name in template_dic_pool[class_id].keys():

                # Find attribute rule.
                rule_idx = -1
                for j in range(len(template_dic_pool[class_id][attr_name])-1, -1, -1):
                    if u'attr_rule' in template_dic_pool[class_id][attr_name][j]:
                        rule_idx = j
                        attr_name_rule_map[class_id][attr_name] = template_dic_pool[class_id][attr_name][j]
                        logger.debug('+- %s: %s' % (attr_name, attr_name_rule_map[class_id][attr_name]))
                        break
                if -1 == rule_idx:
                    attr_name_rule_map[class_id][attr_name] = u''
                    logger.debug('+- %s: Null' % attr_name)
                    logger.info('Can not find rule!( template class id %s, attribute name %s)' %
                                (class_id, attr_name))
                    continue
    #--------------------------------------------------------------------
    @staticmethod
    def prc_assembly_attr_rule(class_id, product_info_list, m_extract_result):
        logger.debug('Start to run prc_assembly_attr_rule rule.')
        
        first_type_code = class_id.split('#')[0]
        second_type_code = class_id.split('#')[1]
        attrNameValue_dict = MatchRule.command_assembly_attr(product_info_list, first_type_code,second_type_code)
        
        for (assemblyAttrName,attrName_val_dict) in attrNameValue_dict.items():
            if len(attrName_val_dict) == 0:
                continue
            for (attrName,attrValue) in attrName_val_dict.items():
                m_extract_result.result_attr[attrName] = ' '.join(attrValue)
                # logger.debug('+-find assembly attribute info. %s: %s' % (attrName, attrValue)
    #--------------------------------------------------------------------

    # Run all_value rule by attr_name<->rule map.
    @staticmethod
    def prc_all_val_rule(template_dic_pool, class_id, attr_name_rule_map, product_info_list, m_extract_result):
        logger.debug('Start to run all_value rule.')
        # import pdb;pdb.set_trace() ###
        # (Pdb) template_dic_pool
        # {u'99#88': {u'assemblyAttrName': [u"JYV200|{'\u805a\u6c2f':'J','\u4e59\u70ef':'v','\u7edd\u7f18':'v','\u989d\u5b9a\u7535\u538b':'200'}", u'-attr_rule;-all_value;'], 
        # u'\u6d4b\u8bd5\u7c7battr_name3': [u'JY\u805a\u6c2f\u4e59\u70ef\u7edd\u7f18', u'-attr_rule;-all_value;-key_word;JY_JY\u805a\u6c2f\u4e59\u70ef\u7edd\u7f18;'], 
        # u'\u6d4b\u8bd5\u7c7battr_name1(mm2)': [u'15mm2', u'-attr_rule;-all_value;-str_format;\\d+[.]{0,1}\\d*[/]{0,1}\\d*mm2;re.I;']}}
        
        # (Pdb) class_id
        # u'99#88'
        # (Pdb) attr_name_rule_map
        # {u'99#88': {u'\u6d4b\u8bd5\u7c7battr_name1(mm2)': u'-attr_rule;-all_value;-str_format;\\d+[.]{0,1}\\d*[/]{0,1}\\d*mm2;re.I;', 
        # u'\u6d4b\u8bd5\u7c7battr_name3': u'-attr_rule;-all_value;-key_word;JY_JY\u805a\u6c2f\u4e59\u70ef\u7edd\u7f18;', 
        # u'assemblyAttrName': u'-attr_rule;-all_value;'}}
        # (Pdb) product_info_list
        # [u'8.7/15kV', u'JYV200', u'\u4e00\u82af', u'15mm2', u'\u7ed3\u67847', u'BB']
        # (Pdb) m_extract_result
        # <extractor.data_extractor.ExtractResult instance at 0xb655680c>
        for attr_name in template_dic_pool[class_id].keys():

            # Check whether attribute rule is exist.
            if u'all_value' not in attr_name_rule_map[class_id][attr_name]:
                continue

            # Execute the command from rule.
            if m_extract_result.result_attr[attr_name] != u'':
                m_extract_result.result_attr[attr_name] += u'\t'
            ### {attr_name:attr_value,} and update product_info_list
            m_extract_result.result_attr[attr_name] = \
                MatchRule.command_all_value(product_info_list, template_dic_pool[class_id][attr_name]) ###
            if m_extract_result.result_attr[attr_name] != u'':
                logger.debug('+-find attribute info. %s: %s' % (attr_name, m_extract_result.result_attr[attr_name]))

    # Run key words rule by attr_name<->rule map.
    @staticmethod
    def prc_key_words_rule(class_id, attr_name_rule_map, product_info_list, m_extract_result):
        logger.debug('Start to run key_word rule.')
        delete_product_info_list = []
        for i in range(0, len(product_info_list)):
            if MatchRule.check_format_letter_number(product_info_list[i]):
                # check key word.
                max_match_len = -1
                match_attr_name = {}
                while 0 != max_match_len:
                    max_match_len = 0
                    max_match_key = u''
                    max_match_key_attr_name = u''
                    max_match_key_detail = u''
                    for attr_name in attr_name_rule_map[class_id].keys():
                        if u'key_word' in attr_name_rule_map[class_id][attr_name]:
                            rule_list = attr_name_rule_map[class_id][attr_name].split(u';')
                            start_match_kw = False
                            for j in range(0, len(rule_list)):
                                if u'key_word' in rule_list[j]:
                                    start_match_kw = True
                                elif start_match_kw and u'-' in rule_list[j]:
                                    break
                                elif start_match_kw and u'_' in rule_list[j]:
                                    if u'_' != rule_list[j][-1]:
                                        key_word = (rule_list[j].split(u'_'))[0]
                                        key_word_detail = (rule_list[j].split(u'_'))[1]
                                        if key_word in product_info_list[i]:
                                            if max_match_len < len(key_word) and \
                                               attr_name not in match_attr_name.keys():
                                                max_match_len = len(key_word)
                                                max_match_key_attr_name = attr_name
                                                max_match_key_detail = key_word_detail
                                                max_match_key = key_word
                                                logger.debug('Dissect %s key word %s.' % (attr_name, key_word))
                                                break
                    if u'' != max_match_key:
                        product_info_list[i] = product_info_list[i].replace(max_match_key, u'', 1)
                        match_attr_name[max_match_key_attr_name] = max_match_key_detail

                    if product_info_list[i] == u'' or product_info_list[i] == u'-':
                        delete_product_info_list.append(i)
                        break
                    elif max_match_len == 0:
                        break
                    else:
                        max_match_len = -1

                # Store value to result.
                for attr_name in match_attr_name.keys():
                    if m_extract_result.result_attr[attr_name] == u'':
                        m_extract_result.result_attr[attr_name] += match_attr_name[attr_name]
                    elif match_attr_name[attr_name] not in m_extract_result.result_attr[attr_name]:
                        m_extract_result.result_attr[attr_name] += u'\t' + match_attr_name[attr_name]
                    logger.debug('Get result_attr[%s] = %s.' % (attr_name, m_extract_result.result_attr[attr_name]))

        # Delete empty node in product_info_list.
        MatchRule.del_product_info_by_del_list(delete_product_info_list, product_info_list)

    # Run string format rule by attr_name<->rule map.
    @staticmethod
    def prc_str_format_rule(class_id, template_dic_pool, product_info_list, attr_name_rule_map, m_extract_result):
        logger.debug('Start to run str_format rule.')
        delete_product_info_list = []
        for i in range(0, len(product_info_list)):
            for attr_name in template_dic_pool[class_id].keys():
                regular_ex_list = []
                start_to_get_ex = False
                # Find regular expression.
                if u'str_format' in attr_name_rule_map[class_id][attr_name]:
                    rule_list = attr_name_rule_map[class_id][attr_name].split(u';')
                    for j in range(0, len(rule_list)): 
                        if u'str_format' in rule_list[j]:
                            start_to_get_ex = True
                        elif u'-' in rule_list[j][0:1] and start_to_get_ex:
                            break
                        elif start_to_get_ex:
                            if u're.' not in rule_list[j] and u'' != rule_list[j]:
                                regular_ex_list.append(rule_list[j])
                            elif 0 < len(regular_ex_list):
                                regular_ex_list[-1] += u';' + rule_list[j]

                # Use regular expression list.
                if 0 < len(regular_ex_list) and m_extract_result.result_attr[attr_name] == u'':
                    for regular_ex_full in regular_ex_list:
                        regular_ex = regular_ex_full.split(u';')[0]
                        regular_limit = u'' if 1 == len(regular_ex_full.split(u';')) else regular_ex_full.split(u';')[1]
                        if MatchRule.command_str_format(regular_ex, regular_limit, product_info_list[i]):
                            m_extract_result.result_attr[attr_name] = product_info_list[i]
                            delete_product_info_list.append(i)
                            break

        # Delete empty node in product_info_list.
        MatchRule.del_product_info_by_del_list(delete_product_info_list, product_info_list)


    ##
    ##关键方法
    # Extractor product information by the basic template.
    def extract_product_info(self):

        # Get the first table and max row number.
        table = self._input_file_handle.sheet_by_index(0)
        row_num = table.nrows
        id_col_str = u'类别编码'
        id_col_id = 0
        src_col_str = u'规格型号'
        src_col_id = 0
        title_line = []
        template_dic_pool = {}
        extract_result_list = []
        attr_name_rule_map = {}
        logger.info('Get table with %d lines ok.' % row_num)

        # Read all the lines.
        start_time = int(time.time()*1000)
        unextract_total_len = 0
        msg_count = 0
        msg_total_len = 0
        logger.info('Start to extract product information....')
        for rd_row_idx in range(0, row_num):

            rd_line = table.row_values(rd_row_idx)
            logger.debug('Read line %d.' % rd_row_idx)

            # Get column index in the 1st line.
            if rd_row_idx is 0:
                title_line = copy.copy(rd_line)
                id_col_id = self.find_col_num_by_name(id_col_str, rd_line)
                src_col_id = self.find_col_num_by_name(src_col_str, rd_line)
                logger.info('Get %s column id: %d; %s column id: %d;' %
                            (id_col_str, id_col_id, src_col_str, src_col_id))
                continue

            # Get basic template by id.
            if rd_line[id_col_id] == u'':
                continue
            # encode class_id like this '99#88'
            class_id = MatchRule.encode_class_id(rd_line[id_col_id], 0, u'xls')
            self.find_template_pool_in_db(class_id, template_dic_pool)

            # Start to extract information by rule.
            if class_id not in template_dic_pool.keys():
                logger.info('Can not find template class id %s .' % class_id)
                continue

            # Generate result element.
            m_extract_result = ExtractResult()
            m_extract_result.class_id = class_id
            m_extract_result.original_str = copy.copy(rd_line)
            for attr_name in template_dic_pool[class_id].keys():
                m_extract_result.result_attr[attr_name] = u''

            # Create attr_name <-> rule map.，找出keyword , format
            self.gen_attr_name_rule_map(class_id, template_dic_pool, attr_name_rule_map)

            # Get product information list by split r'\s+'.
            import re
            product_info_list = re.split(r'\s+', rd_line[src_col_id])
            MatchRule.replace_special_word(product_info_list)
            logger.debug('Read class_id: %s product info: %s .' % (class_id, rd_line[src_col_id]))

            # Execute the first rule: all_value.
            self.prc_all_val_rule(template_dic_pool, class_id, attr_name_rule_map, product_info_list, m_extract_result)

            # Execute the second rule: key_word.
            self.prc_key_words_rule(class_id, attr_name_rule_map, product_info_list, m_extract_result)

            # Execute the third rule: str_format.
            self.prc_str_format_rule(class_id, template_dic_pool, product_info_list, attr_name_rule_map,
                                     m_extract_result)

            # Save the rest information.
            if len(product_info_list):
                m_extract_result.unknown_str = copy.copy(product_info_list)

            # Add to result list.
            extract_result_list.append(m_extract_result)

            # Record message number / total length.
            msg_count += 1
            msg_total_len += len(rd_line[src_col_id])
            for ele in m_extract_result.unknown_str:
                unextract_total_len += len(ele)

        # Record statistic information.
        end_time = int(time.time()*1000)
        from statistic.stat_info_querier import StatInfoQuerier
        StatInfoQuerier.store_val(
            u'msg_total_time', StatInfoQuerier.get_val(u'msg_total_time')+end_time-start_time
        )
        StatInfoQuerier.store_val(
            u'msg_count', StatInfoQuerier.get_val(u'msg_count')+msg_count
        )
        StatInfoQuerier.store_val(
            u'msg_total_len', StatInfoQuerier.get_val(u'msg_total_len')+msg_total_len
        )
        StatInfoQuerier.store_val(
            u'msg_extract_len', StatInfoQuerier.get_val(u'msg_extract_len')+msg_total_len-unextract_total_len
        )

        # Output result to xls.
        self.output_all_result_to_xls(extract_result_list, title_line)

    ##
    # Extract indicated product information.
    @staticmethod
    def extract_product_info_by_ind(lv1_id, lv2_id, product_info, result):

        # Record start time.
        start_time = int(time.time()*1000)

        # Generate class id.
        ### class_id=25#88
        class_id = MatchRule.encode_class_id(lv1_id, lv2_id)

        # Get basic template by id.
        template_dic_pool = {}
        DataExtractor.find_template_pool_in_db(class_id, template_dic_pool)
        if class_id not in template_dic_pool.keys():
            logger.error('No template, can not extract product id %s %s.' % (lv1_id, lv2_id))
            return

        # Start to extract information by rule.
        # Generate result element.
        m_extract_result = ExtractResult() ### [ m_extract_result]
        m_extract_result.class_id = class_id
        m_extract_result.original_str = copy.copy(product_info)
        for attr_name in template_dic_pool[class_id].keys():
            m_extract_result.result_attr[attr_name] = u''

        # Create attr_name <-> rule map.
        attr_name_rule_map = {}
        DataExtractor.gen_attr_name_rule_map(class_id, template_dic_pool, attr_name_rule_map) ### [attr_name_rule_map]

        # import pdb;pdb.set_trace() ###
        ### product_info='8.7/15kV    JYV 一芯  15m㎡    结构7 BB'
        ### product_info_list=[u'8.7/15kV', u'JYV', u'\u4e00\u82af', u'15m\u33a1', u'\u7ed3\u67847', u'BB']
        # Get product information list by split r'\s+'.
        import re
        product_info_list = re.split(r'\s+', product_info)
        product_info_list_bak = product_info.split() #->
        MatchRule.replace_special_word(product_info_list)
        logger.debug('Read class_id: %s product info: %s .' % (class_id, product_info))

        ###---------------------------------------------------------------------
        # import pdb;pdb.set_trace() ###
        # template_dic_pool={u'99#88': {u'\u6d4b\u8bd5\u7c7battr_name3': [u'JY\u805a\u6c2f\u4e59\u70ef\u7edd\u7f18',u'-attr_rule;-all_value;-key_word;JY_JY\u805a\u6c2f\u4e59\u70ef\u7edd\u7f18;'], 
        #  u'\u6d4b\u8bd5\u7c7battr_name1(mm2)': [u'15mm2', u'-attr_rule;-all_value;-str_format;\\d+[.]{0,1}\\d*[/]{0,1}\\d*mm2;re.I;']}}
        
        # class_id = u'99#88'
        
        # attr_name_rule_map = {u'99#88': {u'\u6d4b\u8bd5\u7c7battr_name3': u'-attr_rule;-all_value;-key_word;JY_JY\u805a\u6c2f\u4e59\u70ef\u7edd\u7f18;', u'\u6d4b\u8bd5\u7c7battr_name1(mm2)': u'-attr_rule;-all_value;-str_format;\\d+[.]{0,1}\\d*[/]{0,1}\\d*mm2;re.I;'}}
        
        # product_info_list = [u'8.7/15kV', u'JYV', u'\u4e00\u82af', u'\u7ed3\u67847', u'BB']
        
        # m_extract_result = 
        # (Pdb) m_extract_result.class_id
        # u'99#88'
        # (Pdb) m_extract_result.original_str
        # u'8.7/15kV\tJYV\t\u4e00\u82af  15m\u33a1\t\u7ed3\u67847\tBB'
        # (Pdb) m_extract_result.result_attr
        # {u'\u6d4b\u8bd5\u7c7battr_name3': u'', u'\u6d4b\u8bd5\u7c7battr_name1(mm2)': u'15mm2'}
        # (Pdb) m_extract_result.unknown_str
        # []
        ###---------------------------------------------------------------------    

        # Execute the first rule: all_value.
        DataExtractor.prc_all_val_rule(
            template_dic_pool, class_id, attr_name_rule_map, product_info_list, m_extract_result
        )

        # Execute the second rule: key_word.
        DataExtractor.prc_key_words_rule(
            class_id, attr_name_rule_map, product_info_list, m_extract_result
        )

        # Execute the third rule: str_format.
        DataExtractor.prc_str_format_rule(
            class_id, template_dic_pool, product_info_list, attr_name_rule_map, m_extract_result
        )

        ###--------------------------------------------------------------------        
        # import pdb;pdb.set_trace()
        DataExtractor.prc_assembly_attr_rule(
            class_id, product_info_list_bak, m_extract_result
        )
        # (Pdb) product_info_list
        # [u'8.7/15kV', u'\u4e00\u82af', u'15mm2', u'\u7ed3\u67847', u'BB']
        # (Pdb) m_extract_result.result_attr
        # {u'\u6d4b\u8bd5\u7c7battr_name3': u'200V(\u989d\u5b9a\u7535\u538b)', u'\u6d4b\u8bd5\u7c7battr_name1(mm2)': u'\u805a\u6c2f\u4e59\u70ef(\u6750\u8d28)'}
        # m_extract_result.result_attr属性和属性值的对应，可能被后面的处理更新掉
        #--------------------------------------------------------------------

        # Save the rest information.
        if len(product_info_list):
            m_extract_result.unknown_str = copy.copy(product_info_list)

        # convert to API result format.
        for attr_name in m_extract_result.result_attr.keys():
            result[attr_name] = m_extract_result.result_attr[attr_name]
        result[u'无法解析部分'] = u''
        for unknown_ele in m_extract_result.unknown_str:
            result[u'无法解析部分'] += unknown_ele + u'\t'

        # Record statistic information.
        end_time = int(time.time()*1000)
        from statistic.stat_info_querier import StatInfoQuerier
        StatInfoQuerier.store_val(
            u'msg_total_time', StatInfoQuerier.get_val(u'msg_total_time')+end_time-start_time
        )
        StatInfoQuerier.store_val(
            u'msg_count', StatInfoQuerier.get_val(u'msg_count')+1
        )
        StatInfoQuerier.store_val(
            u'msg_total_len', StatInfoQuerier.get_val(u'msg_total_len')+len(m_extract_result.original_str)
        )
        StatInfoQuerier.store_val(
            u'msg_extract_len',
            StatInfoQuerier.get_val(u'msg_extract_len')+len(m_extract_result.original_str)-len(result[u'无法解析部分'])
        )

#Main function.
if __name__ == '__main__':
    m_data_extractor = DataExtractor()
    m_data_extractor.open_xls_input_file('../../InputFile_test/input_1.xls')
    m_data_extractor.create_xls_output_file_handle('../../InputFile_test/result_' +
                                                   datetime.now().strftime("%Y%m%d_%H_%M_%S") +
                                                   '.xls')
    m_data_extractor.extract_product_info()
