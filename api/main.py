#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, sys
sys.path.append( os.path.join( os.path.abspath(os.path.dirname(__file__)) , '..'))
# sys.path.append( os.path.join( os.path.abspath(os.path.dirname(__file__)) , '../dependence'))
sys.path.append( os.path.join( os.path.abspath(os.path.dirname(__file__)) , '../glearn/crf/ixx_glodon'))

import tornado.httpserver
from tornado import ioloop, web
from tornado.options import define, parse_command_line, options
from lib.log_util import create_log

from api.config import config
from api.handler import *
from glearn.crf.crfpp_platform import CRF

define('port', default=9711, help="run on the given port", type=int)

class Application(tornado.web.Application):
    def __init__(self):
        self.crf = CRF()
        
        handlers = [
            (r'/crf/train_model', TrainCrfModelHandler),
            (r'/crf/decode',DecodeHandler),
            (r'/crf/cross_validate',CrossValidateHandler),

            (r'/file', UploadFileHandler),
            (r'/crf/predict', CrfPredictExtendedHandler),
            # (r'/crf/predict_extended', CrfPredictExtendedHandler),
            
            # -------------------------------------------------------
            (r'/v1/extract', ExtractHandler),
            (r'/v1/attribute/retrieve', RetrieveAttributeHandler),
            (r'/v1/attribute/create', CreateAttributeHandler), 
            (r'/v1/attribute/update', UpdateAttributeHandler),
            (r'/v1/attribute/delete', DeleteAttributeHandler),
            (r'/v1/template/retrieve', RetrieveTemplateHandler),
            (r'/v1/template/create', CreateTemplateHandler), ### defined in template_handler
            (r'/v1/template/update', UpdateTemplateHandler),
            (r'/v1/template/delete', DeleteTemplateHandler),
            (r'/v1/template/create_attr', CreateTemplateAttrHandler),
            (r'/v1/template/create_attr_value', CreateTemplateAttrValueHandler),
            (r'/v1/template/create_attr_rule', CreateTemplateAttrRuleHandler),
            (r'/v1/template/create_attr_key_word', CreateTemplateAttrKeyWordHandler),
            (r'/v1/template/update_attr', UpdateTemplateAttrHandler),
            (r'/v1/template/update_attr_value', UpdateTemplateAttrValueHandler),
            (r'/v1/template/update_attr_rule', UpdateTemplateAttrRuleHandler),
            (r'/v1/template/update_attr_key_word', UpdateTemplateAttrKeyWordHandler),
            (r'/v1/template/delete_attr', DeleteTemplateAttrHandler),
            (r'/v1/template/delete_attr_value', DeleteTemplateAttrValueHandler),
            (r'/v1/template/delete_attr_rule', DeleteTemplateAttrRuleHandler),
            (r'/v1/template/delete_attr_key_word', DeleteTemplateAttrKeyWordHandler),
            (r'/v1/template/retrieve_attr', RetrieveTemplateAttrHandler),
            (r'/v1/template/retrieve_attr_value', RetrieveTemplateAttrValueHandler),
            (r'/v1/template/retrieve_attr_rule', RetrieveTemplateAttrRulewHandler),
            (r'/v1/template/retrieve_attr_key_word', RetrieveTemplateAttrKeyWordwHandler),
            (r'/v1/type/retrieve', RetrieveTypeHandler),
            (r'/v1/type/create', CreateTypeHandler),
            (r'/v1/type/update', UpdateTypeHandler),
            (r'/v1/type/delete', DeleteTypeHandler),
            (r'/v1/stat/heart', HeartRequestHandler),
            (r'/v1/stat/query', QueryStatInfoHandler),

            (r'/v1/assembly/create_template',CreateAssemblyTemplateHandler),
            # (r'/v1/assembly/update_template',UpdateAssemblyTemplateHandler),
            (r'/v1/assembly/retrieve_template',RetrieveAssemblyTemplateHandler),
            (r'/v1/assembly/retrieve_lv2Template',RetrieveLv2AssemblyTemplateHandler),
            (r'/v1/assembly/delete_template',DeleteAssemblyTemplateHandler),

            (r'/v1/assembly/create_attrValPair',CreateAssemblyAttrValPairHandler),
            (r'/v1/assembly/delete_attrValPair',DeleteAssemblyAttrValPairHandler),
            (r'/v1/assembly/delete_attrIdValPair',DeleteAssemblyAttrIdValPairHandler),
            # (r'/v1/assembly/retrieve_attrValPair',RetrieveAssemblyAttrValPairHandler),
            (r'/v1/assembly/retrieve_attrValPairs',RetrieveAssemblyAttrValPairsHandler)
        ]
            
        settings = {
            'template_path': os.path.join(os.path.dirname(__file__), "templates"),
            'static_path': 'static',
            'debug': True
        }
        
        tornado.web.Application.__init__(self, handlers, **settings)

if __name__ == '__main__':
    app_logger = create_log('api')

    tornado.options.parse_command_line()

    app = Application()
    server = tornado.httpserver.HTTPServer(app)
    server.listen(options.port)
    app_logger.info('tornado_crf API listen on %d' % options.port)

    tornado.ioloop.IOLoop.instance().start()

