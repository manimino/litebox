import random

from dataclasses import dataclass
from collections import namedtuple

from rangeindex import RangeIndex


@dataclass
class Thing:
    x: int = 0
    y: float = 0.0
    desc: str = ''


def test_index_on_missing_attributes():
    ri = RangeIndex({'z': float})
    t = Thing()
    ri.add(t)
    found = ri.find([('z', 'is', None)])
    assert found == [t]


def test_index_namedtuple():
    Point = namedtuple("Point", "x")
    pt = Point(random.random())
    ri = RangeIndex({'x': float, 'y': float})
    ri.add(pt)
    ls = ri.find([('x', '<=', 1)])
    assert ls == [pt]


def test_multiple_rangeindex_instances():
    t1 = Thing()
    ri1 = RangeIndex({'x': int})
    ri1.add(t1)

    t2 = Thing()
    ri2 = RangeIndex({'x': int})
    ri2.add(t2)

    assert ri1.find([('x', '<=', 1)]) == [t1]
    assert ri2.find([('x', '<=', 1)]) == [t2]
