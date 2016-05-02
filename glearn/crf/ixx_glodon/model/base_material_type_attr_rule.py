from sqlalchemy import Column, Integer, Unicode, ForeignKey
from model.base import Base
from sqlalchemy.orm import sessionmaker, relationship
from model.base_material_type_attr import *

class BaseMaterialTypeAttrRule(Base):
    __tablename__ = 'base_material_type_attr_rules'

    id = Column(Integer, primary_key=True)
    rule_description = Column(Unicode(128), nullable=True)
    base_material_type_attr_id = Column(Integer, ForeignKey("base_material_type_attrs.id"))
    # base_material_type_attr = relationship(BaseMaterialTypeAttr, primaryjoin=base_material_type_attr_id == BaseMaterialTypeAttr.id)