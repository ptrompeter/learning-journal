# _*_ Coding: utf-8 _*_

import os

USERS = {os.environ.get('MY_NAME'):['group:editor']
        }

def groupfinder(userid, request):
    if userid in USERS:
        return USERS.get(userid, [])

