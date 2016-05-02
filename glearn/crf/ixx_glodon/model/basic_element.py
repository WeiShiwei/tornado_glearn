from sqlalchemy import Column, Integer, Unicode
from model.base import Base


class BasicElement(Base):
    __tablename__ = 'basic_element'

    unique_id = Column(Integer, primary_key=True)
    lv1_id = Column(Unicode(4), nullable=False)
    lv2_id = Column(Unicode(4), nullable=False)
    lv1_name = Column(Unicode(128), nullable=True)
    lv2_name = Column(Unicode(128), nullable=True)
    attr_name = Column(Unicode(128), nullable=False)
    attr_val = Column(Unicode(10240), nullable=True)
