# coding=utf-8
u"""
User: xulin
Date: 13-5-29
Time: 下午3:41
"""
import traceback
from api.handler.base_handler import BaseHandler


class RetrieveTypeHandler(BaseHandler):
    _label = 'RetrieveTypeHandler'

    def get(self):
        try:
            self._json_response('ok')
        except:
            self.send_error()
            self._app_logger.error(traceback.format_exc())


class CreateTypeHandler(BaseHandler):
    _label = 'CreateTypeHandler'

    def post(self):
        try:
            self._json_response('ok')
        except:
            self.send_error()
            self._app_logger.error(traceback.format_exc())


class UpdateTypeHandler(BaseHandler):
    _label = 'UpdateTypeHandler'

    def post(self):
        try:
            self._json_response('ok')
        except:
            self.send_error()
            self._app_logger.error(traceback.format_exc())


class DeleteTypeHandler(BaseHandler):
    _label = 'DeleteTypeHandler'

    def post(self):
        try:
            self._json_response('ok')
        except:
            self.send_error()
            self._app_logger.error(traceback.format_exc())