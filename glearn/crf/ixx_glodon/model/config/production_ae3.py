# coding=utf-8

"""生产环境使用的配置
"""

DB_DEBUG = False
DB = 'attr_detect_ml3'
HOST = '192.168.178.19'
USER = 'db_ae3'
PASSWD = '632#ae931gld'
CONNECT_STRING = 'mysql://%s:%s@%s/%s?charset=utf8' % (USER, PASSWD, HOST, DB)

