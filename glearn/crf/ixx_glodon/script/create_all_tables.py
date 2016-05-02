# coding=utf-8
u"""
User: xulin
Date: 13-12-25
"""
import os, sys
sys.path.append( os.path.join( os.path.abspath(os.path.dirname(__file__)) , '..'))

#import model

from model.base import Base
from model.session import engine
from model.basic_element import BasicElement


Base.metadata.create_all(engine)
