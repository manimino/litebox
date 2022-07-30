from litebox.exceptions import InvalidFields, NotInIndexError, FieldsTypeError
from .conftest import AssertRaises
from litebox.main import LiteBox


def test_update_missing_object():
    lb = LiteBox(on={"x": int})
    with AssertRaises(NotInIndexError):
        lb.update(lb)


def test_remove_missing_object():
    lb = LiteBox(on={"x": int})
    with AssertRaises(NotInIndexError):
        lb.remove(lb)


def test_init_without_fields():
    with AssertRaises(InvalidFields):
        LiteBox()
