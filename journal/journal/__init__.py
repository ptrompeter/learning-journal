import os
from pyramid.config import Configurator

from sqlalchemy import engine_from_config

from pyramid.paster import get_appsettings

from .models import (
    DBSession,
    Base,
    )


def make_session(settings):
    from sqlalchemy.orm import sessionmaker
    engine = engine_from_config(settings, 'sqlalchemy.')
    Session = sessionmaker(bind=engine)
    return Session()


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    database_url = os.environ.get('JOURNAL_DB', None)
    if database_url is not None:
        settings['sqlalchemy.url'] = database_url

    # settings = get_appsettings(config_uri, options=options)
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    config = Configurator(settings=settings)
    config.include('pyramid_jinja2')
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('compose', '/compose')
    config.add_route('entry', '/entries/{entry_id}')
    config.add_route('edit', '/edit/{entry_id}')
    config.scan()
    return config.make_wsgi_app()
