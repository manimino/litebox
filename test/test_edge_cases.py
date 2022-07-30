from dataclasses import dataclass

from litebox.main import LiteBox


@dataclass
class Thing:
    x: int = 0
    y: float = 0.0
    s: str = ""


def test_index_on_missing_attributes():
    tb = LiteBox(on={"z": float})
    t = Thing()
    tb.add(t)
    found = tb.find("z is null")
    assert found == [t]


def test_multiple_litebox_instances():
    t1 = Thing()
    ri1 = LiteBox(on={"x": int})
    ri1.add(t1)

    t2 = Thing()
    ri2 = LiteBox(on={"x": int})
    ri2.add(t2)

    assert ri1.find("x <= 1") == [t1]
    assert ri2.find("x <= 1") == [t2]


def test_multiple_adds():
    things_1 = [Thing(x=1) for _ in range(10)]
    things_2 = [Thing(x=2) for _ in range(10)]
    thing_3 = Thing(x=3)
    tb = LiteBox(on={"x": int})
    tb.add_many(things_1)
    tb.add_many(things_2)
    tb.add(thing_3)
    assert len(tb.find("x == 1")) == 10
    assert len(tb.find("x == 2")) == 10
    assert len(tb.find("x == 3")) == 1
    assert len(tb.find()) == 21


def test_add_one_we_already_have():
    things = [Thing(x=1) for _ in range(10)]
    tb = LiteBox(on={"x": int})
    tb.add_many(things)
    tb.add(things[0])
    assert len(tb) == 10


def test_add_many_we_already_have():
    things_1 = [Thing(x=1) for _ in range(10)]
    things_2 = things_1 + [Thing(x=2) for _ in range(10)]
    tb = LiteBox(on={"x": int})
    tb.add_many(things_1)
    tb.add_many(things_2)
    assert len(tb.find("x == 1")) == 10
    assert len(tb.find("x == 2")) == 10
    assert len(tb) == 20


def test_add_many_with_duplicates():
    things = [Thing(x=1) for _ in range(10)]
    double_things = things + things
    tb = LiteBox(on={"x": int})
    tb.add_many(double_things)
    assert len(tb) == 10


def test_find_on_empty_idx():
    tb = LiteBox(on={"x": float})
    assert len(tb.find("x != x")) == 0


def test_update_many():
    things = [Thing(x=1) for _ in range(10)]
    tb = LiteBox(things, on={"x": int})
    for i in range(5):
        things[i].x = 2
        tb.update(things[i])
    assert len(tb.find("x == 1")) == 5
    assert len(tb.find("x == 2")) == 5


def test_remove_many():
    things = [Thing(x=1) for _ in range(10)]
    tb = LiteBox(things, on={"x": int})
    for i in range(5):
        tb.remove(things[i])
    assert len(tb) == 5
    assert all([t not in tb for t in things[:5]])
    print("expected:", sorted([id(t) for t in things[5:]]))
    assert all([t in tb for t in things[5:]])


def test_empty():
    tb = LiteBox(on={"x": int})
    assert tb not in tb
    assert not tb.find("x == 3")
    assert len(tb) == 0
    for _ in tb:
        # tests iterator. Should be empty, won't reach here
        assert False
