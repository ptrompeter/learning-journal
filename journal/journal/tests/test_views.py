from journal.views import my_view, compose, entry_detail, edit_entry
from pyramid.testing import DummyRequest
from os import environ

AUTH_DATA = {'username': 'admin', 'password': 'secret'}


def test_my_view(dbtransaction, new_entry):
    """Test my_view retunrs a lists entries in the response object."""
    req = DummyRequest()
    resp = my_view(req)
    entries_dict = resp['entries']
    assert entries_dict[0] == new_entry


def test_entry_detail_view(dbtransaction, new_entry):
    """Test entry_detail returns a list of entries in the reposnse object."""
    req = DummyRequest()
    req.matchdict = {'entry_id': new_entry.id}
    resp_dict = entry_detail(req)
    assert resp_dict['entry'] == new_entry


def test_add_new_entry(dbtransaction, dummy_post_request):
    req = dummy_post_request
    resp = compose(req)
    assert resp.status_code == 302


def test_edit_entry(dbtransaction, new_entry, dummy_post_request):
    entry_id = new_entry.id
    dummy_post_request.path = '/edit'
    dummy_post_request.matchdict = {'entry_id': entry_id}
    resp = edit_entry(dummy_post_request)
    assert resp.status_code == 302 and resp.title == 'Found'
    resp_loc = resp.location.split('/')
    assert resp_loc[-2] == 'entries' and int(resp_loc[-1]) == entry_id


def test_home_page(app):
    """Test home route returns 200."""
    response = app.get('/')
    assert response.status_code == 200


def test_entries_page(dbtransaction, app, new_entry):
    """Test entries route returns 200."""
    entry_id = new_entry.id
    response = app.get('/entries/{}'.format(entry_id))
    assert response.status_code == 200


def test_compose_page(authenticated_app):
    """Test compose route returns 200."""
    response = authenticated_app.get('/compose')
    assert response.status_code == 200


# TODO:  test attempting to access compose page directly via url when not logged in.
# def test_compose_page(app):
#     """Test compose route returns 200."""
#     response = app.get('/compose')
#     assert response.status_code == 403


def test_edit_page(authenticated_app):
    """Test edit route returns 200."""
    response = authenticated_app.get('/edit/1')
    assert response.status_code == 200


def test_password_exist(auth_env):
    assert environ.get('AUTH_PASSWORD', None) is not None


def test_stored_password_is_encrypted(auth_env):
    assert environ.get('AUTH_PASSWORD', None) != 'secret'


def test_username_exist(auth_env):
    assert environ.get('AUTH_USERNAME', None) is not None


def test_check_pw_success(auth_env):
    from journal.security import check_password
    password = 'secret'
    assert check_password(password)


def test_check_pw_fail(auth_env):
    from journal.security import check_password
    password = 'super secret'
    assert not check_password(password)


def test_get_login_view(app):
    response = app.get('/login')
    assert response.status_code == 200


def test_post_login_success(app, auth_env):
    response = app.post('/login', AUTH_DATA)
    assert response.status_code == 302


def test_logout_success(authenticated_app, auth_env):
    response = authenticated_app.post('/logout')
    assert response.status_code == 302


def test_post_login_success_redirect(app, auth_env):
    response = app.post('/login', AUTH_DATA)
    headers = response.headers
    domain = 'http://localhost'
    path = headers.get('Location', '')[len(domain):]
    assert response.status_code == 302
    assert path == '/'


def test_post_login_success_auth_tkt_present(app, auth_env):
    response = app.post('/login', AUTH_DATA)
    headers = response.headers
    cookie_set = headers.getall('Set-Cookie')
    assert cookie_set
    for cookie in cookie_set:
        if cookie.startswith('auth_tkt'):
            break
    else:
        assert False


def test_post_login_fail_password(app, auth_env):
    data = AUTH_DATA
    data['password'] = 'garbage'
    response = app.post('/login', data)
    assert response.status_code == 302
