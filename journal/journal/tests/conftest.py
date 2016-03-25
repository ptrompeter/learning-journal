# -*- coding: utf-8 -*-
import pytest
import os
from sqlalchemy import create_engine
from journal.models import DBSession, Base
from pyramid.testing import DummyRequest
from pyramid.testing import setUp
from webob import multidict

TEST_DATABASE_URL = os.environ.get('JOURNAL_DB_TEST')
AUTH_DATA = {'username': 'admin', 'password': 'secret'}


@pytest.fixture(scope='session')
def sqlengine(request):
    engine = create_engine(TEST_DATABASE_URL)
    DBSession.configure(bind=engine)
    Base.metadata.create_all(engine)

    def teardown():
        Base.metadata.drop_all(engine)

    request.addfinalizer(teardown)
    return engine


@pytest.fixture()
def dbtransaction(request, sqlengine):
    connection = sqlengine.connect()
    transaction = connection.begin()
    DBSession.configure(bind=connection)

    def teardown():
        transaction.rollback()
        connection.close()
        DBSession.remove()

    request.addfinalizer(teardown)

    return connection


@pytest.fixture()
def app(dbtransaction):
    from webtest import TestApp
    from journal import main
    fake_settings = {'sqlalchemy.url': TEST_DATABASE_URL}
    os.environ['JOURNAL_DB'] = TEST_DATABASE_URL
    app = main({}, **fake_settings)
    return TestApp(app)


@pytest.fixture()
def auth_env():
        from passlib.apps import custom_app_context as pwd_context
        os.environ['AUTH_PASSWORD'] = pwd_context.encrypt('secret')
        os.environ['AUTH_USERNAME'] = 'admin'


@pytest.fixture()
def authenticated_app(app, auth_env):
    app.post('/login', AUTH_DATA)
    return app


@pytest.fixture()
def new_entry(dbtransaction):
    from journal.models import Entry, DBSession
    entry = Entry(title='test title', text='test text')
    DBSession.add(entry)
    DBSession.flush()
    return entry


@pytest.fixture()
def dummy_post_request():
    """Make a Dummy Request that will mimic a POST method request"""
    req = DummyRequest()
    config = setUp()
    config.add_route('add', '/compose')
    config.add_route('detail', '/entries/{entry_id}')
    config.add_route('edit', '/edit/{entry_id}')
    config.add_route('entry', '/entries/{entry_id}')
    req.method = 'POST'
    test_dict = [('title', 'test title'), ('text', 'test text')]
    mdict = multidict.MultiDict(test_dict)
    req.POST = mdict
    return req
