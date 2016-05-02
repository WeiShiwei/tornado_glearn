# coding=utf-8

import traceback
from api.handler.base_handler import BaseHandler
import ujson
from template.assembly_template import AssemblyTemplate

# from glearn.crf.ixx_glodon.template.assembly_template import AssemblyTemplate
from template.basic_template_generator import BasicTemplate
from template.basic_template_updater import TemplateUpdater

class CreateAssemblyTemplateHandler(BaseHandler):
    _label = 'CreateAssemblyTemplateHandler'
    def post(self):
        try:
            ind_info = dict()
            ind_info["first_type_code"] = self.get_argument('first_type_code', default='')
            ind_info["second_type_code"] = self.get_argument('second_type_code', default='')
            ind_info["assembly_attr_name"] = self.get_argument('assembly_attr_name', default='')

            res = AssemblyTemplate.create_assembly_template(ind_info)
            if res:
                self._json_response('OK')
            else:
                self._json_response('Fail')
        except:
            self.send_error()
            self._app_logger.error(traceback.format_exc())

class UpdateAssemblyTemplateHandler(BaseHandler):
    _label = 'UpdateAssemblyTemplateHandler'
    def post(self):
        try:
            assembly_attr_list = ujson.loads(self.get_argument('assemblyAttrs', default=''))
            AssemblyTemplate.check_assembly_attr(assembly_attr_list)
            res = AssemblyTemplate.update_assembly_attr(assembly_attr_list)
            if res:
                self._json_response('OK')
            else:
                self._json_response('Fail')
        except:
            self.send_error()
            self._app_logger.error(traceback.format_exc())

class RetrieveAssemblyTemplateHandler(BaseHandler):
    _label = 'RetrieveAssemblyTemplateHandler'
    def get(self):
        try:
            ind_info = dict()
            ind_info[u'first_type_code'] = self.get_argument('first_type_code', default='')
            ind_info[u'second_type_code'] = self.get_argument('second_type_code', default='')
            ind_info[u'assembly_attr_names'] = self.get_argument('assembly_attr_names', default='')
            
            attrNameValue_dict = dict()
            AssemblyTemplate.retrieve_assembly_template(ind_info,attrNameValue_dict) 
       
            json_result = {
                'first_type_code': ind_info[u'first_type_code'],
                'second_type_code': ind_info[u'second_type_code'],
                'assembly_attrName_value_dict':attrNameValue_dict
            }
            self._json_response(json_result)
        except:
            self.send_error()
            self._app_logger.error(traceback.format_exc())

class RetrieveLv2AssemblyTemplateHandler(BaseHandler):
    _label = 'RetrieveLv2AssemblyTemplateHandler'
    def get(self):
        try:
            ind_info = dict()
            ind_info[u'first_type_code'] = self.get_argument('first_type_code', default='')
            ind_info[u'second_type_code'] = self.get_argument('second_type_code', default='')
            ind_info[u'page'] = self.get_argument('page', default='')
            ind_info[u'pagesize'] = self.get_argument('pagesize', default='')
            
            # lv2_id_attrValue_dict = dict()
            lv2_id_attrValue_list = list()
            json_result = {
                'first_type_code': ind_info[u'first_type_code'],
                'second_type_code': ind_info[u'second_type_code'],
                'record_num':'',
                # 'lv2_id_attrValue_dict':lv2_id_attrValue_dict
                'lv2_id_attrValue_list':lv2_id_attrValue_list
            }
            AssemblyTemplate.retrieve_lv2assembly_template(ind_info,json_result) 
            
            self._json_response(json_result)
        except:
            self.send_error()
            self._app_logger.error(traceback.format_exc())

class DeleteAssemblyTemplateHandler(BaseHandler):
    _label = 'DeleteAssemblyTemplateHandler'
    def post(self):
        try:
            ind_info = dict()
            ind_info[u'base_material_type_attr_set_id'] = self.get_argument('base_material_type_attr_set_id', default='')
            AssemblyTemplate.delete_assembly_template(ind_info)
            self._json_response('ok')
        except:
            self.send_error()
            self._app_logger.error(traceback.format_exc())


class CreateAssemblyAttrValPairHandler(BaseHandler):
    _label = 'CreateAssemblyAttrValPairHandler'
    def post(self):
        try:
            ind_info = dict()
            ind_info[u'base_material_type_attr_set_id'] = self.get_argument('base_material_type_attr_set_id', default='')
            ind_info[u'base_material_type_attr_id'] = self.get_argument('base_material_type_attr_id', default='')
            ind_info[u'assembly_attr_value'] = self.get_argument('assembly_attr_value', default='')
            res = AssemblyTemplate.create_assembly_attrValPair(ind_info)
            if res:
                self._json_response('OK')
            else:
                self._json_response('Fail')
        except Exception, e:
            self.send_error()
            self._app_logger.error(traceback.format_exc())

class DeleteAssemblyAttrValPairHandler(BaseHandler):
    _label = 'DeleteAssemblyAttrValPairHandler'
    def post(self):
        try:
            ind_info = dict()
            ind_info[u'base_material_type_attr_set_id'] = self.get_argument('base_material_type_attr_set_id', default='')
            ind_info[u'base_material_type_attr_id'] = self.get_argument('base_material_type_attr_id', default='')
            AssemblyTemplate.delete_assembly_attrValPair(ind_info)
            self._json_response('ok')
        except Exception, e:
            self.send_error()
            self._app_logger.error(traceback.format_exc())

class DeleteAssemblyAttrIdValPairHandler(BaseHandler):
    _label = 'DeleteAssemblyAttrIdValPairHandler'
    def post(self):
        try:
            ind_info = dict()
            ind_info[u'attr_set_value_id'] = self.get_argument('attr_set_value_id', default='')
            AssemblyTemplate.delete_assembly_attrValPair_byId(ind_info)
            self._json_response('ok')
        except Exception, e:
            self.send_error()
            self._app_logger.error(traceback.format_exc())

class RetrieveAssemblyAttrValPairHandler(BaseHandler):
    _label = 'RetrieveAssemblyAttrValPairHandler'
    def get(self):
        try:
            ind_info = dict()
            ind_info[u'attr_set_value_id'] = self.get_argument('attr_set_value_id', default='')
            assembly_attrValPair_dict = dict()
            AssemblyTemplate.retrieve_assembly_attrValPair(ind_info,assembly_attrValPair_dict)

            self._json_response(assembly_attrValPair_dict)
        except:
            self.send_error()
            self._app_logger.error(traceback.format_exc())        

class RetrieveAssemblyAttrValPairsHandler(BaseHandler):
    _label = 'RetrieveAssemblyAttrValPairsHandler'
    def get(self):
        try:
            ind_info = dict()
            ind_info[u'base_material_type_attr_set_id'] = self.get_argument('base_material_type_attr_set_id', default='')
            ind_info[u'page'] = self.get_argument('page', default='')
            ind_info[u'pagesize'] = self.get_argument('pagesize', default='')

            #` assembly_id_attrNameVal_dict = dict()
            assembly_id_attrNameVal_list = list()
            json_result = {
                'base_material_type_attr_set_id': ind_info[u'base_material_type_attr_set_id'],
                'record_num':'',
                #` 'assembly_id_attrNameVal_dict':assembly_id_attrNameVal_dict,
                'assembly_id_attrNameVal_list':assembly_id_attrNameVal_list
            }
            AssemblyTemplate.retrieve_assembly_attrValPairs(ind_info,json_result)
            self._json_response(json_result)
        except:
            self.send_error()
            self._app_logger.error(traceback.format_exc())    

