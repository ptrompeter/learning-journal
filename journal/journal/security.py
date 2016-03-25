from pyramid.security import Allow, Everyone, Authenticated, ALL_PERMISSIONS
from passlib.hash import sha512_crypt
from passlib.apps import custom_app_context as pwd_context
import os


def check_password(pw):
    hashed = os.environ.get('AUTH_PASSWORD', sha512_crypt.encrypt('somePassword'))
    return sha512_crypt.verify(pw, hashed)


class DefaultRoot(object):
    __acl__ = [
               (Allow, Everyone, 'view'),
               (Allow, Authenticated, ALL_PERMISSIONS),
    ]

    def __init__(self, request):
        self.request = request


class EntryRoot(object):
    __name__ = 'entry'

    @property
    def __parent__(self):
        return DefaultRoot(self.request)

    def __init__(self, request):
        self.request = request

    def __getitem__(self, name):
        entry_obj = Entry.by_id(name)
        if entry_obj is None:
            raise KeyError(name)
        entry_obj.__parent__ = self
        return entry_obj
