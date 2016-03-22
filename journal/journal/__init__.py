import os
from pyramid.config import Configurator
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy

from sqlalchemy import engine_from_config

from journal.security import groupfinder

from pyramid.paster import get_appsettings

from cryptacular.bcrypt import BCRYPTPasswordManager

from .models import (
    DBSession,
    Base,
    RootFactory
    )

manager = BCRYPTPasswordManager()


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
    authn_policy = AuthTktAuthenticationPolicy(
        'icanhazpws', callback=groupfinder, hashalg='sha512')
    authz_policy = ACLAuthorizationPolicy()
    settings['auth.username'] = os.environ.get('MY_NAME', 'edit')
    settings['auth.password'] = os.environ.get('MY_PASSWORD', 'secret')
    config = Configurator(settings=settings,
        root_factory=RootFactory)
    config.set_authentication_policy(authn_policy)
    config.set_authorization_policy(authz_policy)
    config.include('pyramid_jinja2')
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('compose', '/compose')
    config.add_route('entry', '/entries/{entry_id}')
    config.add_route('edit', '/edit/{entry_id}')
    config.add_route('login', '/login')
    config.add_route('logout', '/logout')
    config.add_route('forbidden', '/forbidden')
    config.scan()
    return config.make_wsgi_app()
