from litebox.exceptions import InvalidFields, NotInIndexError
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
        LiteBox([])


def test_bad_field_type():
    with AssertRaises(InvalidFields):
        LiteBox([], {1: str})


def test_bad_field_values():
    with AssertRaises(InvalidFields):
        LiteBox([], {'a': dict()})

