# _*_ Coding: utf-8 _*_

import os
# from . import manager
from cryptacular.bcrypt import BCRYPTPasswordManager


manager = BCRYPTPasswordManager()


def check_pw(pw):
    return manager.check(os.environ.get('MY_PASSWORD'), pw)
