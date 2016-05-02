# coding=utf-8
u"""
User: xulin
Date: 13-5-29
Time: 上午8:05
"""
import os

ENV = os.environ.get('EXTRACTOR_ENV', 'development')

print 'EXTRACTOR: %s' % ENV

if ENV == 'development':
    import development as config
if ENV == 'production':
    import production as config
