#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
"""
"""
DB_DEBUG = False
DB = os.path.join( os.path.abspath(os.path.dirname(__file__)) , 'db' , 'crf.db')
HOST = '127.0.0.1'
USER = 'glodon'
PASSWD = 'glodon'
CONNECT_STRING = 'sqlite:///' + DB
