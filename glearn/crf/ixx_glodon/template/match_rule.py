# coding=utf-8
u"""
Description: Used to match elements.
User: Jerry.Fang
Date: 13-12-05
"""

import re
from template.logger import logger

from assembly_template import AssemblyTemplate

##
#Description: Generate basic template from xls.
#

class MatchRule:
    
    def __init__(self):
        pass

    max_lv_id_val = 100

    @staticmethod
    def encode_class_id(lv1_id, lv2_id, src=u'normal'):
        if u'normal' == src:
            return u'%s#%s' % (lv1_id, lv2_id)
        elif u'xls' == src:
            m_lv1_id = lv1_id[0:2]
            m_lv2_id = lv1_id[2:4]
            return u'%s#%s' % (m_lv1_id, m_lv2_id)

    @staticmethod
    def decode_class_id(class_id):
        elem = class_id.split('#')
        return elem[0], elem[1]

    @staticmethod
    def replace_special_word_in_str(input_str):
        return input_str.replace(u'（', '(').replace(u'）', ')')\
                        .replace(u'×', '*').replace(u'×', '*')\
                        .replace(u' ', '').replace(u'／', '/')\
                        .replace(u'：', ':').replace(u'?', '3')\
                        .replace(u'㎡', 'm2').replace(u'ⅹ', '*')

    #Replace all the Special word.
    @staticmethod
    def replace_special_word(rd_line):
        for i in range(0, len(rd_line)):
            rd_line[i] = MatchRule.replace_special_word_in_str(rd_line[i])

    ##
    #Description: Compare str_a with str_b.
    #             Calculate the rate of str_a's char which is contained in str_b.
    @staticmethod
    def calc_str_match_rate(str_a, str_b):
        rate = 0.0
        count_char_num = 0.0
        str_a = str_a.lower()
        str_b = str_b.lower()
        if(0 == len(str_a)) or (0 == len(str_b)):
            return rate
        else:
            for i in range(0, len(str_a)):
                if str_a[i] in str_b:
                    count_char_num += 1
            rate = count_char_num*100/len(str_a)
        return rate

    ##
    #Description: read default rule indications list and generate attribute rule.
    @staticmethod
    def gen_attr_rule_by_val(attr_name, attr_list, attr_rule_index):
        attr_list[attr_rule_index] = u'-attr_rule;'

        #The first rule.
        attr_list[attr_rule_index] += u'-all_value;'

        #Find key word.
        key_list = []
        key_detail_list = []
        for i in range(0, len(attr_list)):
            if i != attr_rule_index:
                m = re.match(r'(\W+)(\w+)', attr_list[i])
                if m:
                    if (m.group(2) != '') and (m.group(2) not in key_list) and (m.group() == attr_list[i]):
                        key_list.append(m.group(2))
                        key_detail_list.append(attr_list[i])
                        continue
                m = re.match(r'(\w+)(\W+)', attr_list[i])
                if m:
                    if MatchRule.get_unit_name_from_attr_name(attr_name) != '':
                        continue
                    if (m.group(1) != '') and (m.group(1) not in key_list) and (m.group() == attr_list[i]):
                        key_list.append(m.group(1))
                        key_detail_list.append(attr_list[i])
                        continue
                m = re.match(r'(\w+)([(].*[)])', attr_list[i])
                if m:
                    if (m.group(1) != '') and (m.group(2) not in key_list) and (m.group() == attr_list[i]):
                        key_list.append(m.group(1))
                        key_detail_list.append(attr_list[i])
                        continue
        ## Store key word.
        if len(key_list) != 0:
            attr_list[attr_rule_index] += u'-key_word;'
            while len(key_list) != 0:
                list_length = len(key_list)
                max_len_idx = 0
                for j in range(0, list_length):
                    max_len_idx = j if (len(key_list[max_len_idx]) < len(key_list[j])) else max_len_idx
                attr_list[attr_rule_index] += key_list[max_len_idx] + u'_' + key_detail_list[max_len_idx] + u';'
                del key_list[max_len_idx]
                del key_detail_list[max_len_idx]

        #Find format.
        fmt = u'(\d+[.]{0,1}\d*)([*]{0,1})(\d*[.]{0,1}\d*)([+]{0,1})(\d*[.]{0,1}\d*)([*]{0,1})(\d*[.]{0,1}\d*)'
        #假设：如果属性命有括号，那么属性值是数字或者分数+单位
        m = re.match(r'(.+[(]{1})(.+)([)]{1})', attr_name)
        if m:
            if m.group(1) != '' and m.group(2) != '' and m.group(3) == u')':
                attr_list[attr_rule_index] += u'-str_format;'
                attr_list[attr_rule_index] += u'\d+[.]{0,1}\d*[/]{0,1}\d*'+m.group(2) + u';'
                attr_list[attr_rule_index] += u're.I;'
            else:
            #用假设的fmt正则式挨个匹配，如果能够匹配50%以上，就认为该fmt是一个合理的规则
                format_match_num = 0
                for i in range(0, len(attr_list)):
                    if i != attr_rule_index:
                        m = re.match(fmt, attr_list[i])
                        if m:
                            if attr_list[i] == m.group():
                                format_match_num += 1
                if (format_match_num*100/len(attr_list)) >= 50:
                    attr_list[attr_rule_index] += u'-str_format;'
                    attr_list[attr_rule_index] += fmt + u';'

        # Special rule config.
        if attr_name == u'芯数':
            attr_list[attr_rule_index] += u'-str_format;' + u'.+芯[加]{0,1}[大]{0,1}[地]{0,1}[线]{0,1}' + u';'
        elif attr_name == u'工作温度':
            attr_list[attr_rule_index] += u'-str_format;' + u'\d+[.]{0,1}\d*℃' + u';'
        elif attr_name == u'芯数*标称截面' and m:
            fmt_new = u'(\d+[.]{0,1}\d*)([*]{1})(\d+[.]{0,1}\d*)([+]{0,1})(\d*[.]{0,1}\d*)([*]{0,1})(\d*[.]{0,1}\d*)'
            attr_list[attr_rule_index] = attr_list[attr_rule_index].replace(fmt, fmt_new + u'mm2')
        elif attr_name == u'额定电压(KV)':
            attr_list[attr_rule_index] += u'\d+[/]{1}\d+V;re.I;'


    ##
    #Description: Get unit's name from attribute name.
    @staticmethod
    def get_unit_name_from_attr_name(attr_name, attr_val=u''):
        unit_name = u''
        #Normal.
        m = re.match(r'(.+[(]{1})(.+)([)]{1})', attr_name)
        if m:
            unit_name = m.group(2)
        # Special.
        elif attr_name == u'芯数':
            unit_name = u'芯'

        # unit_name is already in attribute value.
        if unit_name in attr_val and attr_val != u'':
            unit_name = u''

        return unit_name

    ##
    # Description: Delete information list by delete list.
    @staticmethod
    def del_product_info_by_del_list(delete_product_info_list, product_info_list):
        delete_product_info_list.sort()
        delete_product_info_list = [i for i in set(delete_product_info_list)]  
        for i in range(len(delete_product_info_list)-1, -1, -1):
            index = delete_product_info_list[i]
            logger.debug('del product info list %d: %s.' % (index, product_info_list[index]))
            del product_info_list[index]

#-------------------------------------------------------------------------
    @staticmethod
    def command_assembly_attr(product_info_list,first_type_code,second_type_code):
        
        ind_info = dict()
        ind_info[u'first_type_code'] = first_type_code
        ind_info[u'second_type_code'] = second_type_code
        assembly_attr_names = ' '.join(product_info_list)  # 集成属性名在这里其实是就应该是的product_info_list元素
        ind_info[u'assembly_attr_names'] = assembly_attr_names
        
        attrNameValue_dict = dict()
        AssemblyTemplate.retrieve_assembly_template(ind_info, attrNameValue_dict) 

        for (assemblyAttrName,attrName_val_dict) in attrNameValue_dict.items():
            if len(attrName_val_dict) == 0:
                continue
            try:
                product_info_list.remove(assemblyAttrName)
            except ValueError:
                logger.error("remove assemblyAttrName=%s in product_info_list failed!"%assemblyAttrName)

        return attrNameValue_dict

#-------------------------------------------------------------------------
    ##
    #Description: Get product info by template attribute list.
    @staticmethod
    def command_all_value(product_info_list, template_attr_val_list):
        result = u''
        # Check product information list and record the node which should be deleted.
        delete_product_info_list = []
        for i in range(0, len(product_info_list)):
            for j in range(0, len(template_attr_val_list)):
                if product_info_list[i].lower() == template_attr_val_list[j].lower():
                    result += product_info_list[i]
                    delete_product_info_list.append(i)
                    break
        # Delete empty node in product_info_list.
        MatchRule.del_product_info_by_del_list(delete_product_info_list, product_info_list)
        return result
        #--------------------------------------------------------------------
        # 待删除
        # result = u''
        # # Check product information list and record the node which should be deleted.
        # delete_product_info_list = []
        # for i in range(0, len(product_info_list)):
        #     for j in range(0, len(template_attr_val_list)):
        #         # if product_info_list[i].lower() == template_attr_val_list[j].lower():
        #         assemblyAttr_list=template_attr_val_list[j].split('|') ###
        #         if product_info_list[i].lower() == assemblyAttr_list[0].lower():###
        #             # result += product_info_list[i]
        #             result += product_info_list[i] + ('|'+assemblyAttr_list[1] if len(assemblyAttr_list)>1 else '')###
        #             delete_product_info_list.append(i)
        #             break
        # # Delete empty node in product_info_list.
        # MatchRule.del_product_info_by_del_list(delete_product_info_list, product_info_list)
        # return result
        #--------------------------------------------------------------------

    ##
    #Description: Get product info by template attribute value list.
    @staticmethod
    def command_key_word(key_word, template_attr_val_list):
        pass

    ##
    #Description: Get product info by template attribute list.
    @staticmethod
    def command_str_format(regular_ex, regular_limit, input_str):
        limit = re.I if regular_limit == 're.I' else u''
        if limit == u'':
            m = re.match(regular_ex.replace(u'[\\u2E80-\\u9FFF]', u'[\u2E80-\u9FFF]'), input_str)
        elif regular_limit == 're.I':
            m = re.match(regular_ex.replace(u'[\\u2E80-\\u9FFF]', u'[\u2E80-\u9FFF]'), input_str, limit)
        if m:
            if m.group() == input_str:
                return True
        return False

    ##
    # Description: Check whether string format :letter+number.
    @staticmethod
    def check_format_letter_number(input_str):
        m = re.match(r'([A-Z]+)(\d*)', input_str)
        if m:
            check_aggr = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789/-'
            for i in range(0, len(input_str)):
                if input_str[i] not in check_aggr:
                    return False
            return True
        return False
