import os
from sqlalchemy import engine_from_config
from pyramid.config import Configurator
from .models import (
    DBSession,
    Base,
    )

from .security import DefaultRoot
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy


def make_session(settings):
    from sqlalchemy.orm import sessionmaker
    engine = engine_from_config(settings, 'sqlalchemy.')
    Session = sessionmaker(bind=engine)
    return Session()


def main(global_config, **settings):
    """This function returns a Pyramid WSGI application."""
    database_url = os.environ.get('JOURNAL_DB', None)
    if database_url is not None:
        settings['sqlalchemy.url'] = database_url

    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine

    settings['auth.username'] = os.environ.get('AUTH_USERNAME', 'admin')
    settings['auth.password'] = os.environ.get('AUTH_PASSWORD', 'secret')
    auth_secret = os.environ.get('JOURNAL_AUTH_SECRET', 'words')
    authn_policy = AuthTktAuthenticationPolicy(
                                              secret=auth_secret,
                                              hashalg='sha512'
                                              )
    authz_policy = ACLAuthorizationPolicy()
    config = Configurator(
                    settings=settings,
                    authentication_policy=authn_policy,
                    authorization_policy=authz_policy,
                    root_factory=DefaultRoot,
                    )
    config.include('pyramid_jinja2')
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('login', '/login')
    config.add_route('logout', '/logout')
    config.add_route('compose', '/compose')
    config.add_route('edit', '/edit/{entry_id}')
    config.add_route('entry', '/entries/{entry_id}')
    config.scan()
    return config.make_wsgi_app()
