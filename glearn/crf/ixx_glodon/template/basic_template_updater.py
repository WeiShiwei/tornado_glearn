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
from model.base_material_type import *
from model.base_material_type_attr import *
from model.base_material_type_attr_value import *
from model.base_material_type_attr_key_word import *
from model.base_material_type_attr_rule import *
from sqlalchemy.orm import aliased
from sqlalchemy import func

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
            parent_bmt = aliased(BaseMaterialType)
            with get_session() as session:
                rule_list = []
                key_word_list = []
                for attr_name in template_dic_pool[class_id].keys():
                    for i in range(0, len(template_dic_pool[class_id][attr_name])):
                        if u'attr_rule' in template_dic_pool[class_id][attr_name][i]:
                            m_lv1_id, m_lv2_id = MatchRule.decode_class_id(class_id)
                            be = session.query(BaseMaterialType, parent_bmt).join((parent_bmt, parent_bmt.id == BaseMaterialType.parent_id))\
                            .filter(BaseMaterialType.code == m_lv2_id, parent_bmt.code == m_lv1_id).first()
                            # Divide and store attribute rule to elements list.
                            m_basic_element_list = []
                            BasicTemplate.store_attr_rule_to_ele_list(
                                template_dic_pool[class_id][attr_name][i],
                                be[0], attr_name,
                                rule_list, key_word_list
                            )
                            session.add_all(rule_list)
                            session.add_all(key_word_list)
                            session.commit()

    # Generate class id <-> name map by class id.
    @staticmethod
    def gen_class_id_name_map_by_class_id(class_id, template_dic_pool, class_name_dic):
        if class_id not in class_name_dic.keys():
            parent_bmt = aliased(BaseMaterialType)
            class_name_dic[class_id] = []
            with get_session() as session:
                lv1_id, lv2_id = MatchRule.decode_class_id(class_id)
                if class_id in template_dic_pool.keys():
                    be = session.query(BaseMaterialType, parent_bmt).join((parent_bmt, parent_bmt.id == BaseMaterialType.parent_id))\
                    .filter(BaseMaterialType.code == lv2_id, parent_bmt.code == lv1_id).first()
                    if be:
                        class_name_dic[class_id].append(be[1].description)
                        class_name_dic[class_id].append(be[0].description)
                        class_name_dic[class_id].append(False)
                    else:
                        class_name_dic[class_id].append(u'未定义一级种类')
                        class_name_dic[class_id].append(u'未定义二级种类')
                        class_name_dic[class_id].append(False)
                        logger.warning('Find a unnamed template! class id: %s' % class_id)

    # Read attribute value and insert new template to list wait for updating.
    @staticmethod
    def insert_new_element_to_update_list(
            rd_line, attr_start_idx, attr_end_idx, attr_name_list, class_name_dic,
            class_id, template_dic_pool, base_material_type_attr_list, base_material_type_attr_value_list 
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
                    base_material_type_attr = BaseMaterialTypeAttr()
                    base_material_type_attr_value = BaseMaterialTypeAttrValue()
                    m_lv1_id, m_lv2_id = MatchRule.decode_class_id(class_id)
                    parent_bmt = aliased(BaseMaterialType)
                    with get_session() as session:
                         be = session.query(BaseMaterialType, parent_bmt).join((parent_bmt, parent_bmt.id == BaseMaterialType.parent_id))\
                         .filter(BaseMaterialType.code == m_lv2_id, parent_bmt.code == m_lv1_id).first()
                         if attr_name not in template_dic_pool[class_id].keys():
                            base_material_type_attr.base_material_type_id = be[0].id
                            base_material_type_attr.description = attr_name
                            base_material_type_attr_value.description = attr_val
                            base_material_type_attr.base_material_type_attr_values.append(base_material_type_attr_value)
                            is_already_new_attr = True
                            is_already_new_attr_value = True
                            for attr in base_material_type_attr_list:
                                if attr.base_material_type_id == base_material_type_attr.base_material_type_id and \
                                attr.description == base_material_type_attr.description:
                                   is_already_new_attr = False
                                   for attr_value in attr.base_material_type_attr_values:
                                       if attr_value.description == base_material_type_attr_value.description:
                                          is_already_new_attr_value = False
                                   if True is is_already_new_attr_value:
                                      attr.base_material_type_attr_values.append(base_material_type_attr_value)
                            if True is is_already_new_attr:
                               base_material_type_attr_list.append(base_material_type_attr)
                               class_name_dic[class_id][2] = True
                            logger.debug('Find new attribute name: %s' % attr_name)
                         elif attr_val not in template_dic_pool[class_id][attr_name]:
                             for attr in be[0].base_material_type_attrs:
                                 if attr.description == attr_name:
                                    base_material_type_attr_value.base_material_type_attr_id = attr.id
                                    base_material_type_attr_value.description = attr_val
                                    template_dic_pool[class_id][attr_name].append(attr_val)
                                    base_material_type_attr_value_list.append(base_material_type_attr_value)
                                    class_name_dic[class_id][2] = True
                             is_new_basic_element = True
                             logger.debug('Find new attribute value: %s' % attr_val)

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
        base_material_type_attr_list = []
        base_material_type_attr_value_list = []
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
                class_id = MatchRule.encode_class_id(rd_line[class_id_idx], 0, u'xls')
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
                    class_id, template_dic_pool, base_material_type_attr_list, base_material_type_attr_value_list
                )

        #Update all new basic elements to database.
        with get_session() as session:
            logger.info('Add new %d elements attr to table.' % len(base_material_type_attr_list))
            logger.info('Add new %d elements exits attr_value to table.' % len(base_material_type_attr_value_list))
            session.add_all(base_material_type_attr_list)
            session.add_all(base_material_type_attr_value_list)
            session.commit()

        # Rebuild all attribute rule by class id when flag is True.
        for class_id in class_name_dic.keys():
            if class_name_dic[class_id][2]:
                # Rebuild attribute rule by indicated class id.
                template_redis.delete(class_id)
                template_dic_pool = {}
                DataExtractor.find_template_pool_in_db(class_id, template_dic_pool)
                TemplateUpdater.rebuild_attr_rule_by_class_id(class_id, template_dic_pool)

        # Clean redis buffer.
        template_redis.flushdb()

    ##
    # Delete template by API indication.
    @staticmethod
    def del_template_by_api_ind(ind_info):
        # delete all template attribute name.
        if u'' == ind_info[u'unique_id']:
            parent_bmt = aliased(BaseMaterialType)
            with get_session() as session:
                be = session.query(BaseMaterialType, parent_bmt, BaseMaterialTypeAttr).join((parent_bmt, parent_bmt.id == BaseMaterialType.parent_id)).join(BaseMaterialType.base_material_type_attrs)\
                .filter(BaseMaterialType.code == ind_info[u'second_type_code'], parent_bmt.code == ind_info[u'first_type_code'], BaseMaterialTypeAttr.description==ind_info[u'attr_name']).all()
                if 0 < len(be):
                    session.query(BaseMaterialTypeAttrValue).filter(BaseMaterialTypeAttrValue.base_material_type_attr_id == be[0][2].id).delete()
                    session.query(BaseMaterialTypeAttrRule).filter(BaseMaterialTypeAttrRule.base_material_type_attr_id == be[0][2].id).delete()
                    session.query(BaseMaterialTypeAttrKeyWord).filter(BaseMaterialTypeAttrKeyWord.base_material_type_attr_id == be[0][2].id).delete()
                    session.query(BaseMaterialTypeAttr).filter(BaseMaterialTypeAttr.id == be[0][2].id).delete()
                    session.commit()
                    logger.info('Delete all attribute value of unique_id %s ok.' % ind_info[u'unique_id'])

        # delete indication unique template.
        else:
            with get_session() as session:
                be = session.query(BaseMaterialTypeAttrValue).filter_by(
                    id=int(ind_info[u'unique_id'])
                ).first()
                if be:
                    session.delete(be)
                    session.commit()
                    logger.info('Delete unique_id %s ok.' % ind_info[u'unique_id'])

                    # Rebuild attribute rule by class id.
                    template_dic_pool = {}
                    class_id = MatchRule.encode_class_id(
                        ind_info[u'first_type_code'], ind_info[u'second_type_code']
                    )
                    DataExtractor.find_template_pool_in_db(class_id, template_dic_pool)
                    if class_id in template_dic_pool.keys():
                        TemplateUpdater.rebuild_attr_rule_by_class_id(class_id, template_dic_pool)
                    logger.info('Rebuild attribute rule ok.')

        # Clean template redis.
        class_id = MatchRule.encode_class_id(ind_info[u'first_type_code'], ind_info[u'second_type_code'])
        template_redis.delete(class_id)

    ##
    # Update template by API indication.
    @staticmethod
    def update_template_by_api_ind(ind_info):
        parent_bmt = aliased(BaseMaterialType)
        # Check indication information.
        if ind_info[u'first_type_code'] == u''\
           or ind_info[u'second_type_code'] == u'' or ind_info[u'attr_name'] == u''\
           or ind_info[u'attr_val'] == u'':
            logger.error('indication is empty!')
            return

        # Update attribute name.
        if ind_info[u'unique_id'] == u'':
            with get_session() as session:
                be = session.query(BaseMaterialType, parent_bmt, BaseMaterialTypeAttr).join((parent_bmt, parent_bmt.id == BaseMaterialType.parent_id)).join(BaseMaterialType.base_material_type_attrs)\
                .filter(BaseMaterialType.code == ind_info[u'second_type_code'], parent_bmt.code == ind_info[u'first_type_code'], BaseMaterialTypeAttr.description==ind_info[u'attr_name']).all()
                if len(be) > 0:
                    be[0][2].description = ind_info[u'attr_val']
                    session.commit()
                    logger.info('update attribute name %s -> %s ok.' %
                                (ind_info[u'attr_name'], ind_info[u'attr_val']))

        # Update template to database.
        else:
            with get_session() as session:
                be = session.query(BaseMaterialTypeAttrValue).filter_by(id=int(ind_info[u'unique_id'])).first()
                if be:
                    be.description = ind_info[u'attr_val']
                    session.commit()
                    logger.info('update unique_id %s ok.' % ind_info[u'unique_id'])

                    # Rebuild attribute rule by class id when attribute value is not attr_rule.
                if u'attr_rule' not in ind_info[u'attr_val']:
                   template_dic_pool = {}
                   class_id = MatchRule.encode_class_id(
                      ind_info[u'first_type_code'], ind_info[u'second_type_code']
                   )
                   DataExtractor.find_template_pool_in_db(class_id, template_dic_pool)
                   if class_id in template_dic_pool.keys():
                       TemplateUpdater.rebuild_attr_rule_by_class_id(class_id, template_dic_pool)
                   logger.info('Rebuild attribute rule ok.')

        # Clean template redis.
        class_id = MatchRule.encode_class_id(ind_info[u'first_type_code'], ind_info[u'second_type_code'])
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
            class_id = MatchRule.encode_class_id(ind_info[u'first_type_code'], ind_info[u'second_type_code'])
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
            parent_bmt = aliased(BaseMaterialType)
            with get_session() as session:
                be = session.query(BaseMaterialType, parent_bmt, BaseMaterialTypeAttr).join((parent_bmt, parent_bmt.id == BaseMaterialType.parent_id)).join(BaseMaterialType.base_material_type_attrs)\
	            .filter(BaseMaterialType.code == ind_info[u'second_type_code'], parent_bmt.code == ind_info[u'first_type_code'], BaseMaterialTypeAttr.description==ind_info[u'attr_name']).all()
                if len(be) > 0:

                    # Divide two list. one is without attr_rule; other is attr_rule list.
                    be_list_without_rule = []
                    be_list_rule = []
                    rules = u'-attr_rule;-str_format;'
                    key_words = u'-attr_rule;-key_word;'
                    all_value = u'-attr_rule;-all_value;'
                    for attr_value in be[0][2].base_material_type_attr_values:
                        be_list_without_rule.append(attr_value)
                    for attr_rule in be[0][2].base_material_type_attr_rules:
                        rules += (attr_rule.rule_description + ';')
                    for attr_key_word in be[0][2].base_material_type_attr_key_words:
                        key_words += (attr_key_word.key_words + ';')
                    be_list_rule.append(all_value)
                    if u'-attr_rule;key_word;' != key_words:
                       be_list_rule.append(key_words)
                    if u'-attr_rule;-str_format;' != rules:
                       be_list_rule.append(rules)
                    # Write data to result buffer except attr_rule element.
                    all_result[u'total'] = len(be_list_without_rule)
                    for idx in range(start_idx, end_idx):
                        if idx >= len(be_list_without_rule) or idx < 0:
                            break
                        elif u'attr_rule' not in be_list_without_rule[idx].description:
                            all_result[u'rows'][be_list_without_rule[idx].description] = be_list_without_rule[idx].id
                            logger.debug('Retrieve attribute value : %s, %d'
                                         % (be_list_without_rule[idx].description, be_list_without_rule[idx].id))

                    # Write attribute rule to result buffer.
                    all_result[u'rows'][u'attr_rule'] = []
                    for idx in range(0, len(be_list_rule)):
                        if u'attr_rule' in be_list_rule[idx]:
                            all_result[u'rows'][u'attr_rule'].append(be_list_rule[idx])
                            all_result[u'rows'][u'attr_rule'].append(0)
                            logger.info('Retrieve %s attribute rule OK!' % be_list_rule[idx])

    ##
    # Retrieve template attrs information by API indication.
    @staticmethod
    def retrieve_template_attr_by_api_ind(ind_info):
        parent_bmt = aliased(BaseMaterialType)
        result = {}
        result[u'total'] = 0
        result[u'rows'] = []
        with get_session() as session:
            be = session.query(BaseMaterialType, func.count(BaseMaterialTypeAttr.id)).join((parent_bmt, parent_bmt.id == BaseMaterialType.parent_id)).join(BaseMaterialType.base_material_type_attrs)\
            .filter(BaseMaterialType.code == ind_info[u'second_type_code'], parent_bmt.code == ind_info[u'first_type_code']).all()
            if 0 < be[0][1]:
               start_num = (int(ind_info[u'page']) - 1) * int(ind_info[u'page_size'])
               be_1 = session.query(BaseMaterialType, parent_bmt, BaseMaterialTypeAttr).join((parent_bmt, parent_bmt.id == BaseMaterialType.parent_id)).join(BaseMaterialType.base_material_type_attrs)\
               .filter(BaseMaterialType.code == ind_info[u'second_type_code'], parent_bmt.code == ind_info[u'first_type_code']).limit(int(ind_info[u'page_size'])).offset(start_num).all()
               result[u'total'] = be[0][1]
               for attr in be_1:
                   result[u'rows'].append({u'id': attr[2].id, u'attr_name': attr[2].description})
        return result

    ##
    # Retrieve template attr values information by API indication.
    @staticmethod
    def retrieve_template_attr_value_by_api_ind(ind_info):
        result = {}
        result[u'total'] = 0
        result[u'rows'] = []
        with get_session() as session:
             be = session.query(func.count(BaseMaterialTypeAttrValue.id)).filter(BaseMaterialTypeAttrValue.base_material_type_attr_id == ind_info[u'base_material_type_attr_id']).all()
             if 0 < be[0][0]:
                start_num = (int(ind_info[u'page']) - 1) * int(ind_info[u'page_size'])
                be_1 = session.query(BaseMaterialTypeAttrValue).filter(BaseMaterialTypeAttrValue.base_material_type_attr_id == ind_info[u'base_material_type_attr_id']).limit(int(ind_info[u'page_size'])).offset(start_num).all()
                result[u'total'] = be[0][0]
                for attr_value in be_1:
                   result[u'rows'].append({u'id': attr_value.id, u'attr_value': attr_value.description})
        return result

    ##
    # Retrieve template attr rules information by API indication.
    @staticmethod
    def retrieve_template_attr_rule_by_api_ind(ind_info):
        result = {}
        result[u'total'] = 0
        result[u'rows'] = []
        with get_session() as session:
             be = session.query(func.count(BaseMaterialTypeAttrRule.id)).filter(BaseMaterialTypeAttrRule.base_material_type_attr_id == ind_info[u'base_material_type_attr_id']).all()
             if 0 < be[0][0]:
                start_num = (int(ind_info[u'page']) - 1) * int(ind_info[u'page_size'])
                be_1 = session.query(BaseMaterialTypeAttrRule).filter(BaseMaterialTypeAttrRule.base_material_type_attr_id == ind_info[u'base_material_type_attr_id']).limit(int(ind_info[u'page_size'])).offset(start_num).all()
                result[u'total'] = be[0][0]
                for attr_rule in be_1:
                   result[u'rows'].append({u'id': attr_rule.id, u'attr_rule': attr_rule.rule_description})
        return result

    ##
    # Retrieve template attr rules information by API indication.
    @staticmethod
    def retrieve_template_attr_key_word_by_api_ind(ind_info):
        result = {}
        result[u'total'] = 0
        result[u'rows'] = []
        with get_session() as session:
             be = session.query(func.count(BaseMaterialTypeAttrKeyWord.id)).filter(BaseMaterialTypeAttrKeyWord.base_material_type_attr_id == ind_info[u'base_material_type_attr_id']).all()
             if 0 < be[0][0]:
                start_num = (int(ind_info[u'page']) - 1) * int(ind_info[u'page_size'])
                be_1 = session.query(BaseMaterialTypeAttrKeyWord).filter(BaseMaterialTypeAttrKeyWord.base_material_type_attr_id == ind_info[u'base_material_type_attr_id']).limit(int(ind_info[u'page_size'])).offset(start_num).all()
                result[u'total'] = be[0][0]
                for key_word in be_1:
                   result[u'rows'].append({u'id': key_word.id, u'key_word': key_word.key_words})
        return result

    ##
    # delete template attr information by API indication.
    @staticmethod
    def del_template_attr(ind_info):
        with get_session() as session:
             be = session.query(BaseMaterialTypeAttr).filter(BaseMaterialTypeAttr.id == ind_info[u'base_material_type_attr_id']).first()
             if be:
               class_id = MatchRule.encode_class_id(be.base_material_type.parent.code, be.base_material_type.code)
               template_redis.delete(class_id)
               session.query(BaseMaterialTypeAttrValue).filter(BaseMaterialTypeAttrValue.base_material_type_attr_id == ind_info[u'base_material_type_attr_id']).delete()
               session.query(BaseMaterialTypeAttrRule).filter(BaseMaterialTypeAttrRule.base_material_type_attr_id == ind_info[u'base_material_type_attr_id']).delete()
               session.query(BaseMaterialTypeAttrKeyWord).filter(BaseMaterialTypeAttrKeyWord.base_material_type_attr_id == ind_info[u'base_material_type_attr_id']).delete()
               session.query(BaseMaterialTypeAttr).filter(BaseMaterialTypeAttr.id == ind_info[u'base_material_type_attr_id']).delete()
               session.commit()

    ##
    # delete template attr value information by API indication.
    @staticmethod
    def del_template_attr_value(ind_info):
        with get_session() as session:
             be = session.query(BaseMaterialTypeAttrValue).filter(BaseMaterialTypeAttrValue.id == ind_info[u'base_material_type_attr_value_id']).first()
             if be:
               class_id = MatchRule.encode_class_id(be.base_material_type_attr.base_material_type.parent.code, be.base_material_type_attr.base_material_type.code)
               template_redis.delete(class_id)
               session.delete(be)
               session.commit()

    ##
    # delete template attr rule information by API indication.
    @staticmethod
    def del_template_attr_rule(ind_info):
        with get_session() as session:
             be = session.query(BaseMaterialTypeAttrRule).filter(BaseMaterialTypeAttrRule.id == ind_info[u'base_material_type_attr_rule_id']).first()
             if be:
               class_id = MatchRule.encode_class_id(be.base_material_type_attr.base_material_type.parent.code, be.base_material_type_attr.base_material_type.code)
               template_redis.delete(class_id)
               session.delete(be)
               session.commit()

    ##
    # delete template attr key word information by API indication.
    @staticmethod
    def del_template_attr_key_word(ind_info):
        with get_session() as session:
             be = session.query(BaseMaterialTypeAttrKeyWord).filter(BaseMaterialTypeAttrKeyWord.id == ind_info[u'base_material_type_attr_key_word_id']).first()
             if be:
               class_id = MatchRule.encode_class_id(be.base_material_type_attr.base_material_type.parent.code, be.base_material_type_attr.base_material_type.code)
               template_redis.delete(class_id)
               session.delete(be)
               session.commit()

    ##
    # update template attr information by API indication.
    @staticmethod
    def update_template_attr(ind_info):
       with get_session() as session:
          be = session.query(BaseMaterialTypeAttr).filter(BaseMaterialTypeAttr.id == ind_info[u'base_material_type_attr_id']).first()
          if be:
             be.description = ind_info[u'description']
             session.commit()
             class_id = MatchRule.encode_class_id(be.base_material_type.parent.code, be.base_material_type.code)
             template_redis.delete(class_id)

    ##
    # update template attr value information by API indication.
    @staticmethod
    def update_template_attr_value(ind_info):
       with get_session() as session:
          be = session.query(BaseMaterialTypeAttrValue).filter(BaseMaterialTypeAttrValue.id == ind_info[u'base_material_type_attr_value_id']).first()
          if be:
             be.description = ind_info[u'description']
             session.commit()
             class_id = MatchRule.encode_class_id(be.base_material_type_attr.base_material_type.parent.code, be.base_material_type_attr.base_material_type.code)
             template_redis.delete(class_id)

    ##
    # update template attr rule information by API indication.
    @staticmethod
    def update_template_attr_rule(ind_info):
       with get_session() as session:
          be = session.query(BaseMaterialTypeAttrRule).filter(BaseMaterialTypeAttrRule.id == ind_info[u'base_material_type_attr_rule_id']).first()
          if be:
             be.rule_description = ind_info[u'rule_description']
             session.commit()
             class_id = MatchRule.encode_class_id(be.base_material_type_attr.base_material_type.parent.code, be.base_material_type_attr.base_material_type.code)
             template_redis.delete(class_id)

    ##
    # update template attr key word information by API indication.
    @staticmethod
    def update_template_attr_key_word(ind_info):
       with get_session() as session:
          be = session.query(BaseMaterialTypeAttrKeyWord).filter(BaseMaterialTypeAttrKeyWord.id == ind_info[u'base_material_type_attr_key_word_id']).first()
          if be:
             be.key_words = ind_info[u'key_word']
             session.commit()
             class_id = MatchRule.encode_class_id(be.base_material_type_attr.base_material_type.parent.code, be.base_material_type_attr.base_material_type.code)
             template_redis.delete(class_id)

    ##
    # update template attr key word information by API indication.
    @staticmethod
    def add_template_attr(ind_info):
        base_material_type_attr = BaseMaterialTypeAttr()
        parent_bmt = aliased(BaseMaterialType)
        with get_session() as session:
            be = session.query(BaseMaterialType, parent_bmt).join((parent_bmt, parent_bmt.id == BaseMaterialType.parent_id))\
            .filter(BaseMaterialType.code == ind_info[u'code'][2:4], parent_bmt.code == ind_info[u'code'][0:2]).first()
            if be:
               base_material_type_attr.description = ind_info[u'description']
               base_material_type_attr.base_material_type_id = be[0].id
               session.add(base_material_type_attr)
               session.commit()
               class_id = MatchRule.encode_class_id(be[1].code, be[0].code)
               template_redis.delete(class_id)

    ##
    # update template attr key word information by API indication.
    @staticmethod
    def add_template_attr_value(ind_info):
        base_material_type_attr_value = BaseMaterialTypeAttrValue()
        with get_session() as session:
            base_material_type_attr_value.description = ind_info[u'description']
            base_material_type_attr_value.base_material_type_attr_id = ind_info[u'base_material_type_attr_id']
            session.add(base_material_type_attr_value)
            session.commit()
            be = session.query(BaseMaterialTypeAttr).filter(BaseMaterialTypeAttr.id == ind_info[u'base_material_type_attr_id']).first()
            if be:
               class_id = MatchRule.encode_class_id(be.base_material_type.parent.code, be.base_material_type.code)
               template_redis.delete(class_id)
    ##
    # update template attr key word information by API indication.
    @staticmethod
    def add_template_attr_rule(ind_info):
        base_material_type_attr_rule = BaseMaterialTypeAttrRule()
        with get_session() as session:
            base_material_type_attr_rule.rule_description = ind_info[u'rule_description']
            base_material_type_attr_rule.base_material_type_attr_id = ind_info[u'base_material_type_attr_id']
            session.add(base_material_type_attr_rule)
            session.commit()
            be = session.query(BaseMaterialTypeAttr).filter(BaseMaterialTypeAttr.id == ind_info[u'base_material_type_attr_id']).first()
            if be:
               class_id = MatchRule.encode_class_id(be.base_material_type.parent.code, be.base_material_type.code)
               template_redis.delete(class_id)

    ##
    # update template attr key word information by API indication.
    @staticmethod
    def add_template_attr_key_word(ind_info):
        base_material_type_attr_key_word = BaseMaterialTypeAttrKeyWord()
        with get_session() as session:
            base_material_type_attr_key_word.key_words = ind_info[u'key_word']
            base_material_type_attr_key_word.base_material_type_attr_id = ind_info[u'base_material_type_attr_id']
            session.add(base_material_type_attr_key_word)
            session.commit()
            be = session.query(BaseMaterialTypeAttr).filter(BaseMaterialTypeAttr.id == ind_info[u'base_material_type_attr_id']).first()
            if be:
               class_id = MatchRule.encode_class_id(be.base_material_type.parent.code, be.base_material_type.code)
               template_redis.delete(class_id)

# main function.
if __name__ == '__main__':
    m_template_updater = TemplateUpdater()
    m_template_updater.set_input_file(u'../../InputFile_test/result.xls')
    m_template_updater.update_templates()
