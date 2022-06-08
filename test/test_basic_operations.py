import random
from dataclasses import dataclass
from rangeindex.rangeindex import RangeIndex


az = 'qwertyuiopasdfghjklzxcvbnm'
ten = list(range(10))


@dataclass
class Thing:
    x: int
    y: float
    desc: str


def make_thing():
    s = []
    for i in range(5):
        s.append(random.choice(az))
    return Thing(x=random.choice(ten), y=random.random(), desc=''.join(s))


def test_create_insert_find():
    ri = RangeIndex({'x': int, 'y': float, 'desc': str})
    obj_to_find = make_thing()
    obj_to_find.x = 8
    not_this_one = make_thing()
    not_this_one.x = 0
    ri.add(obj_to_find)
    ri.add(not_this_one)
    found_objs = ri.find([('x', '>', 5)])
    assert found_objs == [obj_to_find]


def test_delete():
    ri = RangeIndex({'x': int, 'y': float, 'desc': str})
    t = make_thing()
    ri.add(t)
    found_objs = ri.find()
    assert found_objs == [t]
    ri.remove(t)
    found_objs = ri.find([])
    assert found_objs == []


def test_update():
    ri = RangeIndex({'x': int, 'y': float, 'desc': str})
    t = make_thing()
    t.x = 2
    ri.add(t)
    objs = ri.find([('x', '>=', 2)])
    assert objs == [t]
    ri.update(t, {'x': 0})
    objs = ri.find([('x', '>=', 2)])
    assert objs == []
    objs = ri.find([('x', '<', 2)])
    assert objs == [t]

