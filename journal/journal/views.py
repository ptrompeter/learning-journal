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
    import pdb
    try:
        new_entry = NewEntry(request.POST)
        if request.method == 'POST' and new_entry.validate():
            # pdb.set_trace()
            entry = Entry()
            entry.title = new_entry.title.data
            entry.text = new_entry.text.data
            DBSession.add(entry)
            DBSession.flush()
            entry_id = entry.id
            url = request.route_url('entry', entry_id=entry_id)
            return HTTPFound(location=url)

        return {'new_entry': new_entry, 'request': request}
    except DBAPIError:
        return Response("compose broke", content_type='text/plain', status_int=500)


@view_config(route_name='edit', renderer='templates/edit.jinja2')
def edit_entry(request):
    try:
        entry_id = request.matchdict['entry_id']
        post_for_editing = DBSession.query(Entry).get(entry_id)
        new_entry = NewEntry(request.POST, post_for_editing)

        if request.method == 'POST' and new_entry.validate():
            new_entry.populate_obj(post_for_editing)
            DBSession.add(post_for_editing)
            DBSession.flush()
            url = request.route_url('entry', entry_id=entry_id)
            return HTTPFound(location=url)
        return {'new_entry': new_entry, 'entry': entry_id}
    except DBAPIError:
        return Response("edit broke", content_type='text/plain', status_int=500)


def render_markdown(content):
    output = Markup(markdown.markdown(content))
    return output
