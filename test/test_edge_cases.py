from dataclasses import dataclass

from litebox.main import LiteBox


@dataclass
class Thing:
    x: int = 0
    y: float = 0.0
    s: str = ""


def test_index_on_missing_attributes():
    lb = LiteBox(on={"z": float})
    t = Thing()
    lb.add(t)
    found = lb.find("z is null")
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
    lb = LiteBox(on={"x": int})
    lb.add_many(things_1)
    lb.add_many(things_2)
    lb.add(thing_3)
    assert len(lb.find("x == 1")) == 10
    assert len(lb.find("x == 2")) == 10
    assert len(lb.find("x == 3")) == 1
    assert len(lb.find()) == 21


def test_add_one_we_already_have():
    things = [Thing(x=1) for _ in range(10)]
    lb = LiteBox(on={"x": int})
    lb.add_many(things)
    lb.add(things[0])
    assert len(lb) == 10


def test_add_many_we_already_have():
    things_1 = [Thing(x=1) for _ in range(10)]
    things_2 = things_1 + [Thing(x=2) for _ in range(10)]
    lb = LiteBox(on={"x": int})
    lb.add_many(things_1)
    lb.add_many(things_2)
    assert len(lb.find("x == 1")) == 10
    assert len(lb.find("x == 2")) == 10
    assert len(lb) == 20


def test_add_many_with_duplicates():
    things = [Thing(x=1) for _ in range(10)]
    double_things = things + things
    lb = LiteBox(on={"x": int})
    lb.add_many(double_things)
    assert len(lb) == 10


def test_find_on_empty_idx():
    lb = LiteBox(on={"x": float})
    assert len(lb.find("x != x")) == 0


def test_update_many():
    things = [Thing(x=1) for _ in range(10)]
    lb = LiteBox(things, on={"x": int})
    for i in range(5):
        things[i].x = 2
        lb.update(things[i])
    assert len(lb.find("x == 1")) == 5
    assert len(lb.find("x == 2")) == 5


def test_remove_many():
    things = [Thing(x=1) for _ in range(10)]
    lb = LiteBox(things, on={"x": int})
    for i in range(5):
        lb.remove(things[i])
    assert len(lb) == 5
    assert all([t not in lb for t in things[:5]])
    print("expected:", sorted([id(t) for t in things[5:]]))
    assert all([t in lb for t in things[5:]])


def test_empty():
    lb = LiteBox(on={"x": int})
    assert lb not in lb
    assert not lb.find("x == 3")
    assert len(lb) == 0
    for _ in lb:
        # tests iterator. Should be empty, won't reach here
        assert False
