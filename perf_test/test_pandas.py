import random
import string
import time

from tabulated import PandasBox


def padding() -> str:
    """A random string to increase space between objects, sabotaging cache line performance"""
    return ''.join([random.choice(string.ascii_lowercase) for _ in range(100)])


def test_pandas():
    random.seed(42)
    data = [{"item": i, "num": random.random(), 'data': padding()} for i in range(10 ** 6)]
    ri = PandasBox(data, {"num": float})
    t0 = time.time()
    ri_matches = ri.find("num <= 0.001")
    t_tabulated = time.time() - t0

    t0 = time.time()
    lc_matches = [d for d in data if d["num"] <= 0.001]
    t_listcomp = time.time() - t0

    print(t_listcomp, t_tabulated)
    assert len(ri_matches) == len(lc_matches)
    assert len(lc_matches) > 0
    assert t_listcomp / t_tabulated > 10
    assert t_listcomp < 1


if __name__ == '__main__':
    test_pandas()
