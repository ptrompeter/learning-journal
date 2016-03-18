import transaction
from pyramid.response import Response
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from wtforms import Form, StringField, TextAreaField, validators

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
        all_entries = DBSession.query(Entry).all()
        return {'entries': all_entries}
    except DBAPIError:
        return Response("shit broke", content_type='text/plain', status_int=500)


@view_config(route_name='compose', renderer='templates/compose.jinja2')
def compose(request):
    new_entry = NewEntry(request.POST)
    if request.method == 'POST' and new_entry.validate():
        entry = Entry()
        entry.title = new_entry.title.data
        entry.text = new_entry.text.data
        DBSession.add(entry)
        DBSession.flush()
        transaction.commit()
        url = request.route_url('entry', entry_id='latest')
        return HTTPFound(location=url)


    try:
        return {'new_entry': new_entry}
    except DBAPIError:
        return Response("shit broke", content_type='text/plain', status_int=500)
    
@view_config(route_name='entry', renderer='templates/entry.jinja2', match_param="entry_id=latest")
def new_entry_redirect(request):
    try:     
        # entry_id = request.matchdict['entry_id']
        entry = DBSession.query(Entry).order_by(Entry.id.desc()).first()
        return {'entry': entry}
    except DBAPIError:
        return Response("shit broke", content_type='text/plain', status_int=500)

@view_config(route_name='entry', renderer='templates/entry.jinja2')
def entry_detail(request):
    try:     
        entry_id = request.matchdict['entry_id']
        entry = DBSession.query(Entry).filter(Entry.id == entry_id).first()
        return {'entry': entry}
    except DBAPIError:
        return Response("shit broke", content_type='text/plain', status_int=500)

@view_config(route_name='edit', renderer='templates/edit.jinja2')
def edit_entry(request):
    try:             
        entry_id = request.matchdict['entry_id']
        post_for_editing = DBSession.query(Entry).get(entry_id)
        new_entry = NewEntry(request.POST, post_for_editing)

        if request.method == 'POST' and new_entry.validate():
            new_entry.populate_obj(post_for_editing)
            # entry = Entry()
            # entry.title = new_entry.title.data
            # entry.text = new_entry.text.data
            DBSession.add(new_entry)
            DBSession.flush()
            transaction.commit()
            url = request.route_url('entry', entry_id=entry_id)
            return HTTPFound(location=url)
        return {'new_entry': post_for_editing}
    except DBAPIError:
        return Response("shit broke", content_type='text/plain', status_int=500)



