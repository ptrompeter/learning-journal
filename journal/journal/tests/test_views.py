from journal.models import Entry, DBSession
from journal.views import my_view, compose, entry_detail
from pyramid.testing import DummyRequest
from pyramid.response import Response


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


# def test_entry_detail_view(dbtransaction, new_entry):
#     """Test that list_view returns a Query of Entries."""
#     test_request = DummyRequest()
#     test_request.matchdict = {'detail_id': new_entry.id}
#
#     response_dict = detail_view(test_request)
#     assert response_dict['entry'] == new_entry


# class test_NewEntry(Form):
#     pass


# def test_compose(request):
#     pass


def test_add_new_entry(dbtransaction, dummy_post_request):
    from webob import multidict
    from journal.views import compose
    import pdb
    # req = DummyRequest(title='test title', text='test text')
    # test_dict = [('title', 'test title'),(('text'), ('test text'))]
    # mdict = multidict.MultiDict(test_dict)
    req = dummy_post_request
    # req.method = 'POST'
    # req.POST = mdict
    resp = compose(req)
    pdb.set_trace()
    assert resp.status_code == 302

    # entries = DBSession.query(Entry).all()
    # assert req.POST['title'] == entries[0].title


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
