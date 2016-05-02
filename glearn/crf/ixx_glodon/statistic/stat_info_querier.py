# coding=utf-8
u"""
Description: Report statistic information.
User: Jerry.Fang
Date: 14-01-06
"""
from template.logger import logger
from extractor.data_extractor import template_redis


class StatInfoQuerier():

    def __init__(self):
        pass

    @staticmethod
    def clean_stat_info():
        template_redis.set(u'msg_total_time', 0)
        template_redis.set(u'msg_count', 0)
        template_redis.set(u'msg_total_len', 0)
        template_redis.set(u'msg_extract_len', 0)

    @staticmethod
    def get_val(stat_name):
        if template_redis.get(stat_name) is not None:
            return int(template_redis.get(stat_name))
        else:
            return 0

    @staticmethod
    def store_val(stat_name, stat_val):
        template_redis.set(stat_name, stat_val)

    @staticmethod
    def query(ind_list, result):

        is_need_clear = False

        for ind_key, ind_val in ind_list.items():

            if ind_val == u'':
                continue

            # Clean all statistic information.
            if int(ind_val) == 0:
                is_need_clear = True
                continue

            # query messages' number.
            if ind_key == u'query_msg_count':
                result[u'msg_count'] = StatInfoQuerier.get_val(u'msg_count')

            # query messages' extract rate.
            elif ind_key == u'query_extract_rate':
                msg_total_len = float(StatInfoQuerier.get_val(u'msg_total_len'))
                msg_extract_len = float(StatInfoQuerier.get_val(u'msg_extract_len'))
                if msg_total_len > 0:
                    result[u'extract_rate'] = str(msg_extract_len * 100.0 / msg_total_len) + u'%'
                else:
                    result[u'extract_rate'] = u'0.0%'

            # query messages' extract cost time.
            elif ind_key == u'query_extract_time':
                msg_total_time = StatInfoQuerier.get_val(u'msg_total_time')
                msg_count = StatInfoQuerier.get_val(u'msg_count')
                if msg_count > 0:
                    result[u'extract_time'] = str(msg_total_time / msg_count) + u'ms'
                else:
                    result[u'extract_time'] = u'0ms'

            # report error.
            else:
                logger.error('query request: "%s" - "%s" ' % (ind_key, ind_val))

        #Clean statistic information.
        if is_need_clear is True:
            StatInfoQuerier.clean_stat_info()