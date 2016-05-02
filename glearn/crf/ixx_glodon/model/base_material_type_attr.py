from sqlalchemy import Column, Integer, Unicode, ForeignKey
from model.base import Base
from sqlalchemy.orm import sessionmaker, relationship
from model.base_material_type import *

class BaseMaterialTypeAttr(Base):
    __tablename__ = 'base_material_type_attrs'

    id = Column(Integer, primary_key=True)
    description = Column(Unicode(128), nullable=True)
    base_material_type_id = Column(Integer, ForeignKey("base_material_types.id"))
    # base_material_type = relationship(BaseMaterialType, primaryjoin=base_material_type_id == BaseMaterialType.id)
    is_all_match = Column(Boolean, default=1)

    base_material_type_attr_values = relationship("BaseMaterialTypeAttrValue", backref="base_material_type_attr")
    base_material_type_attr_rules = relationship("BaseMaterialTypeAttrRule", backref="base_material_type_attr")
    base_material_type_attr_key_words = relationship("BaseMaterialTypeAttrKeyWord", backref="base_material_type_attr")
    #--------------------------------------------------------
    attr_set_values = relationship("AttrSetValues",backref = "base_material_type_attr")
    #--------------------------------------------------------

    def __eq__(self, other):
        return self.base_material_type_id == other.base_material_type_id and self.description == other.description