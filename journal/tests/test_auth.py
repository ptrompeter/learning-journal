# _*_ Coding: utf-8 _*_

import os
from journal.views import login, compose, edit_entry
from pyramid.testing import DummyRequest

AUTH_DATA = {'login': os.environ.get('MY_NAME'), 'password':'4lld4pws'}

def test_get_name():
    assert os.environ.get('MY_NAME') is not None

def test_get_pw():
    assert os.environ.get('MY_PASSWORD') is not None

def test_check_pw():
    from ..security import check_pw
    assert check_pw('4lld4pws')

def test_login_status(app):
    response = app.post('/login', AUTH_DATA)
    assert response.status_code == 302
    
def test_login_sets_cookie(app):
    """Test that an auth_tkt cookie is set following successful login"""
    response = app.post('/login', AUTH_DATA)
    headers = response.headers
    cookies = headers.getall('set-cookie')
    for cookie in cookies:
        if cookie.startswith('auth_tkt'):
            break
    else: assert False

def test_persistant_cookie(app):
    """Test that, following a login, a auth tkt appears in the following request."""
    response = app.post('/login', AUTH_DATA).follow()
    assert response.request.cookies['auth_tkt'] is not None

def test_login_fail(app):
    response = app.post('/login', {'login': os.environ.get('MY_NAME'), 'password': 'unpassword'})
    assert response.status_code == 200
    assert b"Login failed.  Try Again." in response.body

def test_post_login_success_redir_home(app):
    response = app.post('/login', AUTH_DATA)
    headers = response.headers
    domain = 'http://localhost'
    actual_path = headers.get('Location', '')[len(domain):]
    assert actual_path == '/'





