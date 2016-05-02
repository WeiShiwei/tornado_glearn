#!/usr/bin/env python
# #_*_ coding: utf-8 _*_
from datetime import datetime

from sqlalchemy import update

from sqlalchemy import (create_engine, MetaData, Table, Column, Integer, Boolean,Unicode,
    String, DateTime, Float, ForeignKey, and_)
from sqlalchemy.orm import mapper, relationship, sessionmaker, backref,\
                           joinedload_all
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.sql import func , distinct

from sqlalchemy.orm import aliased

import os
import random

import sys
sys.path.append( os.path.join( os.path.abspath(os.path.dirname(__file__)) , '../..'))

# ---------------------------------------------
from glearn.crf.config import config, ENV
if ENV == 'development':
    engine = create_engine(
        config.CONNECT_STRING, # PostgreSQL数据库ml_2013（本地）
        echo=config.DB_DEBUG
    )
else:
    engine = create_engine(
        config.CONNECT_STRING, # 结构化新平台的数据库db_structure_glodon_com
        echo=config.DB_DEBUG,
        pool_recycle=3600,
        pool_size=15
    )
Base = declarative_base(engine)
session = sessionmaker(bind=engine)()

# ENV = os.environ.get('API_ENV', 'development')
# if ENV == 'development':
#   # for development
#   db = create_engine('postgresql+psycopg2://postgres:postgres@localhost/ml_2013' , echo=False)
# else:
#   # for production
#   db = create_engine('postgresql+psycopg2://gcj:Gl0147D0n258@192.168.10.14/ml_2013' , echo=False)

# Base = declarative_base(db)
# session = sessionmaker(bind=db)()
# ---------------------------------------------

class CrfTrainSample( Base ):
  __tablename__ = 'crf_train_samples'
  id = Column(Integer, primary_key=True)
  first_type_code = Column( String )
  second_type_code = Column( String )
  content = Column( String )
  raw_content = Column( String )
  status = Column( String )

  # def segment_raw_content_and_save( self ):
  #   raw_path = os.path.join( gv.data_path , 'raw_' + str(self.id) + '.txt' )
  #   raw_file = open(raw_path,"w")
    
  #   raw_file.write( self.content.encode('utf-8') )
  #   raw_file.close()
  #   segmented_path = os.path.join( gv.data_path , 'segmented_' + str(self.id) + '.txt' )
  #   crfpputil.segment_for_labeling( raw_path , segmented_path)
  #   segmented_file = open(segmented_path , 'r')
  #   self.content = segmented_file.read()
  #   self.status = 'segmented'
    
  #   session.add(self)
  #   session.commit()
    
  #   segmented_file.close()
  #   os.remove( raw_path )
  #   os.remove( segmented_path )
# Table name: crf_train_sample_items
#
#  id                  :integer          not null, primary key
#  first_type_code     :string(255)
#  second_type_code    :string(255)
#  content             :text
#  attr_hash           :text
#  crf_model_id        :integer
#  crf_train_sample_id :integer
#  status              :string(255)
#  created_at          :datetime         not null
#  updated_at          :datetime         not null

  

class CrfTrainSampleItem( Base ):
  __tablename__ = 'crf_train_sample_items'
  id = Column(Integer, primary_key=True)
  first_type_code = Column( String )
  second_type_code = Column( String )
  content = Column( String )
  raw_content = Column( String )
  weight = Column( Integer )
  crf_model_id = Column( Integer )
  crf_train_sample_id = Column( Integer )
  status = Column( String )
  
  @classmethod
  def contents_for_train( cls , cm_id ):
    content_samples_list = list()
    for item in session.query( cls ).filter_by( crf_model_id=cm_id ).filter_by( status= 'validated' ):
      content_samples_list.append(item.content)
    return content_samples_list
  
  @classmethod
  def contents_for_validates( cls , cm_id , count ):
    samples = [ [item.content , item.raw_content] for item in session.query( cls ).filter_by( crf_model_id=cm_id ).filter_by( status= 'validated' )]
    random.shuffle( samples )
    samples = samples[0:count]
    labeled_samples = list()
    raw_samples = list()
    for s in samples:
      labeled_samples.append( s[0] )
      raw_samples.append( s[1] )
    return raw_samples , labeled_samples

    @classmethod
    def contents_for_cross_validate(cls,cm_id):
      cross_validate_samples = list()
      for item in session.query(cls).filter(crf_model_id == cm_id).all():
        cross_validate_samples.append(item.content)
      return cross_validate_samples

    @classmethod
    def fetch_all_model_ids(cls):
      model_ids = list()
      # session.query(cls).
      session.query(distinct(cls.crf_model_id))


class CrfModel( Base ):
  __tablename__ = 'crf_models'
  id = Column(Integer, primary_key=True)
  first_type_code = Column( String )
  second_type_code = Column( String )
  status = Column( String )

  @classmethod
  def get_code_tuple(cls,cm_id):
    crf_model = session.query(cls).filter_by(id=cm_id).first()
    return (crf_model.first_type_code,crf_model.second_type_code)
  @classmethod
  def fetch_crfModelId_category_dict(cls):
    crfModelId_category_dict = dict()

    crf_models = session.query(cls).all()
    for model in crf_models:
      crfModelId_category_dict[unicode(model.id)] = unicode(model.first_type_code+'.'+model.second_type_code)
    return crfModelId_category_dict

  @classmethod
  def get_crf_model_id(cls, first_type_code, second_type_code):
    crf_model = session.query(cls).filter_by(first_type_code=first_type_code,second_type_code=second_type_code).first()
    return crf_model.id

  @classmethod
  def fetch_all_code(cls):
    code_tuple_list = list()

    code_tuple_set = set()
    crf_models = session.query(cls).all()
    for model in crf_models:
      # code_tuple_list.append((model.first_type_code,model.second_type_code))
      code_tuple_set.add((model.first_type_code,model.second_type_code))

    code_tuple_list = list(code_tuple_set)
    return code_tuple_list

  @classmethod
  def fetch_all_model_ids(cls):
    # model_id_list = list()
    return [obj[0] for obj in session.query(distinct(cls.id)).order_by(cls.id).all()]

# --------------------------------------------------------------------------------------------------------

class BaseMaterialType(Base):
    __tablename__ = 'base_material_types'

    id = Column(Integer, primary_key=True)
    code = Column(Unicode(4), nullable=True)
    description = Column(Unicode(128), nullable=True)
    parent_id = Column(Integer, ForeignKey("base_material_types.id"))
    
    # base_material_type_attrs = relationship("BaseMaterialTypeAttr", backref="base_material_type")
    children = relationship("BaseMaterialType", lazy="joined", join_depth=2)
    parent = relationship('BaseMaterialType', remote_side=[id])

    def __eq__(self, other):
        return self.code == other.code and self.description == other.description


class BaseMaterialTypeAttr( Base ):
  __tablename__ = 'base_material_type_attrs'
  id = Column(Integer, primary_key=True)
  description = Column( String )
  base_material_type_id = Column(Integer)
  code = Column( String )

  @classmethod
  def get_chunkTag_attrName_dict(cls,first_type_code,second_type_code):
    chunkTag_attrName_dict = dict()

    parent_bmt = aliased(BaseMaterialType)
    be = session.query(BaseMaterialType, parent_bmt).join((parent_bmt, parent_bmt.id == BaseMaterialType.parent_id))\
            .filter(BaseMaterialType.code == second_type_code, parent_bmt.code == first_type_code).first()            
    if be:
      base_material_type_id = be[0].id
      items = session.query(cls).filter_by(base_material_type_id=base_material_type_id)
      for item in items:
        chunkTag_attrName_dict[item.code] = item.description
      return chunkTag_attrName_dict
    else:
      print 'no corresponding entry in BaseMaterialType table'
      return {}
