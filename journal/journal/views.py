import transaction
from pyramid.response import Response
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from wtforms import Form, StringField, TextAreaField, validators
from jinja2 import Markup
import markdown

from sqlalchemy.exc import DBAPIError

from .models import (
    DBSession,
    Entry,
    )

class NewEntry(Form):
    title = StringField('title', [validators.Length(min=1, max=128)])
    text = TextAreaField('text')


@view_config(route_name='home', renderer='templates/home.jinja2')
def my_view(request):
    try:
        all_entries = DBSession.query(Entry).order_by(Entry.id.desc()).all()
        return {'entries': all_entries}
    except DBAPIError:
        return Response("home broke", content_type='text/plain', status_int=500)


@view_config(route_name='entry', renderer='templates/entry.jinja2', match_param="entry_id=latest")
def new_entry_redirect(request):
    try:
        # entry_id = request.matchdict['entry_id']
        entry = DBSession.query(Entry).order_by(Entry.id.desc()).first()
        return {'entry': entry}
    except DBAPIError:
        return Response("new broke", content_type='text/plain', status_int=500)


@view_config(route_name='entry', renderer='templates/entry.jinja2')
def entry_detail(request):
    try:
        entry_id = request.matchdict['entry_id']
        entry = DBSession.query(Entry).get(entry_id)
        entry.text = render_markdown(entry.text)
        return {'entry': entry}
    except DBAPIError:
        return Response("detail broke", content_type='text/plain', status_int=500)


@view_config(route_name='compose', renderer='templates/compose.jinja2')
def compose(request):
    try:
        new_entry = NewEntry(request.POST)
        if request.method == 'POST' and new_entry.validate():
            entry = Entry()
            entry.title = new_entry.title.data
            entry.text = new_entry.text.data
            DBSession.add(entry)
            DBSession.flush()
            entry_id = entry.id
            transaction.commit()

            # latest_entry = DBSession.query(Entry).order_by(Entry.id.desc()).first()
            # url = request.route_url('entry', entry_id=latest_entry.id)

            url = request.route_url('entry', entry_id=entry_id)
            return HTTPFound(location=url)

        return {'new_entry': new_entry}
    except DBAPIError:
        return Response("compose broke", content_type='text/plain', status_int=500)


@view_config(route_name='edit', renderer='templates/compose.jinja2')
def edit(request):
    try:
        entry_id = request.matchdict['entry_id']
        entry = DBSession.query(Entry).get(entry_id)
        entry_edit = NewEntry(request.POST, entry)
        if request.method == 'POST' and entry_edit.validate():
            entry_edit.populate_obj(entry)
            DBSession.add(entry)
            DBSession.flush()
            transaction.commit()

            url = request.route_url('entry', entry_id=entry_id)
            return HTTPFound(location=url)

        return {'new_entry': entry_edit}
    except DBAPIError:
        return Response("edit broke", content_type='text/plain', status_int=500)


def render_markdown(content):
    output = Markup(markdown.markdown(content))
    return output
