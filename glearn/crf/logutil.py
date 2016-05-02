#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging

def create_log(name):
    new_log = logging.getLogger(name)
    # from logging.handlers import SMTPHandler
    # mail_handler = SMTPHandler('127.0.0.1',
    #                            'server-error@example.com',
    #                            ADMINS, 'YourApplication Failed')
    # mail_handler.setLevel(logging.ERROR)

    app_formatter = logging.Formatter("%(asctime)s\t%(process)d|%(thread)d\t%(module)s|%(funcName)s|%(lineno)d"
                                      "\t%(levelname)s\t%(message)s", "%Y-%m-%d@%H:%M:%S")
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(app_formatter)
    # console_handler.setLevel(logging.WARN)
    console_handler.setLevel(logging.INFO)

    new_log.propagate = False
    new_log.addHandler(console_handler)
    # app.logger.addHandler(mail_handler)
    new_log.setLevel(logging.WARN)

    return new_log

logger = create_log('crf')