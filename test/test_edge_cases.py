import random

from dataclasses import dataclass
from collections import namedtuple

from rangeindex import RangeIndex
from rangeindex.constants import PANDAS, SQLITE


@dataclass
class Thing:
    x: int = 0
    y: float = 0.0
    s: str = ""


def test_index_on_missing_attributes(engine):
    ri = RangeIndex(on={"z": float}, engine=engine)
    t = Thing()
    ri.add(t)
    if engine == PANDAS:
        found = ri.find("z != z")
    elif engine == SQLITE:
        found = ri.find("z is null")
    assert found == [t]


def test_index_namedtuple(engine):
    Point = namedtuple("Point", "x")
    pt = Point(random.random())
    ri = RangeIndex(on={"x": float, "y": float}, engine=engine)
    ri.add(pt)
    ls = ri.find("x <= 1")
    assert ls == [pt]


def test_multiple_rangeindex_instances(engine):
    t1 = Thing()
    ri1 = RangeIndex(on={"x": int}, engine=engine)
    ri1.add(t1)

    t2 = Thing()
    ri2 = RangeIndex(on={"x": int}, engine=engine)
    ri2.add(t2)

    assert ri1.find("x <= 1") == [t1]
    assert ri2.find("x <= 1") == [t2]


def test_multiple_adds(engine):
    things_1 = [Thing(x=1) for _ in range(10)]
    things_2 = [Thing(x=2) for _ in range(10)]
    thing_3 = Thing(x=3)
    ri = RangeIndex(on={"x": int}, engine=engine)
    ri.add_many(things_1)
    ri.add_many(things_2)
    ri.add(thing_3)
    assert len(ri.find("x == 1")) == 10
    assert len(ri.find("x == 2")) == 10
    assert len(ri.find("x == 3")) == 1
    assert len(ri.find()) == 21


def test_add_one_we_already_have(engine):
    things = [Thing(x=1) for _ in range(10)]
    ri = RangeIndex(on={"x": int}, engine=engine)
    ri.add_many(things)
    ri.add(things[0])
    assert len(ri) == 10


def test_add_many_we_already_have(engine):
    things_1 = [Thing(x=1) for _ in range(10)]
    things_2 = things_1 + [Thing(x=2) for _ in range(10)]
    ri = RangeIndex(on={"x": int}, engine=engine)
    ri.add_many(things_1)
    ri.add_many(things_2)
    assert len(ri.find("x == 1")) == 10
    assert len(ri.find("x == 2")) == 10
    assert len(ri) == 20


def test_add_many_with_duplicates(engine):
    things = [Thing(x=1) for _ in range(10)]
    double_things = things + things
    ri = RangeIndex(on={"x": int}, engine=engine)
    ri.add_many(double_things)
    assert len(ri) == 10


def test_find_on_empty_idx(engine):
    ri = RangeIndex(on={"x": float}, engine=engine)
    assert len(ri.find("x != x")) == 0
