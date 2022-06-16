import random
from dataclasses import dataclass
from rangeindex import RangeIndex


az = "qwertyuiopasdfghjklzxcvbnm"
ten = list(range(10))


@dataclass
class Thing:
    x: int
    y: float
    s: str


def make_thing():
    s = []
    for i in range(5):
        s.append(random.choice(az))
    return Thing(x=random.choice(ten), y=random.random(), s="".join(s))


def test_create_insert_find(backend):
    ri = RangeIndex({"x": int, "y": float, "s": str}, backend=backend)
    obj_to_find = make_thing()
    obj_to_find.x = 8
    not_this_one = make_thing()
    not_this_one.x = 0
    ri.add(obj_to_find)
    ri.add(not_this_one)
    found_objs = ri.find([("x", ">", 5)])
    assert found_objs == [obj_to_find]


def test_delete(backend):
    ri = RangeIndex({"x": int, "y": float, "s": str}, backend=backend)
    t = make_thing()
    ri.add(t)
    found_objs = ri.find()
    assert found_objs == [t]
    ri.remove(t)
    found_objs = ri.find([])
    assert found_objs == []


def test_update(backend):
    ri = RangeIndex({"x": int, "y": float, "s": str}, backend=backend)
    t = make_thing()
    t.x = 2
    ri.add(t)
    objs = ri.find([("x", ">=", 2)])
    assert objs == [t]
    ri.update(t, {"x": 0})
    objs = ri.find([("x", ">=", 2)])
    assert objs == []
    objs = ri.find([("x", "<", 2)])
    assert objs == [t]


def test_find_equal(backend):
    ri = RangeIndex({"x": int, "y": float, "s": str}, backend=backend)
    t = make_thing()
    ri.add(t)
    int_result = ri.find([("x", "==", t.x)])
    float_result = ri.find([("y", "==", t.y)])
    str_result = ri.find([("s", "==", t.s)])
    assert [t] == int_result
    assert [t] == float_result
    assert [t] == str_result


def test_find_null(backend):
    ri = RangeIndex({"x": int, "y": float, "s": str}, backend=backend)
    t = Thing(x=None, y=None, s=None)
    ri.add(t)
    int_result = ri.find([("x", "is", t.x)])
    float_result = ri.find([("y", "is", t.y)])
    str_result = ri.find([("s", "is", t.s)])
    assert [t] == int_result
    assert [t] == float_result
    assert [t] == str_result


def test_add_many(backend):
    ten_things = [make_thing() for _ in range(10)]
    ri = RangeIndex({"x": int, "y": float, "s": str}, backend=backend)
    ri.add_many(ten_things)
    found = ri.find()
    assert len(found) == len(ten_things)
