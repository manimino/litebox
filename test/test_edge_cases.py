from dataclasses import dataclass
from rangeindex.rangeindex import RangeIndex


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
