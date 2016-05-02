# coding=utf-8

from sqlalchemy import Column, Integer, Unicode, ForeignKey, Boolean
from model.base import Base
from sqlalchemy.orm import sessionmaker, relationship, mapper

class AttrSetValues(Base):
    __tablename__ = 'attr_set_values'

    id = Column(Integer, primary_key = True)
    base_material_type_attr_set_id = Column(Integer, ForeignKey("base_material_type_attr_sets.id"))
    base_material_type_attr_id = Column(Integer, ForeignKey("base_material_type_attrs.id"))
    attr_value = Column(Unicode(128), nullable=True)

    def __eq__(self, other):
        return self.base_material_type_attr_id ==other.base_material_type_attr_id and \
            self.base_material_type_attr_set_id ==other.base_material_type_attr_set_id  and \
            self.attr_value==other.attr_value
