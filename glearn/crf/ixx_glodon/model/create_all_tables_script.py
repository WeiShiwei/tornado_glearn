#coding=utf-8
import os, sys
sys.path.append( os.path.join( os.path.abspath(os.path.dirname(__file__)) , '../'))

import datetime
from sqlalchemy import *
from sqlalchemy import Column, DateTime, text
from sqlalchemy.orm import sessionmaker

from model.config import config, ENV
if ENV == 'development':
    engine = create_engine(
        config.CONNECT_STRING,
        echo=config.DB_DEBUG
    )
else:
    engine = create_engine(
        config.CONNECT_STRING,
        echo=config.DB_DEBUG,
        pool_recycle=3600,
        pool_size=15
    )

metadata = MetaData()

base_material_types = Table('base_material_types', metadata,
    Column('id', Integer, primary_key = True),
    Column('code', String(4), nullable = True),
    Column('description', String(255)),
    Column('parent_id', Integer, nullable = True),
    Column('created_date', DateTime, default=datetime.datetime.now),
    Column('modified_date', DateTime, onupdate=datetime.datetime.now)
)

base_material_type_attrs = Table('base_material_type_attrs', metadata,
    Column('id', Integer, primary_key = True),
    Column('description', String(255)),
    Column('base_material_type_id', Integer, nullable = False),
    Column('is_all_match', Boolean, default = 1),
    Column('created_date', DateTime, default=datetime.datetime.now),
    Column('modified_date', DateTime, onupdate=datetime.datetime.now)
)

base_material_type_attr_values = Table('base_material_type_attr_values', metadata,
    Column('id', Integer, primary_key = True),
    Column('description', String(255)),
    Column('base_material_type_attr_id', Integer, nullable = False),
    Column('created_date', DateTime, default=datetime.datetime.now),
    Column('modified_date', DateTime, onupdate=datetime.datetime.now)
)

base_material_type_attr_rules = Table('base_material_type_attr_rules', metadata,
    Column('id', Integer, primary_key = True),
    Column('rule_description', String(255)),
    Column('base_material_type_attr_id', Integer, nullable = False),
    Column('created_date', DateTime, default=datetime.datetime.now),
    Column('modified_date', DateTime, onupdate=datetime.datetime.now)
)

base_material_type_attr_key_words = Table('base_material_type_attr_key_words', metadata,
    Column('id', Integer, primary_key = True),
    Column('key_words', String(255)),
    Column('base_material_type_attr_id', Integer, nullable = False),
    Column('created_date', DateTime, default=datetime.datetime.now),
    Column('modified_date', DateTime, onupdate=datetime.datetime.now)
)
#----------------------------------------------------------------------------------
base_material_type_attr_sets = Table('base_material_type_attr_sets', metadata,
    Column('id', Integer, primary_key = True),
    Column('base_material_type_id', Integer),
    Column('description', String(255)),
    Column('created_date', DateTime, default=datetime.datetime.now),
    Column('modified_date', DateTime, onupdate=datetime.datetime.now)
)

attr_set_values = Table('attr_set_values', metadata,
    Column('id', Integer, primary_key = True),
    Column('base_material_type_attr_set_id', Integer),
    Column('base_material_type_attr_id', Integer),
    Column('attr_value', String(255)),
    Column('created_date', DateTime, default=datetime.datetime.now),
    Column('modified_date', DateTime, onupdate=datetime.datetime.now)
)
#----------------------------------------------------------------------------------

metadata.create_all(engine)
