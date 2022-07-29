import random

from collections import namedtuple
from dataclasses import dataclass
from tabulated.sqlite_table import LiteBox
from tabulated.pandas_table import PandasBox


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


def test_create_insert_find(table_class):
    tb = table_class(on={"x": int, "y": float, "s": str})
    obj_to_find = make_thing()
    obj_to_find.x = 8
    not_this_one = make_thing()
    not_this_one.x = 0
    tb.add(obj_to_find)
    tb.add(not_this_one)
    found_objs = tb.find("x > 5")
    assert found_objs == [obj_to_find]


def test_delete(table_class):
    tb = table_class(on={"x": int, "y": float, "s": str})
    t = make_thing()
    tb.add(t)
    found_objs = tb.find()
    assert found_objs == [t]
    tb.remove(t)
    found_objs = tb.find([])
    assert found_objs == []


def test_update(table_class):
    tb = table_class(on={"x": int, "y": float, "s": str})
    t = make_thing()
    t.x = 2
    tb.add(t)
    objs = tb.find("x >= 2")
    assert objs == [t]
    tb.update(t, {"x": 0})
    objs = tb.find("x >= 2")
    assert objs == []
    objs = tb.find("x < 2")
    assert objs == [t]
    assert t.x == 0  # check that the update was applied to the obj as well


def test_find_equal(table_class):
    tb = table_class(on={"x": int, "y": float, "s": str, "b": bool})
    t = make_thing()
    tb.add(t)
    int_result = tb.find(f"x == {t.x}")
    float_result = tb.find(f"y == {t.y}")
    str_result = tb.find(f"s == '{t.s}'")
    bool_result = tb.find(f"b == {t.b}")
    assert [t] == int_result
    assert [t] == float_result
    assert [t] == str_result
    assert [t] == bool_result


def test_find_null(table_class):
    tb = table_class(on={"x": int, "y": float, "s": str, "b": bool})
    t = Thing(x=None, y=None, s=None, b=None)
    tb.add(t)
    if table_class == PandasBox:
        int_result = tb.find(f"x != x")
        float_result = tb.find(f"y != y")
        str_result = tb.find(f"s != s")
        bool_result = tb.find(f"b != b")
    elif table_class == LiteBox:
        int_result = tb.find(f"x is null")
        float_result = tb.find(f"y is null")
        str_result = tb.find(f"s is null")
        bool_result = tb.find(f"b is null")
    assert [t] == int_result
    assert [t] == float_result
    assert [t] == str_result
    assert [t] == bool_result


def test_add_many(table_class):
    ten_things = [make_thing() for _ in range(10)]
    tb = table_class(ten_things, on={"x": int, "y": float, "s": str})
    found = tb.find()
    assert len(found) == len(ten_things)


def test_parens_and_ors(table_class):
    things = [make_thing() for _ in range(10)]
    for i, t in enumerate(things):
        t.x = i
    things[0].y = 1000
    tb = table_class(things, on={"x": int, "y": float, "s": str})
    found = tb.find("(x == 0 and y == 1000) or x == 9")
    assert len(found) == 2


def test_contains(table_class):
    things = [make_thing() for _ in range(5)]
    tb = table_class(things, on={"x": int})
    assert all(t in tb for t in things)
    t_not = make_thing()
    assert t_not not in tb


def test_iteration(table_class):
    things = [make_thing() for _ in range(5)]
    tb = table_class(things, on={"x": int, "y": float, "s": str})
    ls = []
    for obj in tb:
        ls.append(obj)
    assert len(ls) == 5
    assert all(obj in ls for obj in things)


def test_index_namedtuple(table_class):
    Point = namedtuple("Point", "x")
    pt = Point(random.random())
    tb = table_class(on={"x": float, "y": float})
    tb.add(pt)
    ls = tb.find("x <= 1")
    assert ls == [pt]


def test_index_dict(table_class):
    d1 = {"a": 1, "b": 2.2}
    d2 = {"a": 0, "b": 4.4}
    ds = [d1, d2]
    tb = table_class(ds, on={"a": int, "b": float})
    ls = tb.find("b == 4.4")
    assert ls == [d2]


def test_update_dict(table_class):
    d1 = {"a": 1, "b": 2.2}
    d2 = {"a": 0, "b": 4.4}
    ds = [d1, d2]
    tb = table_class(ds, on={"a": int, "b": float})
    tb.update(d2, {"b": 5.5})
    ls = tb.find("b == 5.5")
    assert ls == [d2]
    assert d2["b"] == 5.5
