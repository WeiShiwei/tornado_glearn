# coding=utf-8
u"""
Description: Generate basic template from xls.
             Used SQLalchemy tool.
User: Jerry.Fang
Date: 13-12-03
"""

from xlrd import open_workbook
from template.match_rule import *
from extractor.data_extractor import DataExtractor
from extractor.data_extractor import template_redis
from model.basic_element import BasicElement
from model.base_material_type import *
from model.base_material_type_attr import *
from model.base_material_type_attr_value import *
from model.base_material_type_attr_key_word import *
from model.base_material_type_attr_rule import *
from model.session import *
from template.logger import logger
from api.config import config
from sqlalchemy.orm import aliased

##
#Description: Generate basic template from xls.


class BasicTemplate:

    def __init__(self):
        pass

    # Source xls file's location.
    PRIMARY_RULE_FILE = config.RULE_FILE

    # Set primary rule file path.
    def set_primary_path(self, new_path):
        self.PRIMARY_RULE_FILE=new_path
        logger.info('Set new primary path: "%s" ' % new_path)

    #Open source xls file.
    @staticmethod
    def open_xls_file(path):
        try:
            data = open_workbook(path)
            logger.info('Open file successfully: "%s" ' % path)
            return data
        except Exception as exc:
            logger.error('Can not open file: "%s" Info: %s' % (path, exc))
            exit()

    #Generate element dictionary from read line.
    @staticmethod
    def generate_ele_dic(m_basic_element, rd_list, line_num):
        if (6 == len(rd_list)) and ('' not in rd_list):

            #Replace all the special word.
            MatchRule.replace_special_word(rd_list)

            #Set element's value.
            m_basic_element.lv1_id = rd_list[0]
            m_basic_element.lv2_id = rd_list[1]
            m_basic_element.lv1_name = rd_list[2]
            m_basic_element.lv2_name = rd_list[3]
            m_basic_element.attr_name = rd_list[4]
            #todo: customize for other types
            m_basic_element.attr_val = rd_list[5] + MatchRule.get_unit_name_from_attr_name(rd_list[4], rd_list[5]) 
            logger.debug('Read %d line OK.' % line_num)
            return True
        else:
            logger.warning('%d line with %d elements can not be processed.%s' % (line_num, len(rd_list), rd_list))
            return False

    #Report the total number of all dictionary elements.
    @staticmethod
    def report_stat_db():
        with get_session() as session:
            query = session.query(BasicElement)
            logger.debug('%d elements in the basic_element_table{}' % len(query.all()))
        return

    #Delete all elements in table.
    @staticmethod
    def clean_table():
        with get_session() as session:
            query = session.query(BasicElement)
            logger.info('%d elements is ready to be deleted....' % len(query.all()))
            query.delete()
            bmt_query = session.query(BaseMaterialType)
            logger.info('%d base_material_type is ready to be deleted....' % len(bmt_query.all()))
            bmt_query.delete()
            bmta_query = session.query(BaseMaterialTypeAttr)
            logger.info('%d base_material_type_attr is ready to be deleted....' % len(bmta_query.all()))
            bmta_query.delete()
            bmtav_query = session.query(BaseMaterialTypeAttrValue)
            logger.info('%d base_material_type_attr_value is ready to be deleted....' % len(bmtav_query.all()))
            bmtav_query.delete()
            bmtarr_query = session.query(BaseMaterialTypeAttrRule)
            logger.info('%d base_material_type_attr_rule is ready to be deleted....' % len(bmtarr_query.all()))
            bmtarr_query.delete()
            bmtarkw_query = session.query(BaseMaterialTypeAttrKeyWord)
            logger.info('%d base_material_type_attr_key_word is ready to be deleted....' % len(bmtarkw_query.all()))
            bmtarkw_query.delete()
            session.commit()
            logger.info('Delete ok.')

    ##
    #Description: Initial basic template from the primary file.
    def generate_basic_template(self):

        #Open source file.
        data = self.open_xls_file(self.PRIMARY_RULE_FILE)

        #Get the first table and max row number.
        table = data.sheet_by_index(0)
        row_num = table.nrows
        logger.info('Get table with %d lines ok.' % row_num)

        #Read all the lines. Ignore the 1st title line.
        logger.info('Start to initial Basic Template....')
        m_basic_element_dic = {}
        m_max_num_in_m_basic_element_dic = 10000
        top_base_material_types = []
        for i in range(1, row_num):
            print i
            #Generate basic elements class.
            m_basic_element = BasicElement()
            base_material_type = BaseMaterialType()
            child = BaseMaterialType()
            base_material_type_attr = BaseMaterialTypeAttr()
            base_material_type_attr_value = BaseMaterialTypeAttrValue()
            #Add element to dictionary.
            if True is self.generate_ele_dic(m_basic_element, table.row_values(i), i):
                m_basic_element_dic[i] = m_basic_element
                
                base_material_type.code = m_basic_element.lv1_id
                base_material_type.description = m_basic_element.lv1_name
                
                child.code = m_basic_element.lv2_id
                child.description = m_basic_element.lv2_name
                
                base_material_type_attr.description = m_basic_element.attr_name
                base_material_type_attr_value.description = m_basic_element.attr_val
                
                ### def is_array_members(array_list, item):
                index = self.is_array_members(top_base_material_types, base_material_type)
                if -1 != index:
                    base_material_type = top_base_material_types[index]
                else:
                    top_base_material_types.append(base_material_type)
                
                children_index = self.is_array_members(base_material_type.children, child)
                if -1 != children_index:
                    child = base_material_type.children[children_index]
                else:
                    base_material_type.children.append(child)
                
                attr_index = self.is_array_members(child.base_material_type_attrs, base_material_type_attr)
                if -1 != attr_index:
                    base_material_type_attr = child.base_material_type_attrs[attr_index]
                else:
                    child.base_material_type_attrs.append(base_material_type_attr)
                
                value_index = self.is_array_members(base_material_type_attr.base_material_type_attr_values, base_material_type_attr_value)
                if -1 != value_index:
                    base_material_type_attr_value = base_material_type_attr.base_material_type_attr_values[attr_index]
                else:
                    base_material_type_attr.base_material_type_attr_values.append(base_material_type_attr_value)
            else:
                del m_basic_element
            #Update to data base when dictionary is full or it is the last loop.
        #commit change and clean dictionary.
        with get_session() as session:
             logger.info('Add new %d elements to table.' % len(m_basic_element_dic))
             # session.add_all(m_basic_element_dic.values())
             session.add_all(top_base_material_types)
             session.commit()
             m_basic_element_dic.clear()

        # Clean all templates in redis.
        template_redis.flushdb()
        logger.info('Initial Basic Template OK!')
        return

    #Description: Check element in attribute pool.
    @staticmethod
    def check_ele_in_attr_pool(attr_pool, m_basic_element, default_ind, m_match_rule, door_sill_rate):
        is_ele_found = default_ind
        if 0 < len(attr_pool):
            for k in range(0, len(attr_pool)):
                if (attr_pool[k].attr_name in m_basic_element.attr_name) or \
                        (m_basic_element.attr_name in attr_pool[k].attr_name):
                    is_ele_found = True
                    logger.debug('Similar Element is in the DataBase. ')
                    logger.debug('DB element: [%s, %s, %s, %s, %s]' % 
                                (attr_pool[k].lv1_id, attr_pool[k].lv2_id, attr_pool[k].lv1_name,
                                 attr_pool[k].lv2_name, attr_pool[k].attr_name))
                    logger.debug('CSV element:[%s, %s, %s, %s, %s]' % 
                                (m_basic_element.lv1_id, m_basic_element.lv2_id, m_basic_element.lv1_name,
                                 m_basic_element.lv2_name, m_basic_element.attr_name))
                    break
                elif (door_sill_rate <= m_match_rule.calc_str_match_rate(attr_pool[k].attr_name,
                                                                         m_basic_element.attr_name)) or \
                     (door_sill_rate <= m_match_rule.calc_str_match_rate(m_basic_element.attr_name,
                                                                         attr_pool[k].attr_name)):
                    is_ele_found = True
                    logger.debug('Similar Element (>%d%%) is in the DataBase. ' % door_sill_rate)
                    logger.debug('DB element: [%s, %s, %s, %s, %s]' %
                                 (attr_pool[k].lv1_id, attr_pool[k].lv2_id, attr_pool[k].lv1_name,
                                  attr_pool[k].lv2_name, attr_pool[k].attr_name))
                    logger.debug('CSV element:[%s, %s, %s, %s, %s]' %
                                 (m_basic_element.lv1_id, m_basic_element.lv2_id, m_basic_element.lv1_name,
                                  m_basic_element.lv2_name, m_basic_element.attr_name))
                    break
        return is_ele_found

    # Generate regular expression in template dictionary
    @staticmethod
    def gen_attr_rule_in_template(template_attr_dic):
        for attr_name, attr_list in template_attr_dic.iteritems():
            attr_rule_index = -1
            # Find rule's position in list and clean it.
            for n in range(0, len(attr_list)):
                if u'attr_rule' in attr_list[n]:
                    logger.info('Clean old %s.' % attr_list[n])
                    attr_list[n] = u''
                    attr_rule_index = n
                    break
            # if here is not rule, then create a new node.
            if -1 == attr_rule_index:
                attr_list.append(u'')
                attr_rule_index = len(attr_list)-1
                logger.debug('Create new attr_rule.')
            # Generate attribute rule.
            MatchRule.gen_attr_rule_by_val(attr_name, attr_list, attr_rule_index)

    # store attribute rule to element list.
    @staticmethod
    def store_attr_rule_to_ele_list(attr_rule_info, base_material_type, attr_name, str_rule_list, key_word_list):
        # Divide attribute rule to list.
        attr_rule_list = attr_rule_info.split(u'-')
        for attr_rule_ele in attr_rule_list:
            if u'str_format' in attr_rule_ele:
                with get_session() as session:
                    be = session.query(BaseMaterialTypeAttr).filter_by(base_material_type_id=base_material_type.id, description=attr_name).first()
                    if be:
                       for i in attr_rule_ele.split(u';'):
                          if u'' != i and u'str_format' != i:
                             str_rule = BaseMaterialTypeAttrRule()
                             str_rule.base_material_type_attr_id = be.id
                             str_rule.rule_description = i
                             str_rule_list.append(str_rule)
            if u'key_word' in attr_rule_ele:
                with get_session() as session:
                    be = session.query(BaseMaterialTypeAttr).filter_by(base_material_type_id=base_material_type.id, description=attr_name).first()
                    if be:
                       for i in attr_rule_ele.split(u';'):
                          if u'' != i and u'key_word' != i:
                             key_word = BaseMaterialTypeAttrKeyWord()
                             key_word.base_material_type_attr_id = be.id
                             key_word.key_words = i
                             key_word_list.append(key_word)
                logger.debug('Insert new element to element pool! [%s, %s, %s, %s, %s]' %
                            (base_material_type.parent.code, base_material_type.code,
                             base_material_type.parent.description,
                             base_material_type.description, attr_name))

    # Submit all attr_rule to database.
    @staticmethod
    def submit_all_attr_rule_to_database(template_dic_pool):
        parent_bmt = aliased(BaseMaterialType)
        with get_session() as session:
            rule_list = []
            key_word_list = []
            for class_id in template_dic_pool.keys():
                for attr_name in template_dic_pool[class_id].keys():
                    for i in range(0, len(template_dic_pool[class_id][attr_name])):
                        if u'attr_rule' in template_dic_pool[class_id][attr_name][i]:
                            m_lv1_id, m_lv2_id = MatchRule.decode_class_id(class_id)
                            # be = session.query(BasicElement).filter_by(lv1_id=m_lv1_id, lv2_id=m_lv2_id).first()
                            be = session.query(BaseMaterialType, parent_bmt).join((parent_bmt, parent_bmt.id == BaseMaterialType.parent_id))\
                            .filter(BaseMaterialType.code == m_lv2_id, parent_bmt.code == m_lv1_id).first()
                            if be:
                                # Divide and store attribute rule to elements list.
                                BasicTemplate.store_attr_rule_to_ele_list(
                                    template_dic_pool[class_id][attr_name][i],
                                    be[0], attr_name,
                                    rule_list, key_word_list
                                )
            logger.info('Add new %d elements to table.' % (len(rule_list) + len(key_word_list)))
            session.add_all(rule_list)
            session.add_all(key_word_list)
            session.commit()

    # Clean attr_rule by class_id.
    @staticmethod
    def clean_attr_rule_by_class_id(class_id):
        parent_bmt = aliased(BaseMaterialType)
        m_lv1_id, m_lv2_id = MatchRule.decode_class_id(class_id)
        with get_session() as session:
            be = session.query(BaseMaterialType, parent_bmt).join((parent_bmt, parent_bmt.id == BaseMaterialType.parent_id))\
            .filter(BaseMaterialType.code == m_lv2_id, parent_bmt.code == m_lv1_id).first()
            if be:
                for attr in be[0].base_material_type_attrs:
                   session.query(BaseMaterialTypeAttrRule).filter(BaseMaterialTypeAttrRule.base_material_type_attr_id == attr.id).delete()
                   session.query(BaseMaterialTypeAttrKeyWord).filter(BaseMaterialTypeAttrKeyWord.base_material_type_attr_id == attr.id).delete()
                   session.commit()

    ##
    # Generate regular expression in all basic template .
    def gen_attr_rule_in_all_basic_template(self):
        logger.info('Start generate all basic template attribute rule...')

        # Find all basic template and store them to the pool.
        template_dic_pool = {}
        class_id_list = []
        DataExtractor.gen_class_id_list(class_id_list)
        for class_id in class_id_list:
            DataExtractor.find_template_pool_in_db(class_id, template_dic_pool)
        # Generate attribute rule under one basic template.
        for class_id in template_dic_pool.keys():
            self.gen_attr_rule_in_template(template_dic_pool[class_id])
        # Clean all attr_rule.
        for class_id in template_dic_pool.keys():
            self.clean_attr_rule_by_class_id(class_id)
        # Submit all attribute rule .
                
        self.submit_all_attr_rule_to_database(template_dic_pool)
        # Clean all templates in redis.
        template_redis.flushdb()
        logger.info('Generate all basic template attribute rule OK.')

    ##
    # Log all template to log file.
    @staticmethod
    def log_all_template(start=u'00#00', stop=u'99#99'):
        template_dic_pool = {}
        lv1_start, lv2_start = MatchRule.decode_class_id(start)
        lv1_stop, lv2_stop = MatchRule.decode_class_id(stop)
        for lv1_id in range(lv1_start, lv1_stop):
            for lv2_id in range(lv2_start, lv2_stop):
                class_id = MatchRule.encode_class_id(lv1_id, lv2_id)
                DataExtractor.find_template_pool_in_db(class_id, template_dic_pool)

    ##
    # Check the indication list and delete invalid node.
    @staticmethod
    def check_new_template_ind_list(indication_list):
        template_total_num = len(indication_list)
        # Check whether indication is right.
        for i in range(template_total_num-1, -1, -1):
            if u'first_type_code' not in indication_list[i].keys() or \
               u'second_type_code' not in indication_list[i].keys() or \
               u'first_type_name' not in indication_list[i].keys() or \
               u'second_type_name' not in indication_list[i].keys() or \
               u'attr_name' not in indication_list[i].keys() or \
               u'attr_val' not in indication_list[i].keys():
                logger.error('Wrong template keys: %s' % indication_list[i])
                del indication_list[i]
                continue
            if indication_list[i][u'first_type_code'] == '' or \
               indication_list[i][u'second_type_code'] == '':
                logger.error('Wrong template lv id: %d, %d.' %
                             (indication_list[i]['first_type_code'], indication_list[i]['second_type_code']))
                del indication_list[i]
                continue
            if u'attr_rule' in indication_list[i][u'attr_val']:
                del indication_list[i]
                continue

    ##weishiwei
    # Create new template by indication list.
    @staticmethod
    def create_new_template_by_ind_list(indication_list):

        # Get total template number.
        template_total_num = len(indication_list)
        logger.debug('Get %d template to add.' % template_total_num)

        ###------------------------------------------------------------------
        # import pdb;pdb.set_trace()
        # (Pdb) type(indication_list[0]) <type 'dict'>
        # [{u'attr_name': u'\u6d4b\u8bd5\u7c7battr_name1(mm2)', u'second_type_code': u'88', u'attr_val': u'15mm2', u'first_type_name': u'\u6d4b\u8bd5\u7c7blv1', u'second_type_name': u'\u6d4b\u8bd5\u7c7blv2', u'first_type_code': u'99'}, {u'attr_name': u'\u6d4b\u8bd5\u7c7battr_name2(mm2)', u'second_type_code': u'88', u'attr_val': u'16', u'first_type_name': u'\u6d4b\u8bd5\u7c7blv1', u'second_type_name': u'\u6d4b\u8bd5\u7c7blv2', u'first_type_code': u'99'}]
        #------------------------------------------------------------------

        # Add new templates to add-list.
        m_basic_element = BasicElement()
        m_basic_element_list = []
        for i in range(0, template_total_num):
            #Add element to dictionary.
            BasicTemplate.generate_ele_dic(
                m_basic_element,
                [
                    indication_list[i][u'first_type_code'],
                    indication_list[i][u'second_type_code'],
                    indication_list[i][u'first_type_name'],
                    indication_list[i][u'second_type_name'],
                    indication_list[i][u'attr_name'],
                    indication_list[i][u'attr_val']
                ],
                0)
            BasicTemplate.create_basic_data(m_basic_element.lv1_id, m_basic_element.lv1_name, m_basic_element.lv2_id, m_basic_element.lv2_name, m_basic_element.attr_name, m_basic_element.attr_val)
            # Clean template redis.
            class_id = MatchRule.encode_class_id(indication_list[i][u'first_type_code'], indication_list[i][u'second_type_code'])
            template_redis.delete(class_id)
        logger.info('Add all templates successfully!')
        return True

    ##
    # 将excle数据导入数据库
    @staticmethod
    def is_array_members(array_list, item):
        index = -1
        for i in array_list:
            if i == item:
                index = array_list.index(i)
                break
        return index

    ##
    # Rebuild attribute rule by indication list.
    @staticmethod
    def gen_attr_rule_by_ind_list(indication_list):

        # Find all basic template and store them to the pool.
        template_dic_pool = {}
        for i in range(0, len(indication_list)):
            class_id = MatchRule.encode_class_id(
                indication_list[i][u'first_type_code'],
                indication_list[i][u'second_type_code']
            )
            DataExtractor.find_template_pool_in_db(class_id, template_dic_pool)

        # Generate attribute rule under one basic template.
        for class_id in template_dic_pool.keys():
            BasicTemplate.gen_attr_rule_in_template(template_dic_pool[class_id])

        # Clean all attr_rule.
        for class_id in template_dic_pool.keys():
            BasicTemplate.clean_attr_rule_by_class_id(class_id)

        # Clean template redis.
        for class_id in template_dic_pool.keys():
            template_redis.delete(class_id)

        # Submit all attribute rule .
        BasicTemplate.submit_all_attr_rule_to_database(template_dic_pool)
        logger.info('Regenerate new template attribute rule OK.')

    @staticmethod
    def create_basic_data(first_code, first_name, second_code, second_name, attr, value):
        parent_bmt = aliased(BaseMaterialType)
        with get_session() as session:
             be = session.query(BaseMaterialType, parent_bmt).join((parent_bmt, parent_bmt.id == BaseMaterialType.parent_id))\
                    .filter(BaseMaterialType.code == second_code, parent_bmt.code == first_code).first()
             
             if be: ###若表base_material_types中存在first_code,second_code
                is_new_attr = True
                is_new_value = True
                bmt_attr_id = 0
                for bmt_attr in be[0].base_material_type_attrs:
                    if bmt_attr.description == attr:
                       is_new_attr = False
                       bmt_attr_id = bmt_attr.id
                    for bmt_value in bmt_attr.base_material_type_attr_values:
                        if bmt_value.description == value:
                           is_new_value = False
                if True is is_new_attr:
                   base_material_type_attr = BaseMaterialTypeAttr(description=attr, base_material_type_id=be[0].id)
                   base_material_type_attr_value = BaseMaterialTypeAttrValue(description=value)
                   base_material_type_attr.base_material_type_attr_values.append(base_material_type_attr_value)
                   session.add(base_material_type_attr)
                   session.commit()
                elif False is is_new_attr and True is is_new_value:
                   base_material_type_attr_value = BaseMaterialTypeAttrValue(description=value, base_material_type_attr_id=bmt_attr_id)
                   session.add(base_material_type_attr_value)
                   session.commit()
             else:
                ### 感觉把好多东西杂糅在了一起,是理解的角度不对吗
                base_material_type = BaseMaterialType(code=first_code, description=first_name)
                child = BaseMaterialType(code=second_code, description=second_name)
                base_material_type_attr = BaseMaterialTypeAttr(description=attr)
                base_material_type_attr_value = BaseMaterialTypeAttrValue(description=value)
                
                base_material_type_attr.base_material_type_attr_values.append(base_material_type_attr_value)
                child.base_material_type_attrs.append(base_material_type_attr)
                base_material_type.children.append(child)
                
                session.add(base_material_type)
                session.commit()

# Main function  .
if __name__ == '__main__':

    #Generate basic template object.
    mBasicTemplate = BasicTemplate()
    mBasicTemplate.clean_table()
    mBasicTemplate.generate_basic_template()
    mBasicTemplate.gen_attr_rule_in_all_basic_template()
    #mBasicTemplate.log_all_template(u'25#00', u'26#00')
