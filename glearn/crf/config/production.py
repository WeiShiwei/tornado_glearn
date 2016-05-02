# coding=utf-8

"""生产环境使用的配置
"""


DB_DEBUG = False
DB = 'db_structure_glodon_com'
HOST = 'rds.glodon.com:3321'
USER = 'dwglodonc0m'
PASSWD = 'dwdbadmin'
CONNECT_STRING = 'mysql://%s:%s@%s/%s?charset=utf8' % (USER, PASSWD, HOST, DB)


# DB = 'ml_2013'
# HOST = '192.168.10.14'
# USER = 'gcj'
# PASSWD = 'Gl0147D0n258'
# CONNECT_STRING = 'postgresql+psycopg2://%s:%s@%s/%s' % (USER, PASSWD, HOST, DB)