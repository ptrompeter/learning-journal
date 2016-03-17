from pyramid.response import Response
from pyramid.view import view_config

from sqlalchemy.exc import DBAPIError

from .models import (
    DBSession,
    Entry,
    )


@view_config(route_name='home', renderer='templates/home.jinja2')
def my_view(request):
    try:
        all_entries = DBSession.query(Entry).all()
        return {'entries': all_entries}
    except DBAPIError:
        return Response("shit broke", content_type='text/plain', status_int=500), request


@view_config(route_name='compose', renderer='templates/base.jinja2')
def compose(request):
    try:
        return {'content': "this is the compose page."}
    except DBAPIError:
        return Response("shit broke", content_type='text/plain', status_int=500), request
