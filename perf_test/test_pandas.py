import random
import time

from rangeindex import RangeIndex


def test_pandas():
    random.seed(42)
<<<<<<< HEAD
    data = [{"item": i, "num": random.random()} for i in range(10 ** 6)]
    ri = RangeIndex(data, {"num": float})
    t0 = time.time()
    ri_matches = ri.find("num <= 0.001")
    t_rangeindex = time.time() - t0

    t0 = time.time()
    lc_matches = [d for d in data if d["num"] <= 0.001]
=======
    data = [{'item': i, 'num': random.random()} for i in range(10**6)]
    ri = RangeIndex(data, {'num': float})
    t0 = time.time()
    ri_matches = ri.find('num <= 0.001')
    t_rangeindex = time.time() - t0

    t0 = time.time()
    lc_matches = [d for d in data if d['num'] <= 0.001]
>>>>>>> 79df7c9 (add perf tests, improve readme)
    t_listcomp = time.time() - t0

    assert len(ri_matches) == len(lc_matches)
    assert len(lc_matches) > 0
    assert t_listcomp / t_rangeindex > 10
    assert t_listcomp < 1
