import transaction
import os
from pyramid.response import Response
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from wtforms import Form, StringField, TextAreaField, validators
from jinja2 import Markup
import markdown
# from . import manager
from pyramid.view import (
    view_config,
    forbidden_view_config,
    )

from pyramid.security import (
    remember,
    forget,
    )

from .security import check_pw, manager

# from cryptacular.bcrypt import BCRYPTPasswordManager

from sqlalchemy.exc import DBAPIError

from .models import (
    DBSession,
    Entry,
    )


class NewEntry(Form):
    title = StringField('title', [validators.Length(min=1, max=128)])
    text = TextAreaField('text')

class LoginForm(Form):
    login = StringField('login', [validators.Length(min=1, max=128)])
    password = StringField('password', [validators.Length(min=8, max=32)])

@view_config(route_name='home', renderer='templates/home.jinja2')
def my_view(request):
    import pdb; pdb.set_trace()
    all_entries = DBSession.query(Entry).order_by(Entry.id.desc()).all()
    return {'entries': all_entries}




@view_config(route_name='entry', renderer='templates/entry.jinja2')
def entry_detail(request):
    # try:
    entry_id = request.matchdict['entry_id']
    entry = DBSession.query(Entry).get(entry_id)
    entry.text = render_markdown(entry.text)
    return {'entry': entry}
    # except httpexceptions:
    #     return



@view_config(route_name='compose', renderer='templates/compose.jinja2', permission='edit')
def compose(request):
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

@view_config(route_name='forbidden', renderer='templates/forbidden.jinja2')
def forbidden_view(request):
    """Do not allow login if user is already logged in"""
    if authenticated_userid(request):
        return HTTPForbidden()
    loc = request.route_url('login', _query=(('next', request.path),))
    return HTTPFound(location=loc)

@view_config(route_name='login', renderer='templates/login.jinja2')
def login(request):
    # username = request.params.get('username', '')
    error = ''
    login_form = LoginForm(request.POST)
    if request.method == 'POST':
        login = request.POST.get('login', '')
        password = request.POST.get('password', '')

        user = os.environ.get('MY_NAME', None)
        my_password = os.environ.get('MY_PASSWORD', None)
        if user == login and check_pw(password):
            headers = remember(request, login)
            return HTTPFound(request.route_url('home'), headers=headers)
        did_fail = True

        return{
            'failed_attempt': did_fail,
            'error_msg': "Login failed.  Try Again.",
            'login_form': login_form,
        }
    return {'login_form': login_form}

@view_config(route_name='logout', renderer='templates/home.jinja2')
def logout_view(request):
    headers = forget(request)
    loc = request.route_url('home')
    return HTTPFound(location=loc)

@view_config(route_name='edit', renderer='templates/edit.jinja2', permission='edit')
def edit_entry(request):
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


def render_markdown(content):
    output = Markup(markdown.markdown(content))
    return output
