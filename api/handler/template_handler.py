# coding=utf-8
u"""
User: xulin
Date: 13-5-29
Time: 下午3:41
"""
import traceback
from api.handler.base_handler import BaseHandler
import ujson
from template.basic_template_generator import BasicTemplate
from template.basic_template_updater import TemplateUpdater

class RetrieveTemplateHandler(BaseHandler):
    _label = 'RetrieveTemplateHandler'

    def get(self):
        try:
            ind_info = dict()
            ind_info[u'first_type_code'] = self.get_argument('first_type_code', default='')
            ind_info[u'second_type_code'] = self.get_argument('second_type_code', default='')
            ind_info[u'attr_name'] = self.get_argument('attr_name', default='')
            ind_info[u'page'] = self.get_argument('page', default='')
            ind_info[u'page_size'] = self.get_argument('page_size', default='')
            all_result = {
                u'total': 0,
                u'rows': {}
            }
            TemplateUpdater.retrieve_template_by_api_ind(ind_info, all_result)
            self._json_response(all_result)
        except:
            self.send_error()
            self._app_logger.error(traceback.format_exc())


class CreateTemplateHandler(BaseHandler):
    _label = 'CreateTemplateHandler'

    def post(self):
        try:
            template_list = ujson.loads(self.get_argument('templates', default=''))
            ### 检查 template_list 
            BasicTemplate.check_new_template_ind_list(template_list)
            ### 更新数据库 
            res = BasicTemplate.create_new_template_by_ind_list(template_list)
            if res:
                ### 产生属性规则
                BasicTemplate.gen_attr_rule_by_ind_list(template_list) 
                self._json_response('OK')
            else:
                self._json_response('Fail')
        except:
            self.send_error()
            self._app_logger.error(traceback.format_exc())


class UpdateTemplateHandler(BaseHandler):
    _label = 'UpdateTemplateHandler'

    def post(self):
        try:
            ind_info = dict()
            ind_info[u'unique_id'] = self.get_argument('unique_id', default='')
            ind_info[u'first_type_code'] = self.get_argument('first_type_code', default='')
            ind_info[u'second_type_code'] = self.get_argument('second_type_code', default='')
            ind_info[u'attr_name'] = self.get_argument('attr_name', default='')
            ind_info[u'attr_val'] = self.get_argument('attr_val', default='')
            TemplateUpdater.update_template_by_api_ind(ind_info)
            self._json_response('ok')
        except:
            self.send_error()
            self._app_logger.error(traceback.format_exc())


class DeleteTemplateHandler(BaseHandler):
    _label = 'DeleteTemplateHandler'

    def post(self):
        try:
            ind_info = dict()
            ind_info[u'unique_id'] = self.get_argument('unique_id', default='')
            ind_info[u'first_type_code'] = self.get_argument('first_type_code', default='')
            ind_info[u'second_type_code'] = self.get_argument('second_type_code', default='')
            ind_info[u'attr_name'] = self.get_argument('attr_name', default='')
            TemplateUpdater.del_template_by_api_ind(ind_info)
            self._json_response('ok')
        except:
            self.send_error()
            self._app_logger.error(traceback.format_exc())

class RetrieveTemplateAttrHandler(BaseHandler):
    _label = 'RetrieveTemplateAttrHandler'
    def get(self):
        try:
            ind_info = dict()
            ind_info[u'first_type_code'] = self.get_argument('first_type_code', default='')
            ind_info[u'second_type_code'] = self.get_argument('second_type_code', default='')
            ind_info[u'page'] = self.get_argument('page', default='')
            ind_info[u'page_size'] = self.get_argument('page_size', default='')
            result = TemplateUpdater.retrieve_template_attr_by_api_ind(ind_info)
            self._json_response(result)
        except:
            self.send_error()
            self._app_logger.error(traceback.format_exc())

class RetrieveTemplateAttrValueHandler(BaseHandler):
     _label = 'RetrieveTemplateAttrValueHandler'
     def get(self):
         try:
             ind_info = dict()
             ind_info[u'base_material_type_attr_id'] = self.get_argument('base_material_type_attr_id', default='')
             ind_info[u'page'] = self.get_argument('page', default='')
             ind_info[u'page_size'] = self.get_argument('page_size', default='')
             result = TemplateUpdater.retrieve_template_attr_value_by_api_ind(ind_info)
             self._json_response(result)
         except:
             self.send_error()
             self._app_logger.error(traceback.format_exc())

class RetrieveTemplateAttrRulewHandler(BaseHandler):
    _label = 'RetrieveTemplateAttrRulewHandler'
    def get(self):
        try:
            ind_info = dict()
            ind_info[u'base_material_type_attr_id'] = self.get_argument('base_material_type_attr_id', default='')
            ind_info[u'page'] = self.get_argument('page', default='')
            ind_info[u'page_size'] = self.get_argument('page_size', default='')
            result = TemplateUpdater.retrieve_template_attr_rule_by_api_ind(ind_info)
            self._json_response(result)
        except:
            self.send_error()
            self._app_logger.error(traceback.format_exc())

class RetrieveTemplateAttrKeyWordwHandler(BaseHandler):
    _label = 'RetrieveTemplateAttrKeyWordwHandler'
    def get(self):
        try:
            ind_info = dict()
            ind_info[u'base_material_type_attr_id'] = self.get_argument('base_material_type_attr_id', default='')
            ind_info[u'page'] = self.get_argument('page', default='')
            ind_info[u'page_size'] = self.get_argument('page_size', default='')
            result = TemplateUpdater.retrieve_template_attr_key_word_by_api_ind(ind_info)
            self._json_response(result)
        except:
            self.send_error()
            self._app_logger.error(traceback.format_exc())

class DeleteTemplateAttrHandler(BaseHandler):
    _label = 'DeleteTemplateAttrHandler'
    def post(self):
        try:
            ind_info = dict()
            ind_info[u'base_material_type_attr_id'] = self.get_argument('base_material_type_attr_id', default='')
            result = TemplateUpdater.del_template_attr(ind_info)
            self._json_response(result)
        except:
            self.send_error()
            self._app_logger.error(traceback.format_exc())

class DeleteTemplateAttrValueHandler(BaseHandler):
    _label = 'DeleteTemplateAttrValueHandler'
    def post(self):
        try:
            ind_info = dict()
            ind_info[u'base_material_type_attr_value_id'] = self.get_argument('base_material_type_attr_value_id', default='')
            result = TemplateUpdater.del_template_attr_value(ind_info)
            self._json_response(result)
        except:
            self.send_error()
            self._app_logger.error(traceback.format_exc())

class DeleteTemplateAttrRuleHandler(BaseHandler):
    _label = 'DeleteTemplateAttrRuleHandler'
    def post(self):
        try:
            ind_info = dict()
            ind_info[u'base_material_type_attr_rule_id'] = self.get_argument('base_material_type_attr_rule_id', default='')
            result = TemplateUpdater.del_template_attr_rule(ind_info)
            self._json_response(result)
        except:
            self.send_error()
            self._app_logger.error(traceback.format_exc())

class DeleteTemplateAttrKeyWordHandler(BaseHandler):
    _label = 'DeleteTemplateAttrKeyWordHandler'
    def post(self):
        try:
            ind_info = dict()
            ind_info[u'base_material_type_attr_key_word_id'] = self.get_argument('base_material_type_attr_key_word_id', default='')
            result = TemplateUpdater.del_template_attr_key_word(ind_info)
            self._json_response(result)
        except:
            self.send_error()
            self._app_logger.error(traceback.format_exc())

class UpdateTemplateAttrHandler(BaseHandler):
    _label = 'UpdateTemplateAttrHandler'
    def post(self):
        try:
            ind_info = dict()
            ind_info[u'base_material_type_attr_id'] = self.get_argument('base_material_type_attr_id', default='')
            ind_info[u'description'] = self.get_argument('description', default='')
            result = TemplateUpdater.update_template_attr(ind_info)
            self._json_response(result)
        except:
            self.send_error()
            self._app_logger.error(traceback.format_exc())

class UpdateTemplateAttrValueHandler(BaseHandler):
    _label = 'UpdateTemplateAttrValueHandler'
    def post(self):
        try:
            ind_info = dict()
            ind_info[u'base_material_type_attr_value_id'] = self.get_argument('base_material_type_attr_value_id', default='')
            ind_info[u'description'] = self.get_argument('description', default='')
            result = TemplateUpdater.update_template_attr_value(ind_info)
            self._json_response(result)
        except:
            self.send_error()
            self._app_logger.error(traceback.format_exc())

class UpdateTemplateAttrRuleHandler(BaseHandler):
    _label = 'UpdateTemplateAttrRuleHandler'
    def post(self):
        try:
            ind_info = dict()
            ind_info[u'base_material_type_attr_rule_id'] = self.get_argument('base_material_type_attr_rule_id', default='')
            ind_info[u'rule_description'] = self.get_argument('rule_description', default='')
            result = TemplateUpdater.update_template_attr_rule(ind_info)
            self._json_response(result)
        except:
            self.send_error()
            self._app_logger.error(traceback.format_exc())

class UpdateTemplateAttrKeyWordHandler(BaseHandler):
    _label = 'UpdateTemplateAttrKeyWordHandler'
    def post(self):
        try:
            ind_info = dict()
            ind_info[u'base_material_type_attr_key_word_id'] = self.get_argument('base_material_type_attr_key_word_id', default='')
            ind_info[u'description'] = self.get_argument('description', default='')
            result = TemplateUpdater.update_template_attr_key_word(ind_info)
            self._json_response(result)
        except:
            self.send_error()
            self._app_logger.error(traceback.format_exc())

class CreateTemplateAttrHandler(BaseHandler):
    _label = 'CreateTemplateAttrHandler'
    def post(self):
        try:
            ind_info = dict()
            ind_info[u'code'] = self.get_argument('code', default='')
            ind_info[u'description'] = self.get_argument('description', default='')
            result = TemplateUpdater.add_template_attr(ind_info)
            self._json_response(result)
        except:
            self.send_error()
            self._app_logger.error(traceback.format_exc())

class CreateTemplateAttrValueHandler(BaseHandler):
    _label = 'CreateTemplateAttrValueHandler'
    def post(self):
        try:
            ind_info = dict()
            ind_info[u'base_material_type_attr_id'] = self.get_argument('base_material_type_attr_id', default='')
            ind_info[u'description'] = self.get_argument('description', default='')
            result = TemplateUpdater.add_template_attr_value(ind_info)
            self._json_response(result)
        except:
            self.send_error()
            self._app_logger.error(traceback.format_exc())

class CreateTemplateAttrRuleHandler(BaseHandler):
    _label = 'CreateTemplateAttrRuleHandler'
    def post(self):
        try:
            ind_info = dict()
            ind_info[u'base_material_type_attr_id'] = self.get_argument('base_material_type_attr_id', default='')
            ind_info[u'rule_description'] = self.get_argument('rule_description', default='')
            result = TemplateUpdater.add_template_attr_rule(ind_info)
            self._json_response(result)
        except:
            self.send_error()
            self._app_logger.error(traceback.format_exc())

class CreateTemplateAttrKeyWordHandler(BaseHandler):
    _label = 'CreateTemplateAttrKeyWordHandler'
    def post(self):
        try:
            ind_info = dict()
            ind_info[u'base_material_type_attr_id'] = self.get_argument('base_material_type_attr_id', default='')
            ind_info[u'key_word'] = self.get_argument('key_word', default='')
            result = TemplateUpdater.add_template_attr_key_word(ind_info)
            self._json_response(result)
        except:
            self.send_error()
            self._app_logger.error(traceback.format_exc())