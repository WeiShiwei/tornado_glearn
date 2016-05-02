# coding=utf-8
import os

"""开发环境使用的配置
"""

DB_DEBUG = False

DB = 'ml_2013'
HOST = '127.0.0.1'
USER = 'postgres'
PASSWD = 'postgres'
CONNECT_STRING = 'postgresql+psycopg2://%s:%s@%s/%s' % (USER, PASSWD, HOST, DB)