# coding=utf-8

"""生产环境使用的配置
"""

DB_DEBUG = False
DB = 'glodon_ixx_production'
HOST = '192.168.178.19'
USER = 'zhangwh'
PASSWD = 'www.zhangwh.c0m'
CONNECT_STRING = 'mysql://%s:%s@%s/%s?charset=utf8' % (USER, PASSWD, HOST, DB)
