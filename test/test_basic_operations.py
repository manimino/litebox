import random

from collections import namedtuple
from dataclasses import dataclass
from litebox.main import LiteBox


az = "qwertyuiopasdfghjklzxcvbnm"
ten = list(range(10))


@dataclass
class Thing:
    x: int
    y: float
    s: str
    b: bool


def make_thing():
    s = []
    for i in range(5):
        s.append(random.choice(az))
    return Thing(
        x=random.choice(ten),
        y=random.random(),
        s="".join(s),
        b=random.choice([False, True]),
    )


def test_create_insert_find():
    lb = LiteBox(on={"x": int, "y": float, "s": str})
    obj_to_find = make_thing()
    obj_to_find.x = 8
    not_this_one = make_thing()
    not_this_one.x = 0
    lb.add(obj_to_find)
    lb.add(not_this_one)
    found_objs = lb.find("x > 5")
    assert found_objs == [obj_to_find]


def test_delete():
    lb = LiteBox(on={"x": int, "y": float, "s": str})
    t = make_thing()
    lb.add(t)
    found_objs = lb.find()
    assert found_objs == [t]
    lb.remove(t)
    found_objs = lb.find([])
    assert found_objs == []


def test_update():
    lb = LiteBox(on={"x": int, "y": float, "s": str})
    t = make_thing()
    t.x = 2
    lb.add(t)
    objs = lb.find("x >= 2")
    assert objs == [t]
    t.x = 0
    lb.update(t)
    objs = lb.find("x >= 2")
    assert objs == []
    objs = lb.find("x < 2")
    assert objs == [t]


def test_find_equal():
    lb = LiteBox(on={"x": int, "y": float, "s": str, "b": bool})
    t = make_thing()
    lb.add(t)
    int_result = lb.find(f"x == {t.x}")
    float_result = lb.find(f"y == {t.y}")
    str_result = lb.find(f"s == '{t.s}'")
    bool_result = lb.find(f"b == {t.b}")
    assert [t] == int_result
    assert [t] == float_result
    assert [t] == str_result
    assert [t] == bool_result


def test_find_null():
    lb = LiteBox(on={"x": int, "y": float, "s": str, "b": bool})
    t = Thing(x=None, y=None, s=None, b=None)
    lb.add(t)
    int_result = lb.find(f"x is null")
    float_result = lb.find(f"y is null")
    str_result = lb.find(f"s is null")
    bool_result = lb.find(f"b is null")
    assert [t] == int_result
    assert [t] == float_result
    assert [t] == str_result
    assert [t] == bool_result


def test_add_many():
    ten_things = [make_thing() for _ in range(10)]
    lb = LiteBox(ten_things, on={"x": int, "y": float, "s": str})
    found = lb.find()
    assert len(found) == len(ten_things)


def test_parens_and_ors():
    things = [make_thing() for _ in range(10)]
    for i, t in enumerate(things):
        t.x = i
    things[0].y = 1000
    lb = LiteBox(things, on={"x": int, "y": float, "s": str})
    found = lb.find("(x == 0 and y == 1000) or x == 9")
    assert len(found) == 2


def test_contains():
    things = [make_thing() for _ in range(5)]
    lb = LiteBox(things, on={"x": int})
    assert all(t in lb for t in things)
    t_not = make_thing()
    assert t_not not in lb


def test_iteration():
    things = [make_thing() for _ in range(5)]
    lb = LiteBox(things, on={"x": int, "y": float, "s": str})
    ls = []
    for obj in lb:
        ls.append(obj)
    assert len(ls) == 5
    assert all(obj in ls for obj in things)


def test_index_namedtuple():
    Point = namedtuple("Point", "x")
    pt = Point(random.random())
    lb = LiteBox(on={"x": float, "y": float})
    lb.add(pt)
    ls = lb.find("x <= 1")
    assert ls == [pt]


def test_index_dict():
    d1 = {"a": 1, "b": 2.2}
    d2 = {"a": 0, "b": 4.4}
    ds = [d1, d2]
    lb = LiteBox(ds, on={"a": int, "b": float})
    ls = lb.find("b == 4.4")
    assert ls == [d2]


def test_update_dict():
    d1 = {"a": 1, "b": 2.2}
    d2 = {"a": 0, "b": 4.4}
    ds = [d1, d2]
    lb = LiteBox(ds, on={"a": int, "b": float})
    d2['b'] = 5.5
    lb.update(d2)
    ls = lb.find("b == 5.5")
    assert ls == [d2]


def test_callable():
    def get_a1(obj):
        return obj['a'][1]
    data = [{'a': [1, 2, 3]}]
    lb = LiteBox(data, on={get_a1: int})
    assert len(lb.find("get_a1 == 2")) == 1
