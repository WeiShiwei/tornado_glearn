# coding=utf-8

import os
import sys
sys.path.append( os.path.join( os.path.abspath(os.path.dirname(__file__)) , '..'))

from xlrd import open_workbook
# from template.match_rule import *
# from extractor.data_extractor import DataExtractor
# from extractor.data_extractor import template_redis
from model.basic_element import BasicElement
from model.base_material_type import *
from model.base_material_type_attr import *
from model.base_material_type_attr_value import *
from model.base_material_type_attr_key_word import *
from model.base_material_type_attr_rule import *
from model.session import *
from template.logger import logger ###20150319
# from logger import logger
from api.config import config
from sqlalchemy.orm import aliased

from model.base_material_type_attr_sets import *
from model.attr_set_values import *

import math

class AssemblyTemplate():    
    ##
    @staticmethod
    def create_assembly_template(assmblyTemplate): 
        res = False

        lv1_id = assmblyTemplate[u'first_type_code']
        lv2_id = assmblyTemplate[u'second_type_code']
        assembly_attr_name = assmblyTemplate["assembly_attr_name"]

        parent_bmt = aliased(BaseMaterialType)
        with get_session() as session:

            be = session.query(BaseMaterialType, parent_bmt).join((parent_bmt, parent_bmt.id == BaseMaterialType.parent_id))\
                .filter(BaseMaterialType.code == lv2_id, parent_bmt.code == lv1_id).first()
            if be:
                base_material_type_id = be[0].id # be is 'KeyedTuple' object

                be_assembly_template = session.query(BaseMaterialTypeAttrSets).filter(BaseMaterialTypeAttrSets.base_material_type_id==base_material_type_id,\
                    BaseMaterialTypeAttrSets.description ==assembly_attr_name).first()
                if be_assembly_template:                    
                    res = False
                    logger.error('there is already a item(%s,%s) in base_material_type_attr_sets'%(base_material_type_id,assembly_attr_name))                    
                else:                    
                    base_material_type_attr_set = BaseMaterialTypeAttrSets(description =assembly_attr_name, \
                        base_material_type_id=base_material_type_id)
                    session.add(base_material_type_attr_set)
                    session.commit()
                    res = True
            else:
                logger.error('no corresponding entry:(%s) in BaseMaterialType table' % (lv1_id+' '+lv2_id))
                res = False
        return res


    @staticmethod
    def check_assembly_attr(assembly_attr_list):
        pass
    
    @staticmethod
    def update_assembly_attr(assembly_attr_list):
        """ '更新'意味着可以插入，可以修改（只要传进来的格式正确）
        """
        attr_total_num = len(assembly_attr_list)
        logger.debug('Get %d attrs to add.' % attr_total_num)

        with get_session() as session:
            for assembly_attr in assembly_attr_list:
                base_material_type_attr_set_id = assembly_attr['base_material_type_attr_set_id']
                base_material_type_attr_id = assembly_attr['base_material_type_attr_id']
                assembly_attr_value = assembly_attr['assembly_attr_value']
                
                be_assembly_attr = session.query(AttrSetValues).filter(AttrSetValues.base_material_type_attr_set_id== base_material_type_attr_set_id,\
                    AttrSetValues.base_material_type_attr_id==base_material_type_attr_id).first()
                if be_assembly_attr:
                    be_assembly_attr.attr_value=assembly_attr_value
                    session.add(be_assembly_attr)
                else:
                    attr_set_value = AttrSetValues(base_material_type_attr_set_id=base_material_type_attr_set_id, \
                        base_material_type_attr_id=base_material_type_attr_id,attr_value=assembly_attr_value)
                    session.add(attr_set_value)
            session.commit()
        
        logger.info('Add all assmbly attrs successfully!')
        return True

    
    @staticmethod
    def retrieve_assembly_template(ind_info,attrNameValue_dict):
        
        first_type_code = ind_info[u'first_type_code']
        second_type_code = ind_info[u'second_type_code']
        assembly_attr_names = ind_info[u'assembly_attr_names']

        logger.debug('retrieve "%s" assembly template' % assembly_attr_names)
        
        with get_session() as session:
            assembly_attr_name_list = assembly_attr_names.split()
            for assembly_attr_name in assembly_attr_name_list:
                # 对一个集成属性做分析，返回一个dict
                attrNameValue_dict[assembly_attr_name]=AssemblyTemplate.retrieve_attrName_value_dict( \
                    session,first_type_code,second_type_code,assembly_attr_name)

    @staticmethod
    def retrieve_attrName_value_dict(session,first_type_code,second_type_code,assembly_attr_name):
        attrName_value_dict=dict()
        parent_bmt = aliased(BaseMaterialType)
        be = session.query(BaseMaterialType, parent_bmt).join((parent_bmt, parent_bmt.id == BaseMaterialType.parent_id))\
                .filter(BaseMaterialType.code == second_type_code, parent_bmt.code == first_type_code).first()            
        if be:
            # import pdb;pdb.set_trace() ###
            base_material_type_id = be[0].id
            be_assembly = session.query(BaseMaterialTypeAttrSets).filter(BaseMaterialTypeAttrSets.base_material_type_id == base_material_type_id,\
                BaseMaterialTypeAttrSets.description == assembly_attr_name).first()
            if be_assembly:
                for u,a in session.query(BaseMaterialTypeAttr,AttrSetValues).\
                                    filter(BaseMaterialTypeAttr.id == AttrSetValues.base_material_type_attr_id).\
                                    filter(AttrSetValues.base_material_type_attr_set_id == be_assembly.id) .\
                                    all():
                    attrName_value_dict[u.description] = a.attr_value
                    #attrName_value_dict[u.description] = [a.attr_value]#为什么要加[]呢?
            else:
                logger.error('no corresponding entry in BaseMaterialTypeAttrSets table(MatchRule.command_assembly_attr(...) is ok)' )
        else:
            logger.error('no corresponding entry in BaseMaterialType table' )

        return attrName_value_dict

    @staticmethod
    def retrieve_lv2assembly_template(ind_info,json_result):
        first_type_code = ind_info[u'first_type_code']
        second_type_code = ind_info[u'second_type_code']
        page = ind_info[u'page']
        pagesize = ind_info[u'pagesize']

        logger.debug('retrieve (%s,%s)\'s lv2 assembly template'%(first_type_code,second_type_code))
        
        parent_bmt = aliased(BaseMaterialType)
        with get_session() as session:
            (base,parent) = session.query(BaseMaterialType, parent_bmt).join((parent_bmt, parent_bmt.id == BaseMaterialType.parent_id))\
                                    .filter(BaseMaterialType.code == second_type_code, parent_bmt.code == first_type_code).first()
            if base:
                base_material_type_id = base.id # be is 'KeyedTuple' object 
                
                bmts = session.query(BaseMaterialTypeAttrSets).\
                        filter(BaseMaterialTypeAttrSets.base_material_type_id == base_material_type_id).\
                        order_by(BaseMaterialTypeAttrSets.id.desc())
                recordNum = bmts.count()                
                json_result["record_num"] = str(recordNum)                 
                # json_result["pageNum"] = str(int(math.ceil(float(recordNum)/float(pagesize)))) 

                for assembly_attr in bmts.offset((int(page)-1)*int(pagesize)).limit(int(pagesize)).all():
                    adict = dict()
                    adict[assembly_attr.id] = assembly_attr.description 
                    json_result['lv2_id_attrValue_list'].append(adict)

            else:
                logger.error('no corresponding entry:(%s) in BaseMaterialType table' % (first_type_code+' '+second_type_code))
                pass
        return True

    @staticmethod
    def retrieve_lv2assembly_template_list(category):
        templates = list()
        first_type_code,second_type_code = category.split('.')
        # first_type_code = ind_info[u'first_type_code']
        # second_type_code = ind_info[u'second_type_code']
        # page = ind_info[u'page']
        # pagesize = ind_info[u'pagesize']

        logger.debug('retrieve (%s,%s)\'s lv2 assembly template'%(first_type_code,second_type_code))
        
        parent_bmt = aliased(BaseMaterialType)
        with get_session() as session:
            (base,parent) = session.query(BaseMaterialType, parent_bmt).join((parent_bmt, parent_bmt.id == BaseMaterialType.parent_id))\
                                    .filter(BaseMaterialType.code == second_type_code, parent_bmt.code == first_type_code).first()
            if base:
                base_material_type_id = base.id # be is 'KeyedTuple' object 
                
                bmts = session.query(BaseMaterialTypeAttrSets).\
                        filter(BaseMaterialTypeAttrSets.base_material_type_id == base_material_type_id).\
                        order_by(BaseMaterialTypeAttrSets.id.desc())
                # recordNum = bmts.count()                
                # json_result["record_num"] = str(recordNum)                 
                # json_result["pageNum"] = str(int(math.ceil(float(recordNum)/float(pagesize)))) 

                for assembly_attr in bmts.all():
                    templates.append( assembly_attr.description )
                # for assembly_attr in bmts.offset((int(page)-1)*int(pagesize)).limit(int(pagesize)).all():
                #     adict = dict()
                #     adict[assembly_attr.id] = assembly_attr.description 
                    # json_result['lv2_id_attrValue_list'].append(adict)

            else:
                logger.error('no corresponding entry:(%s) in BaseMaterialType table' % (first_type_code+' '+second_type_code))
                pass
        return templates


    @staticmethod
    def delete_assembly_template(ind_info):
        base_material_type_attr_set_id = ind_info[u'base_material_type_attr_set_id']
        # logger.debug('delete "%s" assembly template' % base_material_type_attr_set_id)

        parent_bmt = aliased(BaseMaterialType)
        with get_session() as session:
            
            be_assembly = session.query(BaseMaterialTypeAttrSets).filter(BaseMaterialTypeAttrSets.id==base_material_type_attr_set_id).first()
            if be_assembly:
                session.query(AttrSetValues).filter(AttrSetValues.base_material_type_attr_set_id==base_material_type_attr_set_id).delete()
                session.delete(be_assembly)
                session.commit()
            else:
                logger.error('no corresponding entry(%s) in BaseMaterialTypeAttrSets table' % (base_material_type_attr_set_id))
                pass


    @staticmethod
    def create_assembly_attrValPair(ind_info):
        base_material_type_attr_set_id = ind_info[u'base_material_type_attr_set_id']
        base_material_type_attr_id = ind_info[u'base_material_type_attr_id']
        assembly_attr_value = ind_info[u'assembly_attr_value']
        logger.debug('Get %s attrValue to add.' % assembly_attr_value)

        with get_session() as session:
            be = session.query(AttrSetValues).filter(AttrSetValues.base_material_type_attr_set_id == base_material_type_attr_set_id,\
                    AttrSetValues.base_material_type_attr_id == base_material_type_attr_id,\
                    AttrSetValues.attr_value == assembly_attr_value).first() ###
            if be:
                # be.attr_value=assembly_attr_value
                # session.add(be)
                logger.error("AttrSetValues already have (%s,%s,%s)"%(base_material_type_attr_set_id,base_material_type_attr_id,assembly_attr_value))
                return False
            else:
                attr_set_value = AttrSetValues(base_material_type_attr_set_id=base_material_type_attr_set_id, \
                        base_material_type_attr_id=base_material_type_attr_id,attr_value=assembly_attr_value)
                session.add(attr_set_value)
            session.commit()
        logger.info("Add all assembly attr_value_pair successfully!")
        return True
    @staticmethod
    def delete_assembly_attrValPair(ind_info):
        base_material_type_attr_set_id = ind_info[u'base_material_type_attr_set_id']
        base_material_type_attr_id = ind_info[u'base_material_type_attr_id']
        logger.debug('delete_assembly_attrValPair.')

        with get_session() as session:
            be = session.query(AttrSetValues).filter(AttrSetValues.base_material_type_attr_set_id == base_material_type_attr_set_id,\
                    AttrSetValues.base_material_type_attr_id == base_material_type_attr_id).first()
            if be:
                session.delete(be)
            else:
                logger.error("no relative item to delete in attr_set_values table") 
            session.commit()
        logger.info("delete assembly attr_value_pair successfully!")
        return True
    @staticmethod
    def delete_assembly_attrValPair_byId(ind_info):
        attr_set_value_id = ind_info[u'attr_set_value_id']
        logger.debug('delete_assembly_attrValPair.')
        with get_session() as session:
            be = session.query(AttrSetValues).filter(AttrSetValues.id == attr_set_value_id).first()
            if be:
                session.delete(be)
            else:
                logger.error("no relative item to delete in attr_set_values table") 
            session.commit()
        logger.info("delete assembly attr_value_pair successfully!")
        return True

    @staticmethod
    def retrieve_assembly_attrValPair(ind_info,assembly_attrValPair_dict):
        attr_set_value_id = ind_info['attr_set_value_id']
        logger.debug('retrieve assembly attrValPair')

        with get_session() as session:
            assembly_attrValPair_info = session.query(BaseMaterialTypeAttr,BaseMaterialTypeAttrSets,AttrSetValues).\
                                                filter(BaseMaterialTypeAttr.id == AttrSetValues.base_material_type_attr_id).\
                                                filter(BaseMaterialTypeAttrSets.id == AttrSetValues.base_material_type_attr_set_id).\
                                                filter(AttrSetValues.id == attr_set_value_id).first()
            assembly_attrValPair_dict["assemblyAttrName"]=assembly_attrValPair_info[0].description
            assembly_attrValPair_dict["assemblyAttr"]=assembly_attrValPair_info[1].description
            assembly_attrValPair_dict["assemblyAttrValue"]=assembly_attrValPair_info[2].attr_value
        logger.info('retrieve assembly attrValPair successfully')
        return assembly_attrValPair_dict

    @staticmethod
    def retrieve_assembly_attrValPairs(ind_info,json_result):
        base_material_type_attr_set_id = ind_info['base_material_type_attr_set_id']
        page_str = ind_info[u'page']
        pagesize_str = ind_info[u'pagesize']

        try:
            page = int(page_str)
            pagesize = int(pagesize_str)
        except ValueError, e:
            logger.error("ValueError: could not convert string page=%s and pagesize=%s to float"%(page_str,pagesize_str))
            
        with get_session() as session:
            be_assembly = session.query(BaseMaterialTypeAttrSets).filter(BaseMaterialTypeAttrSets.id==base_material_type_attr_set_id).first()
            if be_assembly:

                asvs = session.query(AttrSetValues).\
                            filter(AttrSetValues.base_material_type_attr_set_id == base_material_type_attr_set_id).\
                            order_by(AttrSetValues.id.desc())
                recordNum = asvs.count()
                json_result["record_num"] = str(recordNum) 
                #` json_result["pageNum"] = str(int(math.ceil(float(recordNum)/float(pagesize)))) 

                for attr_set_value in asvs.offset((page-1)*pagesize).limit(pagesize).all():
                    bmt = session.query(BaseMaterialTypeAttr).filter(BaseMaterialTypeAttr.id == attr_set_value.base_material_type_attr_id).first()
                    
                    #` json_result['assembly_id_attrNameVal_dict'][attr_set_value.id] = dict()
                    adict = dict()
                    adict[attr_set_value.id] = dict()
                    if bmt:
                        #` json_result['assembly_id_attrNameVal_dict'][attr_set_value.id][bmt.description] = attr_set_value.attr_value
                        adict[attr_set_value.id][bmt.description] = attr_set_value.attr_value
                        json_result['assembly_id_attrNameVal_list'].append(adict)
            else:
                logger.error("no relative item to delete in base_material_type_attr_sets table")
        logger.info("retrieve_assembly_attrValPairs successfully")
        return True


if __name__ == '__main__':
    pass