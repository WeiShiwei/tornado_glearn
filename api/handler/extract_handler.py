# coding=utf-8
u"""
User: xulin
Date: 13-5-29
Time: 下午3:41
"""
import traceback
import time
from api.handler.base_handler import BaseHandler
from extractor.data_extractor import DataExtractor


class ExtractHandler(BaseHandler):
    _label = 'ExtractHandler'

    def post(self):
        try:
            all_result = {
                u'first_type_code': self.get_argument('first_type_code'),
                u'second_type_code': self.get_argument('second_type_code'),
                u'product_info': self.get_argument('product_info'),
                u'result': {}
            }

            DataExtractor.extract_product_info_by_ind(all_result[u'first_type_code'],
                                                      all_result[u'second_type_code'],
                                                      all_result[u'product_info'],
                                                      all_result[u'result'])

            self._json_response(all_result)

        except:
            self.send_error()
            self._app_logger.error(traceback.format_exc())

    def get(self):
        try:
            t0 = time.clock()
            all_result = {
                u'first_type_code': 25,
                u'second_type_code': 11,
                u'product_info': u'8.7/15kV\tYJV\t一芯  25m㎡\t结构7\tBB',
                u'result': {}
            }

            DataExtractor.extract_product_info_by_ind(all_result[u'first_type_code'],
                                                      all_result[u'second_type_code'],
                                                      all_result[u'product_info'],
                                                      all_result[u'result'])

            elapsed = (time.clock() - t0) * 1000
            self._app_logger.warn('EXTRACT TIME %d' % elapsed)

            self._json_response(all_result)

        except:
            self.send_error()
            self._app_logger.error(traceback.format_exc())
