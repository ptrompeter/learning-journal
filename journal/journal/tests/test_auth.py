# _*_ Coding: utf-8 _*_

import os
from journal.views import login, compose, edit_entry
from pyramid.testing import DummyRequest

def test_get_name():
    assert os.environ.get('MY_NAME') is not None

def test_get_pw():
    assert os.environ.get('MY_PASSWORD') is not None

def test_login