from journal.models import Entry, DBSession
from pyramid.testing import DummyRequest
from pyramid.response import Response


# class test_NewEntry(Form):
#     pass

def test_my_view():
    req = DummyRequest()
    from journal.views import my_view
    assert my_view(req) == Response({'entries': []})

# def test_compose(request):
#     pass


# def test_new_entry_redirect(request):


# def test_entry_detail(request):


# def test_edit_entry(request):

def test_list_page(app):
    response = app.get('/')
    assert response.status_code == 200