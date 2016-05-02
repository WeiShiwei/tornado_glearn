from sqlalchemy import Column, Integer, Unicode, ForeignKey, Boolean
from model.base import Base
from sqlalchemy.orm import sessionmaker, relationship, mapper


class BaseMaterialType(Base):
    __tablename__ = 'base_material_types'

    id = Column(Integer, primary_key=True)
    code = Column(Unicode(4), nullable=True)
    description = Column(Unicode(128), nullable=True)
    parent_id = Column(Integer, ForeignKey("base_material_types.id"))
    
    base_material_type_attrs = relationship("BaseMaterialTypeAttr", backref="base_material_type")
    children = relationship("BaseMaterialType", lazy="joined", join_depth=2)
    parent = relationship('BaseMaterialType', remote_side=[id])

    #-----------------------------------------------------------
    base_material_type_attr_sets = relationship("BaseMaterialTypeAttrSets",backref = "base_material_type")
    #-----------------------------------------------------------

    def __eq__(self, other):
        return self.code == other.code and self.description == other.description

        