# coding=utf-8
u"""
User: xulin
Date: 13-5-29
Time: 下午3:41
"""
import traceback
from api.handler.base_handler import BaseHandler


class RetrieveAttributeHandler(BaseHandler):
    _label = 'RetrieveAttributeHandler'

    def get(self):
        try:
            self._json_response('ok')
        except:
            self.send_error()
            self._app_logger.error(traceback.format_exc())


class CreateAttributeHandler(BaseHandler):
    _label = 'CreateAttributeHandler'

    def post(self):
        try:
            self._json_response('ok')
        except:
            self.send_error()
            self._app_logger.error(traceback.format_exc())


class UpdateAttributeHandler(BaseHandler):
    _label = 'UpdateAttributeHandler'

    def post(self):
        try:
            self._json_response('ok')
        except:
            self.send_error()
            self._app_logger.error(traceback.format_exc())


class DeleteAttributeHandler(BaseHandler):
    _label = 'DeleteAttributeHandler'

    def post(self):
        try:
            self._json_response('ok')
        except:
            self.send_error()
            self._app_logger.error(traceback.format_exc())