# -*- coding: utf-8 -*-

from journal.models import Entry, DBSession


def test_create_entry(dbtransaction):
    """Test for a change of state of the model."""
    new_model = Entry(title="jill", text='jello')
    assert new_model.id is None
    DBSession.add(new_model)
    DBSession.flush()
    assert new_model.id is not None