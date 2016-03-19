# -*- coding: utf-8 -*-
import pytest
import os
from sqlalchemy import create_engine

from journal.models import DBSession, Base


TEST_DATABASE_URL = os.environ.get('JOURNAL_DB_TEST')


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
def new_entry(dbtransaction):
    from journal.models import Entry, DBSession
    entry = Entry(title='test title', text='test text')
    DBSession.add(entry)
    DBSession.flush()
    return entry
