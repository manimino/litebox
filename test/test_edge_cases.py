import random

from dataclasses import dataclass
from collections import namedtuple

from rangeindex import RangeIndex


@dataclass
class Thing:
    x: int = 0
    y: float = 0.0
    s: str = ''


def test_index_on_missing_attributes(backend):
    ri = RangeIndex({'z': float}, backend)
    t = Thing()
    ri.add(t)
    found = ri.find([('z', 'is', None)])
    assert found == [t]


def test_index_namedtuple(backend):
    Point = namedtuple("Point", "x")
    pt = Point(random.random())
    ri = RangeIndex({'x': float, 'y': float}, backend)
    ri.add(pt)
    ls = ri.find([('x', '<=', 1)])
    assert ls == [pt]


def test_multiple_rangeindex_instances(backend):
    t1 = Thing()
    ri1 = RangeIndex({'x': int}, backend)
    ri1.add(t1)

    t2 = Thing()
    ri2 = RangeIndex({'x': int}, backend)
    ri2.add(t2)

    assert ri1.find([('x', '<=', 1)]) == [t1]
    assert ri2.find([('x', '<=', 1)]) == [t2]


def test_multiple_adds(backend):
    things_1 = [Thing(x=1) for _ in range(10)]
    things_2 = [Thing(x=2) for _ in range(10)]
    thing_3 = Thing(x=3)
    ri = RangeIndex({'x': int}, backend)
    ri.add_many(things_1)
    ri.add_many(things_2)
    ri.add(thing_3)
    assert len(ri.find('x == 1')) == 10
    assert len(ri.find('x == 2')) == 10
    assert len(ri.find('x == 3')) == 1
    assert len(ri.find()) == 21


def test_add_one_we_already_have(backend):
    things = [Thing(x=1) for _ in range(10)]
    ri = RangeIndex({'x': int}, backend)
    ri.add_many(things)
    ri.add(things[0])
    assert len(ri) == 10


def test_add_many_we_already_have(backend):
    things_1 = [Thing(x=1) for _ in range(10)]
    things_2 = things_1 + [Thing(x=2) for _ in range(10)]
    ri = RangeIndex({'x': int}, backend)
    ri.add_many(things_1)
    ri.add_many(things_2)
    assert len(ri.find('x == 1')) == 10
    assert len(ri.find('x == 2')) == 10
    assert len(ri) == 20


def test_add_many_with_duplicates(backend):
    things = [Thing(x=1) for _ in range(10)]
    double_things = things + things
    ri = RangeIndex({'x': int}, backend)
    ri.add_many(double_things)
    assert len(ri) == 10
