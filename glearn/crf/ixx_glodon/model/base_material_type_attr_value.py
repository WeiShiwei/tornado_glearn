from sqlalchemy import Column, Integer, Unicode, ForeignKey
from model.base import Base
from sqlalchemy.orm import sessionmaker, relationship
from model.base_material_type_attr import *

class BaseMaterialTypeAttrValue(Base):
    __tablename__ = 'base_material_type_attr_values'

    id = Column(Integer, primary_key=True)
    description = Column(Unicode(128), nullable=True)
    base_material_type_attr_id = Column(Integer, ForeignKey("base_material_type_attrs.id"))
    # base_material_type_attr = relationship(BaseMaterialTypeAttr, primaryjoin=base_material_type_attr_id == BaseMaterialTypeAttr.id)

    def __eq__(self, other):
        return self.base_material_type_attr_id == other.base_material_type_attr_id and self.description == other.description

