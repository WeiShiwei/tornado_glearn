# coding=utf-8
u"""
User: xulin
Date: 13-6-6
Time: 上午11:08
"""
import datetime
from sqlalchemy import Column, DateTime, text
from sqlalchemy.ext.declarative import declarative_base


class TBase(object):
    created_date = Column(DateTime, default=datetime.datetime.now)
    modified_date = Column(DateTime, default=datetime.datetime.now, onupdate=text('current_timestamp'))


Base = declarative_base(cls=TBase)


if __name__ == '__main__':
    pass