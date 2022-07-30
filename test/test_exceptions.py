from litebox.exceptions import InvalidFields, NotInIndexError, FieldsTypeError
from .conftest import AssertRaises
from litebox.main import LiteBox


def test_update_missing_object():
    tb = LiteBox(on={"x": int})
    with AssertRaises(NotInIndexError):
        tb.update(tb)


def test_remove_missing_object():
    tb = LiteBox(on={"x": int})
    with AssertRaises(NotInIndexError):
        tb.remove(tb)


def test_init_without_fields():
    with AssertRaises(InvalidFields):
        LiteBox()
