# coding=utf-8
u"""
Description: Test the main functions of template.
User: Jerry.Fang
Date: 13-12-30
"""
import os, sys
sys.path.append( os.path.join( os.path.abspath(os.path.dirname(__file__)) , '../..'))

import requests
import ujson
import unittest

from template.basic_template_generator import BasicTemplate
from template.basic_template_updater import TemplateUpdater
from model.session import *
from model.basic_element import BasicElement
from model.base_material_type import *
from model.base_material_type_attr import *
from model.base_material_type_attr_value import *
from model.base_material_type_attr_rule import *
from model.base_material_type_attr_key_word import *
from sqlalchemy.orm import aliased

m_basic_template = BasicTemplate()
m_basic_template.set_primary_path( os.path.join( os.path.abspath(os.path.dirname(__file__)) , 'bmt-changed.xls') )

m_basic_template.generate_basic_template()
m_basic_template.gen_attr_rule_in_all_basic_template()