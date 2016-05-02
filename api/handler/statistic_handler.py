# coding=utf-8
u"""
Description: Report statistic information.
User: Jerry.Fang
Date: 14-01-06
"""
import traceback
from api.handler.base_handler import BaseHandler
import ujson
from statistic.heart_beat import HeartReqProcess
from statistic.stat_info_querier import StatInfoQuerier


class HeartRequestHandler(BaseHandler):
    _label = 'HeartRequestHandler'

    def get(self):
        try:
            result = {
                u'heart_response': HeartReqProcess.get_response()
            }
            self._json_response(result)
        except:
            self.send_error()
            self._app_logger.error(traceback.format_exc())


class QueryStatInfoHandler(BaseHandler):
    _label = 'QueryStatInfoHandler'

    def get(self):
        try:
            ind_list = dict()
            ind_list[u'query_msg_count'] = self.get_argument('query_msg_count', default='')
            ind_list[u'query_extract_rate'] = self.get_argument('query_extract_rate', default='')
            ind_list[u'query_extract_time'] = self.get_argument('query_extract_time', default='')
            result = dict()
            StatInfoQuerier.query(ind_list, result)
            self._json_response(result)
        except:
            self.send_error()
            self._app_logger.error(traceback.format_exc())