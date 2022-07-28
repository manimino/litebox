import unittest

from dataclasses import dataclass

from tabulated import Tabulated
from tabulated.constants import PANDAS, SQLITE
from tabulated.exceptions import NotInIndexError, FieldsTypeError

joe_and_jane = [
    {"name": "Joe", "age": 16},
    {"name": "Jane", "favourite_color": "red"},
]


@dataclass
class Thing:
    x: int = 0
    y: float = 0.0
    s: str = ""


def test_index_on_missing_attributes(engine):
    ri = Tabulated(on={"z": float}, engine=engine)
    t = Thing()
    ri.add(t)
    if engine == PANDAS:
        found = ri.find("z != z")
    elif engine == SQLITE:
        found = ri.find("z is null")
    assert found == [t]


def test_multiple_tabulated_instances(engine):
    t1 = Thing()
    ri1 = Tabulated(on={"x": int}, engine=engine)
    ri1.add(t1)

    t2 = Thing()
    ri2 = Tabulated(on={"x": int}, engine=engine)
    ri2.add(t2)

    assert ri1.find("x <= 1") == [t1]
    assert ri2.find("x <= 1") == [t2]


def test_multiple_adds(engine):
    things_1 = [Thing(x=1) for _ in range(10)]
    things_2 = [Thing(x=2) for _ in range(10)]
    thing_3 = Thing(x=3)
    ri = Tabulated(on={"x": int}, engine=engine)
    ri.add_many(things_1)
    ri.add_many(things_2)
    ri.add(thing_3)
    assert len(ri.find("x == 1")) == 10
    assert len(ri.find("x == 2")) == 10
    assert len(ri.find("x == 3")) == 1
    assert len(ri.find()) == 21


def test_add_one_we_already_have(engine):
    things = [Thing(x=1) for _ in range(10)]
    ri = Tabulated(on={"x": int}, engine=engine)
    ri.add_many(things)
    ri.add(things[0])
    assert len(ri) == 10


def test_add_many_we_already_have(engine):
    things_1 = [Thing(x=1) for _ in range(10)]
    things_2 = things_1 + [Thing(x=2) for _ in range(10)]
    ri = Tabulated(on={"x": int}, engine=engine)
    ri.add_many(things_1)
    ri.add_many(things_2)
    assert len(ri.find("x == 1")) == 10
    assert len(ri.find("x == 2")) == 10
    assert len(ri) == 20


def test_add_many_with_duplicates(engine):
    things = [Thing(x=1) for _ in range(10)]
    double_things = things + things
    ri = Tabulated(on={"x": int}, engine=engine)
    ri.add_many(double_things)
    assert len(ri) == 10


def test_find_on_empty_idx(engine):
    ri = Tabulated(on={"x": float}, engine=engine)
    assert len(ri.find("x != x")) == 0


def test_update_many(engine):
    things = [Thing(x=1) for _ in range(10)]
    ri = Tabulated(things, on={"x": int}, engine=engine)
    for i in range(5):
        ri.update(things[i], {"x": 2})
    assert len(ri.find("x == 1")) == 5
    assert len(ri.find("x == 2")) == 5


def test_remove_many(engine):
    things = [Thing(x=1) for _ in range(10)]
    ri = Tabulated(things, on={"x": int}, engine=engine)
    for i in range(5):
        ri.remove(things[i])
    assert len(ri) == 5
    assert all([t not in ri for t in things[:5]])
    print("expected:", sorted([id(t) for t in things[5:]]))
    assert all([t in ri for t in things[5:]])


def test_empty(engine):
    ri = Tabulated(on={"x": int})
    assert ri not in ri
    assert not ri.find("x == 3")
    for _ in ri:
        # should be empty, won't reach here
        assert False


class TestExceptions(unittest.TestCase):
    def test_update_missing_object(self):
        for engine in [SQLITE, PANDAS]:
            self.ri = Tabulated(on={"x": int}, engine=engine)
            with self.assertRaises(NotInIndexError):
                self.ri.update(self.ri, {"x": 100})

    def test_remove_missing_object(self):
        for engine in [SQLITE, PANDAS]:
            self.ri = Tabulated(on={"x": int}, engine=engine)
            with self.assertRaises(NotInIndexError):
                self.ri.remove(self.ri)

    def test_init_without_fields(self):
        with self.assertRaises(FieldsTypeError):
            Tabulated(joe_and_jane)
