from journal.models import Entry, DBSession
from pyramid.testing import DummyRequest
from pyramid.response import Response


# class test_NewEntry(Form):
#     pass

# def test_my_view():
#     req = DummyRequest()
#     from journal.views import my_view
#     assert my_view(req) == Response({'entries': []})

# def test_compose(request):
#     pass


def test_add_new_entry(dbtransaction):
    from journal.views import compose
    req = DummyRequest()
    req.title = 'test title'
    req.text = 'test text'
    req.method = 'POST'
    compose(req)

    entries = DBSession.query(Entry).all()
    assert req.title == entries[0].title




# def test_entry_detail(request):


# def test_edit_entry(request):

def test_home_page(app):
    response = app.get('/')
    assert response.status_code == 200

# def test_entry_page(app, add_entry):
#     import transaction
#     # from conftest import add_entry
#     add_entry()
#     transaction.commit()
#     response = app.get('/entry/1')
#     assert response.status_code == 200

def test_compose_page(app):
    response = app.get('/')
    assert response.status_code == 200

# def test_edit_page(app):
#     response = app.get('/')
#     assert response.status_code == 200
