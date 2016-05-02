# coding=utf-8
u"""
Description: Generate new basic template from the result and add
             it to data base.
User: Jerry.Fang
Date: 13-12-12
"""

from xlrd import open_workbook
from model.session import *
from template.match_rule import MatchRule
from template.logger import logger
from model.basic_element import BasicElement
from extractor.data_extractor import DataExtractor
from extractor.data_extractor import template_redis
from template.basic_template_generator import BasicTemplate
import copy

##
#Description: Open result file and add new template to database.


class TemplateUpdater():
    def __init__(self):
        self.input_file = u''
        self._input_file_handle = []
        pass

    # Set input file's path.
    def set_input_file(self, file_path):
        self.input_file = file_path
        logger.info('Set input result file path: %s .' % file_path)

    # Open source xls file.
    def open_xls_input_file(self):
        try:
            self._input_file_handle = open_workbook(self.input_file)
            logger.info('Open file successfully: "%s" ' % self.input_file)
        except Exception as exc:
            logger.error('Can not open file: "%s" Info: %s' % (self.input_file, exc))
            exit()

    #record old attribute rule to dictionary.
    @staticmethod
    def record_old_attr_rule_in_dic(class_id, template_dic_pool, old_attr_rule_dic):
        if class_id in template_dic_pool.keys():
            for attr_name in template_dic_pool[class_id].keys():
                for attr_val in template_dic_pool[class_id][attr_name]:
                    if u'attr_rule' in attr_val:
                        old_attr_rule_dic[attr_name] = attr_val

    # Merge strategy: if attr_val in pool, use new rule; if attr_val not in pool, keep old rule.
    @staticmethod
    def merge_old_attr_rule_with_new_attr_rule(class_id, template_dic_pool, old_attr_rule_dic):
        if class_id not in template_dic_pool.keys():
            template_dic_pool[class_id] = dict()
        for attr_name in old_attr_rule_dic.keys():
            if attr_name not in template_dic_pool[class_id].keys():
                template_dic_pool[class_id][attr_name] = []
                template_dic_pool[class_id][attr_name].append(old_attr_rule_dic[attr_name])

    # Rebuild attribute rule by class id.
    @staticmethod
    def rebuild_attr_rule_by_class_id(class_id, template_dic_pool):

        # record old attribute rule.
        old_attr_rule_dic = dict()
        TemplateUpdater.record_old_attr_rule_in_dic(class_id, template_dic_pool, old_attr_rule_dic)

        # Clean attribute rule by class id in database.
        BasicTemplate.clean_attr_rule_by_class_id(class_id)

        # Regenerate attribute rules by class id.
        del template_dic_pool[class_id]
        template_redis.delete(class_id)
        DataExtractor.find_template_pool_in_db(class_id, template_dic_pool)
        if class_id in template_dic_pool.keys():
            BasicTemplate.gen_attr_rule_in_template(template_dic_pool[class_id])

        # Merge old attr rule with new rule.
        TemplateUpdater.merge_old_attr_rule_with_new_attr_rule(class_id, template_dic_pool, old_attr_rule_dic)

        # Submit change to database.
        TemplateUpdater.submit_attr_rule_by_class_id(class_id, template_dic_pool)

    # Submit indicate attribute rule to database.
    @staticmethod
    def submit_attr_rule_by_class_id(class_id, template_dic_pool):
        if class_id in template_dic_pool.keys():
            with get_session() as session:
                for attr_name in template_dic_pool[class_id].keys():
                    for i in range(0, len(template_dic_pool[class_id][attr_name])):
                        if u'attr_rule' in template_dic_pool[class_id][attr_name][i]:
                            m_lv1_id, m_lv2_id = MatchRule.decode_class_id(class_id)
                            be = session.query(BasicElement).filter_by(lv1_id=m_lv1_id, lv2_id=m_lv2_id).first()
                            if be:
                                lv1_name = be.lv1_name
                                lv2_name = be.lv2_name
                            else:
                                lv1_name = u''
                                lv2_name = u''
                            # Divide and store attribute rule to elements list.
                            m_basic_element_list = []
                            BasicTemplate.store_attr_rule_to_ele_list(
                                template_dic_pool[class_id][attr_name][i],
                                m_lv1_id, m_lv2_id, lv1_name, lv2_name, attr_name,
                                m_basic_element_list
                            )
                            session.add_all(m_basic_element_list)
                            session.commit()

    # Generate class id <-> name map by class id.
    @staticmethod
    def gen_class_id_name_map_by_class_id(class_id, template_dic_pool, class_name_dic):
        if class_id not in class_name_dic.keys():
            class_name_dic[class_id] = []
            with get_session() as session:
                lv1_id, lv2_id = MatchRule.decode_class_id(class_id)
                if class_id in template_dic_pool.keys():
                    be = session.query(BasicElement).filter_by(lv1_id=lv1_id, lv2_id=lv2_id).first()
                    if be:
                        class_name_dic[class_id].append(be.lv1_name)
                        class_name_dic[class_id].append(be.lv2_name)
                        class_name_dic[class_id].append(False)
                    else:
                        class_name_dic[class_id].append(u'未定义一级种类')
                        class_name_dic[class_id].append(u'未定义二级种类')
                        class_name_dic[class_id].append(False)
                        logger.warning('Find a unnamed template! class id: %d' % class_id)

    # Read attribute value and insert new template to list wait for updating.
    @staticmethod
    def insert_new_element_to_update_list(
            rd_line, attr_start_idx, attr_end_idx, attr_name_list, class_name_dic,
            class_id, template_dic_pool, m_basic_element_update_list
    ):
        for attr_val_block in rd_line[attr_start_idx:attr_end_idx]:
            if u'' == attr_val_block:
                continue
            attr_val_list = attr_val_block.split(u'\t')
            for attr_val in attr_val_list:
                if u'' != attr_val:
                    # Check whether attribute is new.
                    attr_name = attr_name_list[rd_line.index(attr_val_block)]
                    is_new_basic_element = False
                    if attr_name not in template_dic_pool[class_id].keys():
                        is_new_basic_element = True
                        logger.debug('Find new attribute name: %s' % attr_name)
                    elif attr_val not in template_dic_pool[class_id][attr_name]:
                        is_new_basic_element = True
                        logger.debug('Find new attribute value: %s' % attr_val)

                    # Insert to list wait for updating.
                    if is_new_basic_element:
                        m_basic_element = BasicElement()
                        m_lv1_id, m_lv2_id = MatchRule.decode_class_id(class_id)
                        m_basic_element.lv1_id = m_lv1_id
                        m_basic_element.lv2_id = m_lv2_id
                        m_basic_element.lv1_name = class_name_dic[class_id][0]
                        m_basic_element.lv2_name = class_name_dic[class_id][1]
                        m_basic_element.attr_name = attr_name
                        m_basic_element.attr_val = attr_val
                        class_name_dic[class_id][2] = True

                        # Check whether the new element is already in the update list.
                        is_already_record = False
                        for m_record_be in m_basic_element_update_list:
                            if m_basic_element.lv1_id == m_record_be.lv1_id and \
                               m_basic_element.lv2_id == m_record_be.lv2_id and \
                               m_basic_element.attr_name == m_record_be.attr_name and \
                               m_basic_element.attr_val == m_record_be.attr_val:
                                is_already_record = True
                                break

                        # Insert to update list .
                        if False is is_already_record:
                            m_basic_element_update_list.append(m_basic_element)

    ##
    # Updater main processing.
    def update_templates(self):

        # Open file handle.
        self.open_xls_input_file()

        # Generate table names' list.
        sheet_names_list = self._input_file_handle.sheet_names()

        # Product template pool.
        template_dic_pool = {}

        # New element waite for updating.
        m_basic_element_update_list = []

        # Read all sheets by name.
        class_name_dic = {}
        for sheet_name in sheet_names_list:
            sheet_handle = self._input_file_handle.sheet_by_name(sheet_name)
            row_num = sheet_handle.nrows
            attr_start_idx = 0
            attr_end_idx = 0
            attr_name_list = []
            class_id_idx = 0

            # Read all lines.
            for rd_row_idx in range(0, row_num):

                # Read one line and replace all special words.
                rd_line = sheet_handle.row_values(rd_row_idx)
                for i in range(0, len(rd_line)):
                    rd_line[i] = rd_line[i].replace(u'  ', u'\t').replace(u'、', u'\t')
                MatchRule.replace_special_word(rd_line)

                # Get attribute name or value start index and end index.
                if 0 == rd_row_idx:
                    attr_start_idx = rd_line.index(u'解析结果')
                    logger.info('Find attribute start index = %d.' % attr_start_idx)
                    continue

                # Get attribute name list and attribute and index.
                if 1 == rd_row_idx:
                    attr_end_idx = rd_line.index(u'无法解析部分')
                    attr_name_list = rd_line[:]
                    class_id_idx = rd_line.index(u'类别编码')
                    logger.info('Find attribute end index = %d. class_id index = %d' % (attr_end_idx, class_id_idx))
                    continue

                # Find template and store in template pool.
                class_id = MatchRule.encode_class_id(int(rd_line[class_id_idx]), 0, u'xls')
                DataExtractor.find_template_pool_in_db(class_id, template_dic_pool)
                if class_id not in template_dic_pool.keys():
                    logger.info('Can not find template %s' % class_id)
                    continue

                # Generate class name <-> id map function.
                TemplateUpdater.gen_class_id_name_map_by_class_id(
                    class_id, template_dic_pool, class_name_dic
                )

                # Read attribute value and insert new template to list wait for updating.
                self.insert_new_element_to_update_list(
                    rd_line, attr_start_idx, attr_end_idx, attr_name_list, class_name_dic,
                    class_id, template_dic_pool, m_basic_element_update_list
                )

        #Update all new basic elements to database.
        with get_session() as session:
            logger.info('Add new %d elements to table.' % len(m_basic_element_update_list))
            session.add_all(m_basic_element_update_list)
            session.commit()

        # Rebuild all attribute rule by class id when flag is True.
        for class_id in class_name_dic.keys():
            if class_name_dic[class_id][2]:
                # Rebuild attribute rule by indicated class id.
                template_redis.delete(class_id)
                TemplateUpdater.rebuild_attr_rule_by_class_id(class_id, template_dic_pool)

        # Clean redis buffer.
        template_redis.flushdb()

    ##
    # Delete template by API indication.
    @staticmethod
    def del_template_by_api_ind(ind_info):

        # delete all template attribute name.
        if u'' == ind_info[u'unique_id']:
            with get_session() as session:
                be_pool = session.query(BasicElement).filter_by(
                    lv1_id=int(ind_info[u'first_type_code']),
                    lv2_id=int(ind_info[u'second_type_code']),
                    attr_name=ind_info[u'attr_name']
                )
                if be_pool.first():
                    be_pool.delete()
                    session.commit()
                    logger.info('Delete all attribute value of unique_id %s ok.' % ind_info[u'unique_id'])

        # delete indication unique template.
        else:
            with get_session() as session:
                be = session.query(BasicElement).filter_by(
                    unique_id=int(ind_info[u'unique_id'])
                ).first()
                if be:
                    session.delete(be)
                    session.commit()
                    logger.info('Delete unique_id %s ok.' % ind_info[u'unique_id'])

                    # Rebuild attribute rule by class id.
                    template_dic_pool = {}
                    class_id = MatchRule.encode_class_id(
                        int(ind_info[u'first_type_code']), int(ind_info[u'second_type_code'])
                    )
                    DataExtractor.find_template_pool_in_db(class_id, template_dic_pool)
                    if class_id in template_dic_pool.keys():
                        TemplateUpdater.rebuild_attr_rule_by_class_id(class_id, template_dic_pool)
                    logger.info('Rebuild attribute rule ok.')

        # Clean template redis.
        class_id = MatchRule.encode_class_id(int(ind_info[u'first_type_code']), int(ind_info[u'second_type_code']))
        template_redis.delete(class_id)

    ##
    # Update template by API indication.
    @staticmethod
    def update_template_by_api_ind(ind_info):

        # Check indication information.
        if ind_info[u'first_type_code'] == u''\
           or ind_info[u'second_type_code'] == u'' or ind_info[u'attr_name'] == u''\
           or ind_info[u'attr_val'] == u'':
            logger.error('indication is empty!')
            return

        # Update attribute name.
        if ind_info[u'unique_id'] == u'':
            with get_session() as session:
                be_pool = session.query(BasicElement).filter_by(
                    lv1_id=int(ind_info[u'first_type_code']),
                    lv2_id=int(ind_info[u'second_type_code']),
                    attr_name=ind_info[u'attr_name']
                ).all()
                if len(be_pool) > 0:
                    for be in be_pool:
                        be.attr_name = ind_info[u'attr_val']
                    session.commit()
                    logger.info('update attribute name %s -> %s ok.' %
                                (ind_info[u'attr_name'], ind_info[u'attr_val']))

        # Update template to database.
        else:
            with get_session() as session:
                be = session.query(BasicElement).filter_by(
                    unique_id=int(ind_info[u'unique_id'])
                ).first()
                if be:
                    be.lv1_id = int(ind_info[u'first_type_code'])
                    be.lv2_id = int(ind_info[u'second_type_code'])
                    be.attr_name = ind_info[u'attr_name']
                    be.attr_val = ind_info[u'attr_val']
                    session.commit()
                    logger.info('update unique_id %s ok.' % ind_info[u'unique_id'])

                    # Rebuild attribute rule by class id when attribute value is not attr_rule.
                    if u'attr_rule' not in ind_info[u'attr_val']:
                        template_dic_pool = {}
                        class_id = MatchRule.encode_class_id(
                            int(ind_info[u'first_type_code']), int(ind_info[u'second_type_code'])
                        )
                        DataExtractor.find_template_pool_in_db(class_id, template_dic_pool)
                        if class_id in template_dic_pool.keys():
                            TemplateUpdater.rebuild_attr_rule_by_class_id(class_id, template_dic_pool)
                        logger.info('Rebuild attribute rule ok.')

        # Clean template redis.
        class_id = MatchRule.encode_class_id(int(ind_info[u'first_type_code']), int(ind_info[u'second_type_code']))
        template_redis.delete(class_id)

    ##
    # Retrieve template information by API indication.
    @staticmethod
    def retrieve_template_by_api_ind(ind_info, all_result):

        # Check indication information.
        if ind_info[u'first_type_code'] == u'' or ind_info[u'second_type_code'] == u''\
           or ind_info[u'page'] == u'' or ind_info[u'page_size'] == u'':
            logger.error('Input is empty!')
            return

        # Calculate start index and end index.
        start_idx = (int(ind_info[u'page'])-1) * int(ind_info[u'page_size'])
        end_idx = int(ind_info[u'page']) * int(ind_info[u'page_size'])
        idx = 0

        # Retrieve all attribute name.
        if ind_info[u'attr_name'] == u'':

            # Search data from database.
            # find template.
            template_dic_pool = {}
            class_id = MatchRule.encode_class_id(int(ind_info[u'first_type_code']), int(ind_info[u'second_type_code']))
            DataExtractor.find_template_pool_in_db(class_id, template_dic_pool)
            if class_id in template_dic_pool.keys():

                # write to result buffer.
                all_result[u'total'] = len(template_dic_pool[class_id].keys())
                all_result[u'rows'][u'attr_name'] = []
                attr_name_list = template_dic_pool[class_id].keys()
                for idx in range(start_idx, end_idx):
                    if idx >= len(attr_name_list) or idx < 0:
                        break
                    else:
                        all_result[u'rows'][u'attr_name'].append(attr_name_list[idx])
                        logger.debug('Retrieve attribute name : %s' % attr_name_list[idx])
                logger.info('Retrieve %d attribute name OK!' % (idx + 1 - start_idx))

        # Retrieve attribute value.
        else:
            # Search data from database.
            with get_session() as session:
                be_pool = session.query(BasicElement).filter_by(
                    lv1_id=int(ind_info[u'first_type_code']),
                    lv2_id=int(ind_info[u'second_type_code']),
                    attr_name=ind_info[u'attr_name']
                ).all()
                if len(be_pool) > 0:

                    # Divide two list. one is without attr_rule; other is attr_rule list.
                    be_list_without_rule = []
                    be_list_rule = []
                    for be in be_pool:
                        if u'attr_rule' not in be.attr_val:
                            be_list_without_rule.append(be)
                        else:
                            be_list_rule.append(be)

                    # Write data to result buffer except attr_rule element.
                    all_result[u'total'] = len(be_list_without_rule)
                    for idx in range(start_idx, end_idx):
                        if idx >= len(be_list_without_rule) or idx < 0:
                            break
                        elif u'attr_rule' not in be_list_without_rule[idx].attr_val:
                            all_result[u'rows'][be_list_without_rule[idx].attr_val] = be_list_without_rule[idx].unique_id
                            logger.debug('Retrieve attribute value : %s, %d'
                                         % (be_list_without_rule[idx].attr_val, be_list_without_rule[idx].unique_id))

                    # Write attribute rule to result buffer.
                    all_result[u'rows'][u'attr_rule'] = []
                    for idx in range(0, len(be_list_rule)):
                        if u'attr_rule' in be_list_rule[idx].attr_val:
                            all_result[u'rows'][u'attr_rule'].append(be_list_rule[idx].attr_val)
                            all_result[u'rows'][u'attr_rule'].append(be_list_rule[idx].unique_id)
                            logger.info('Retrieve %s attribute rule OK!' % be_list_rule[idx].attr_val)

# main function.
if __name__ == '__main__':
    m_template_updater = TemplateUpdater()
    m_template_updater.set_input_file(u'../../InputFile_test/result.xls')
    m_template_updater.update_templates()
