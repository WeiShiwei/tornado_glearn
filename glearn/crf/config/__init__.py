# coding=utf-8
u"""
User: xulin
Date: 13-6-6
Time: 上午11:19
"""

import os
from . import development as config, production

ENV = os.environ.get('MODEL_ENV', 'development')

print 'MODEL: %s' % ENV

if ENV == 'development':
    import development as config
if ENV == 'production':
    import production as config
