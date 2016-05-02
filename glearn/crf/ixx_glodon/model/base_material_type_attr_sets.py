# coding=utf-8

from sqlalchemy import Column, Integer, Unicode, ForeignKey, Boolean
from model.base import Base
from sqlalchemy.orm import sessionmaker, relationship, mapper


class BaseMaterialTypeAttrSets(Base):
    __tablename__ = 'base_material_type_attr_sets'

    id = Column(Integer, primary_key = True)
    description = Column(Unicode(128),nullable=True)
    base_material_type_id = Column(Integer, ForeignKey("base_material_types.id"))
    
    attr_set_values = relationship("AttrSetValues",backref = "base_material_type_attr_set")

    def __eq__(self, other):
        return self.base_material_type_id == other.base_material_type_id and self.description == other.description


    @classmethod
    def update_assembly_template(assmblyTemplate,base_material_type_id,base_material_type_attr_id):
    	""""""
    	lv1_id = assmblyTemplate[u'first_type_code']
    	lv2_id = assmblyTemplate[u'second_type_code']
    	assembly_attr_name = assmblyTemplate["assembly_attr_name"]
    	assembly_attr_val = assmblyTemplate["assembly_attr_val"]
    	

