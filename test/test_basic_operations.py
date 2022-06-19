import random
from dataclasses import dataclass
from rangeindex import RangeIndex
from rangeindex.constants import PANDAS, SQLITE


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


def test_create_insert_find(engine):
    ri = RangeIndex(on={"x": int, "y": float, "s": str}, engine=engine)
    obj_to_find = make_thing()
    obj_to_find.x = 8
    not_this_one = make_thing()
    not_this_one.x = 0
    ri.add(obj_to_find)
    ri.add(not_this_one)
    found_objs = ri.find("x > 5")
    assert found_objs == [obj_to_find]


def test_delete(engine):
    ri = RangeIndex(on={"x": int, "y": float, "s": str}, engine=engine)
    t = make_thing()
    ri.add(t)
    found_objs = ri.find()
    assert found_objs == [t]
    ri.remove(t)
    found_objs = ri.find([])
    assert found_objs == []


def test_update(engine):
    ri = RangeIndex(on={"x": int, "y": float, "s": str}, engine=engine)
    t = make_thing()
    t.x = 2
    ri.add(t)
    objs = ri.find("x >= 2")
    assert objs == [t]
    ri.update(t, {"x": 0})
    objs = ri.find("x >= 2")
    assert objs == []
    objs = ri.find("x < 2")
    assert objs == [t]


def test_find_equal(engine):
    ri = RangeIndex(on={"x": int, "y": float, "s": str}, engine=engine)
    t = make_thing()
    ri.add(t)
    int_result = ri.find(f"x == {t.x}")
    float_result = ri.find(f"y == {t.y}")
    str_result = ri.find(f"s == '{t.s}'")
    assert [t] == int_result
    assert [t] == float_result
    assert [t] == str_result


def test_find_null(engine):
    ri = RangeIndex(on={"x": int, "y": float, "s": str}, engine=engine)
    t = Thing(x=None, y=None, s=None)
    ri.add(t)
    if engine == PANDAS:
        int_result = ri.find(f"x != x")
        float_result = ri.find(f"y != y")
        str_result = ri.find(f"s != s")
    elif engine == SQLITE:
        int_result = ri.find(f"x is null")
        float_result = ri.find(f"y is null")
        str_result = ri.find(f"s is null")
    assert [t] == int_result
    assert [t] == float_result
    assert [t] == str_result


def test_add_many(engine):
    ten_things = [make_thing() for _ in range(10)]
    ri = RangeIndex(ten_things, on={"x": int, "y": float, "s": str}, engine=engine)
    found = ri.find()
    assert len(found) == len(ten_things)
