from pyramid.response import Response
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound, HTTPForbidden
from pyramid.security import remember, forget
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from jinja2 import Markup
from .security import check_password
import markdown

from sqlalchemy.exc import DBAPIError

from .models import (
    DBSession,
    Entry,
    )


class NewEntry(Form):
    title = StringField('title', [validators.Length(min=1, max=128)])
    text = TextAreaField('text')


class LoginForm(Form):
    username = StringField('username',
                           validators=[
                                       validators.input_required(),
                                       validators.length(min=3),
                                      ])
    password = PasswordField('password',
                             validators=[validators.input_required()])


# def user_login(request):
#     username = request.param.get


@view_config(route_name='home', renderer='templates/home.jinja2', permission='view')
def my_view(request):
    all_entries = DBSession.query(Entry).order_by(Entry.id.desc()).all()
    return {'entries': all_entries}


@view_config(route_name='entry', renderer='templates/entry.jinja2', permission='view')
def entry_detail(request):
    try:
        entry_id = request.matchdict['entry_id']
        entry = DBSession.query(Entry).get(entry_id)
        entry.text = render_markdown(entry.text)
        return {'entry': entry}
    except DBAPIError:
        return Response("detail broke", content_type='text/plain', status_int=500)


@view_config(route_name='compose', renderer='templates/compose.jinja2', permission='edit')
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
            url = request.route_url('entry', entry_id=entry_id)
            return HTTPFound(location=url)

        return {'new_entry': new_entry, 'request': request}
    except DBAPIError:
        return Response("compose broke", content_type='text/plain', status_int=500)


# CSRF is generated on a per request basis.
# server sends, client sends back.  server verifies client sent back csrf token
# @view_config(method=POST, check-csrf)
# @view_config(route_name='edit', renderer='templates/edit.jinja2', method=GET)
@view_config(route_name='edit', renderer='templates/edit.jinja2', permission='edit')
def edit_entry(request):
    try:
        entry_id = request.matchdict['entry_id']
        post_for_editing = DBSession.query(Entry).get(entry_id)
        new_entry = NewEntry(request.POST, post_for_editing)

        if request.method == 'POST' and new_entry.validate():
            new_entry.populate_obj(post_for_editing)
            url = request.route_url('entry', entry_id=entry_id)
            return HTTPFound(location=url)
        return {'new_entry': new_entry, 'entry': entry_id}
    except DBAPIError:
        return Response("edit broke", content_type='text/plain', status_int=500)


# @view_config(route_name='edit', renderer='templates/edit.jinja2', permission='view')
# def edit_entry_unauthorized(request):
#     return HTTPFound(request.route_url('login'))


@view_config(route_name='login', renderer='templates/login.jinja2', permission='view')
def login(request):
    form = LoginForm(request.POST)
    if request.method == 'POST' and form.validate():
        username = request.params.get('username', '')
        password = request.params.get('password', '')
        if check_password(password):
            headers = remember(request, username)
            return HTTPFound(request.route_url('home'), headers=headers)
        return HTTPFound(request.route_url('login'))
    return {'form': form}


@view_config(route_name='logout', permission='view')
def logout(request):
    headers = forget(request)
    return HTTPFound(request.route_url('home'), headers=headers)


def render_markdown(content):
    output = Markup(markdown.markdown(content))
    return output
