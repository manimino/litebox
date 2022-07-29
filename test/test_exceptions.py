from tabulated.exceptions import FieldsTypeError, InvalidFields

from tabulated.exceptions import NotInIndexError, FieldsTypeError
from .conftest import AssertRaises


def test_update_missing_object(table_class):
    tb = table_class(on={"x": int})
    with AssertRaises(NotInIndexError):
        tb.update(tb, {"x": 100})


def test_remove_missing_object(table_class):
    tb = table_class(on={"x": int})
    with AssertRaises(NotInIndexError):
        tb.remove(tb)


def test_init_without_fields(table_class):
    with AssertRaises(InvalidFields):
        table_class()
