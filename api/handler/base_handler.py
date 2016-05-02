# coding=utf-8

import logging
from datetime import datetime
from tornado import web
import ujson as json


class BaseHandler(web.RequestHandler):
    """请求处理的抽象类

    属性：
        _cacheable：确定是否把返回结果缓存在Redis中，如果确定缓存，那么在请求处理时，需要先从缓存中获取返回结果。
        _label：用于确定当前处理请求接口的类，主要用于Log输出。
        _app_logger：Log输出对象。
    """

    _cacheable = False
    _label = 'BaseHandler'
    _app_logger = logging.getLogger('api')

    def prepare(self):
        """处理请求前的预处理
        """
        pass

    def on_finish(self):
        """处理请求后的收尾处理
        """
        pass

    def _json_response(self, response):
        self.set_header('Cache-Control', 'private')
        self.set_header('Date', datetime.now())
        self.set_header('Content-Type', 'application/json; charset=utf-8')

        self.write(json.dumps(response))
        self.finish()



