# coding=utf-8
u"""
Description: Report statistic information.
User: Jerry.Fang
Date: 14-01-06
"""

import requests
import ujson
import unittest
from statistic.stat_info_querier import StatInfoQuerier
from statistic.heart_beat import HeartReqProcess
from extractor.data_extractor import template_redis


class TestStatisticFunctions(unittest.TestCase):
    def setUp(self):
        template_redis.flushdb()
        pass

    def test_heart_fun(self):
        self.assertEqual(u'OK', HeartReqProcess.get_response())

    def test_query_fun(self):
        self.assertEqual(0, StatInfoQuerier.get_val(u'msg_total_time'))

        StatInfoQuerier.store_val(u'msg_total_time', 100)
        self.assertEqual(100, StatInfoQuerier.get_val(u'msg_total_time'))

        StatInfoQuerier.clean_stat_info()
        self.assertEqual(0, StatInfoQuerier.get_val(u'msg_total_time'))

        StatInfoQuerier.store_val(u'msg_total_time', 1000)
        StatInfoQuerier.store_val(u'msg_count', 20)
        StatInfoQuerier.store_val(u'msg_total_len', 300000)
        StatInfoQuerier.store_val(u'msg_extract_len', 289000)
        ind_list1 = {
            'query_msg_count': 1,
            'query_extract_rate': 1,
            'query_extract_time': 1,
            'query_msg_count_error1': 2,
            'query_msg_count_error2': u'',
        }
        expect_result1 = {
            u'msg_count': 20,
            u'extract_rate': u'96.3333333333%',
            u'extract_time': u'50ms',
        }
        actual_result = dict()
        StatInfoQuerier.query(ind_list1, actual_result)
        self.assertEqual(expect_result1, actual_result)

        ind_list2 = {
            'query_msg_count': 0,
            'query_extract_rate': 1,
            'query_extract_time': 1,
        }
        expect_result2 = {
            u'extract_rate': u'96.3333333333%',
            u'extract_time': u'50ms',
        }
        expect_result3 = {
            u'extract_rate': u'0.0%',
            u'extract_time': u'0ms',
        }
        actual_result = dict()
        StatInfoQuerier.query(ind_list2, actual_result)
        self.assertEqual(expect_result2, actual_result)
        StatInfoQuerier.query(ind_list2, actual_result)
        self.assertEqual(expect_result3, actual_result)

        ind_list3 = {
            'query_msg_count': 1,
            'query_extract_rate': 1,
            'query_extract_time': 1,
        }
        expect_result4 = {
            u'msg_count': 0,
            u'extract_rate': u'0.0%',
            u'extract_time': u'0ms',
        }
        actual_result = dict()
        StatInfoQuerier.query(ind_list3, actual_result)
        self.assertEqual(expect_result4, actual_result)

# Run test cases.
if __name__ == '__main__':
    unittest.main()