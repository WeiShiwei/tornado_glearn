# coding=utf-8
u"""
User: weishiwei
Date: 14-06-16
Time: 上午10:45
"""
import os

ENV = os.environ.get('API_ENV', 'development')

print 'API: %s' % ENV

if ENV == 'development':
    import development as config
if ENV == 'production':
    import production as config
