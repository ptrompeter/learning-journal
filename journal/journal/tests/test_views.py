from journal.views import my_view, compose, entry_detail, edit_entry
from pyramid.testing import DummyRequest


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


def test_compose_page(app):
    """Test compose route returns 200."""
    response = app.get('/compose')
    assert response.status_code == 200


def test_edit_page(app):
    """Test edit route returns 200."""
    response = app.get('/edit/1')
    assert response.status_code == 200
