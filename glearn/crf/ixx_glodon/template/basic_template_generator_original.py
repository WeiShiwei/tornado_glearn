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
from model.session import *
from template.logger import logger
from api.config import config

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
            m_basic_element.lv1_id = int(rd_list[0])
            m_basic_element.lv2_id = int(rd_list[1])
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
        for i in range(1, row_num):

            #Generate basic elements class.
            m_basic_element = BasicElement()

            #Add element to dictionary.
            if True is self.generate_ele_dic(m_basic_element, table.row_values(i), i):
                m_basic_element_dic[i] = m_basic_element
            else:
                del m_basic_element

            #Update to data base when dictionary is full or it is the last loop.
            if (m_max_num_in_m_basic_element_dic <= len(m_basic_element_dic)) or (i == (row_num-1)):

                #commit change and clean dictionary.
                with get_session() as session:
                    logger.info('Add new %d elements to table.' % len(m_basic_element_dic))
                    session.add_all(m_basic_element_dic.values())
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
    def store_attr_rule_to_ele_list(attr_rule_info, lv1_id, lv2_id, lv1_name, lv2_name, attr_name, ele_store_list):
        # Divide attribute rule to list.
        attr_rule_list = attr_rule_info.split(u'-')
        for attr_rule_ele in attr_rule_list:
            if attr_rule_ele != u'' and u'attr_rule' not in attr_rule_ele:
                m_basic_element = BasicElement()
                m_basic_element.lv1_id = lv1_id
                m_basic_element.lv2_id = lv2_id
                m_basic_element.lv1_name = lv1_name
                m_basic_element.lv2_name = lv2_name
                m_basic_element.attr_name = attr_name
                m_basic_element.attr_val = u'-attr_rule;-' + attr_rule_ele
                ele_store_list.append(m_basic_element)
                logger.debug('Insert new element to element pool! [%s, %s, %s, %s, %s]' %
                            (m_basic_element.lv1_id, m_basic_element.lv2_id,
                             m_basic_element.lv1_name,
                             m_basic_element.lv2_name, m_basic_element.attr_name))

    # Submit all attr_rule to database.
    @staticmethod
    def submit_all_attr_rule_to_database(template_dic_pool):
        with get_session() as session:
            m_basic_element_list = []
            for class_id in template_dic_pool.keys():
                for attr_name in template_dic_pool[class_id].keys():
                    for i in range(0, len(template_dic_pool[class_id][attr_name])):
                        if u'attr_rule' in template_dic_pool[class_id][attr_name][i]:
                            m_lv1_id, m_lv2_id = MatchRule.decode_class_id(class_id)
                            be = session.query(BasicElement).filter_by(lv1_id=m_lv1_id, lv2_id=m_lv2_id).first()
                            if be:
                                # Divide and store attribute rule to elements list.
                                BasicTemplate.store_attr_rule_to_ele_list(
                                    template_dic_pool[class_id][attr_name][i],
                                    m_lv1_id, m_lv2_id, be.lv1_name, be.lv2_name, attr_name,
                                    m_basic_element_list
                                )
            logger.info('Add new %d elements to table.' % len(m_basic_element_list))
            session.add_all(m_basic_element_list)
            session.commit()

    # Clean attr_rule by class_id.
    @staticmethod
    def clean_attr_rule_by_class_id(class_id):
        m_lv1_id, m_lv2_id = MatchRule.decode_class_id(class_id)
        with get_session() as session:
            be = session.query(BasicElement).filter_by(lv1_id=m_lv1_id, lv2_id=m_lv2_id).first()
            if be:
                be_pool = session.query(BasicElement).filter_by(lv1_id=m_lv1_id, lv2_id=m_lv2_id).all()
                for i in range(0, len(be_pool)):
                    if u'attr_rule' in be_pool[i].attr_val:
                        session.delete(be_pool[i])
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

    ##
    # Create new template by indication list.
    @staticmethod
    def create_new_template_by_ind_list(indication_list):

        # Get total template number.
        template_total_num = len(indication_list)
        logger.debug('Get %d template to add.' % template_total_num)

        # Add new templates to add-list.
        m_basic_element_list = []
        for i in range(0, template_total_num):

            # Check whether the template is already in the database.
            with get_session() as session:
                be = session.query(BasicElement).filter_by(lv1_id=int(indication_list[i][u'first_type_code']),
                                                           lv2_id=int(indication_list[i][u'second_type_code']),
                                                           lv1_name=indication_list[i][u'first_type_name'],
                                                           lv2_name=indication_list[i][u'second_type_name'],
                                                           attr_name=indication_list[i][u'attr_name'],
                                                           attr_val=indication_list[i][u'attr_val']).first()
                if be:
                    logger.warning('The template is already in database: %d, %d, %s, %s.' %
                                   (be.lv1_id, be.lv2_id, be.attr_name, be.attr_val))
                    continue

            # Replace special word and Convert to inner structure.
            m_basic_element = BasicElement()

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
            m_basic_element_list.append(m_basic_element)
            logger.debug('Add new template to list: %d, %d, %s, %s.' % (m_basic_element.lv1_id, m_basic_element.lv2_id,
                                                                        m_basic_element.attr_name,
                                                                        m_basic_element.attr_val))
            # Clean template redis.
            class_id = MatchRule.encode_class_id(m_basic_element.lv1_id, m_basic_element.lv2_id)
            template_redis.delete(class_id)

        # Submit all new template to database.
        if len(m_basic_element_list):
            with get_session() as session:
                logger.info('Add new %d elements to table.' % len(m_basic_element_list))
                session.add_all(m_basic_element_list)
                session.commit()
        logger.info('Add all templates successfully!')
        return True

    ##
    # Rebuild attribute rule by indication list.
    @staticmethod
    def gen_attr_rule_by_ind_list(indication_list):

        # Find all basic template and store them to the pool.
        template_dic_pool = {}
        for i in range(0, len(indication_list)):
            class_id = MatchRule.encode_class_id(
                int(indication_list[i][u'first_type_code']),
                int(indication_list[i][u'second_type_code'])
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

# Main function  .
if __name__ == '__main__':

    #Generate basic template object.
    mBasicTemplate = BasicTemplate()
    mBasicTemplate.clean_table()
    mBasicTemplate.generate_basic_template()
    mBasicTemplate.gen_attr_rule_in_all_basic_template()
    #mBasicTemplate.log_all_template(u'25#00', u'26#00')
