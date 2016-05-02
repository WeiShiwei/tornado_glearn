# coding=utf-8
import os

"""开发环境使用的配置
"""

# DB_DEBUG = False
# DB = os.path.join( os.path.abspath(os.path.dirname(__file__)) , '../..' , 'db' , 'glodon_db')
# HOST = '127.0.0.1'
# USER = 'glodon'
# PASSWD = 'glodon'
# CONNECT_STRING = 'sqlite:///' + DB
#"sqlite:///F:/personal/python/InputFile_test/glodon_db"

DB_DEBUG = False
DB = 'glodon_ixx_production'
HOST = '127.0.0.1'
USER = 'root'
PASSWD = 'weihaixin'
CONNECT_STRING = 'mysql://%s:%s@%s/%s?charset=utf8' % (USER, PASSWD, HOST, DB)