import unittest

from dataclasses import dataclass

from tabulated.pandas_table import PandasTable
from tabulated.sqlite_table import SqliteTable


@dataclass
class Thing:
    x: int = 0
    y: float = 0.0
    s: str = ""


def test_index_on_missing_attributes(table_class):
    ri = table_class(on={"z": float})
    t = Thing()
    ri.add(t)
    if table_class == PandasTable:
        found = ri.find("z != z")
    elif table_class == SqliteTable:
        found = ri.find("z is null")
    assert found == [t]


def test_multiple_tabulated_instances(table_class):
    t1 = Thing()
    ri1 = table_class(on={"x": int})
    ri1.add(t1)

    t2 = Thing()
    ri2 = table_class(on={"x": int})
    ri2.add(t2)

    assert ri1.find("x <= 1") == [t1]
    assert ri2.find("x <= 1") == [t2]


def test_multiple_adds(table_class):
    things_1 = [Thing(x=1) for _ in range(10)]
    things_2 = [Thing(x=2) for _ in range(10)]
    thing_3 = Thing(x=3)
    ri = table_class(on={"x": int})
    ri.add_many(things_1)
    ri.add_many(things_2)
    ri.add(thing_3)
    assert len(ri.find("x == 1")) == 10
    assert len(ri.find("x == 2")) == 10
    assert len(ri.find("x == 3")) == 1
    assert len(ri.find()) == 21


def test_add_one_we_already_have(table_class):
    things = [Thing(x=1) for _ in range(10)]
    ri = table_class(on={"x": int})
    ri.add_many(things)
    ri.add(things[0])
    assert len(ri) == 10


def test_add_many_we_already_have(table_class):
    things_1 = [Thing(x=1) for _ in range(10)]
    things_2 = things_1 + [Thing(x=2) for _ in range(10)]
    ri = table_class(on={"x": int})
    ri.add_many(things_1)
    ri.add_many(things_2)
    assert len(ri.find("x == 1")) == 10
    assert len(ri.find("x == 2")) == 10
    assert len(ri) == 20


def test_add_many_with_duplicates(table_class):
    things = [Thing(x=1) for _ in range(10)]
    double_things = things + things
    ri = table_class(on={"x": int})
    ri.add_many(double_things)
    assert len(ri) == 10


def test_find_on_empty_idx(table_class):
    ri = table_class(on={"x": float})
    assert len(ri.find("x != x")) == 0


def test_update_many(table_class):
    things = [Thing(x=1) for _ in range(10)]
    ri = table_class(things, on={"x": int})
    for i in range(5):
        ri.update(things[i], {"x": 2})
    assert len(ri.find("x == 1")) == 5
    assert len(ri.find("x == 2")) == 5


def test_remove_many(table_class):
    things = [Thing(x=1) for _ in range(10)]
    ri = table_class(things, on={"x": int})
    for i in range(5):
        ri.remove(things[i])
    assert len(ri) == 5
    assert all([t not in ri for t in things[:5]])
    print("expected:", sorted([id(t) for t in things[5:]]))
    assert all([t in ri for t in things[5:]])


def test_empty(table_class):
    ri = table_class(on={"x": int})
    assert ri not in ri
    assert not ri.find("x == 3")
    assert len(ri) == 0
    for _ in ri:
        # tests iterator. Should be empty, won't reach here
        assert False
