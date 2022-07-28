import math
import random
import string
import time
from tabulated import Tabulated
from tabulated.constants import PANDAS, SQLITE


class Thing:
    def __init__(self):
        self.f0 = random.random()
        self.f1 = random.random()
        self.i0 = int(random.random() * 10 ** 10)
        self.i1 = int(random.random() * 10 ** 10)
        self.b0 = random.choice([True, False])
        self.b1 = random.choice([True, False])
        self.s0 = [random.choice(string.ascii_lowercase) for _ in range(10)]
        self.s1 = [random.choice(string.ascii_lowercase) for _ in range(10)]
        self.padding = (
            "X" * 100
        )  # makes objects larger, more like our primary use case. Affects benchmarks.


def generate_float_range(
    n_results=1, n_idx=1, dataset_size=10 ** 6
) -> tuple[float, float]:
    """
    Generate a range of float values that, when queried, will return approx n_results items.
    Example: if n_idx is 1, and we want 1/10 of the items in the dataset, we could return (0.5, 0.6)
    as that will be 1/10 of the items.
    But if n_idx is 2, we want a range of 0.1**(1/2) items, to account for the fact that we have
    two independent value ranges.
    """
    width = (n_results / dataset_size) ** (1 / n_idx)
    lim_1 = random.random() * (1 - width)
    lim_2 = lim_1 + width
    return lim_1, lim_2


def query_floats(ri, n_items, n_runs):
    t_tot = 0
    tot_matches = 0
    for _ in range(n_runs):
        lo, hi = generate_float_range(n_items, 2, len(ri))
        t0 = time.time()
        matches = ri.find(f"f0 > {lo} and f0 <= {hi} and f1 > {lo} and f1 <= {hi}")
        t1 = time.time()
        t_tot += (t1 - t0) / n_runs
        tot_matches += len(matches) / n_runs
    return tot_matches, t_tot


def linear_floats(things, n_items, n_runs):
    t_tot = 0
    tot_matches = 0
    for _ in range(n_runs):
        lo, hi = generate_float_range(n_items, 2, len(things))
        t0 = time.time()
        matches = [
            x for x in things if x.f0 > lo and x.f0 <= hi and x.f1 > lo and x.f1 <= hi
        ]
        t1 = time.time()
        t_tot += (t1 - t0) / n_runs
        tot_matches += len(matches) / n_runs
    return tot_matches, t_tot


def time_str(t: float) -> str:
    if t < 10 ** -4:
        return "{}μs".format(round(t * 10 ** 6, 1))
    elif t < 10 ** -1:
        return "{}ms".format(round(t * 10 ** 3, 1))
    else:
        return "{}s".format(round(t, 1))


def num_str(n: int) -> str:
    if n >= 10 ** 9:
        return "{}B".format(int(round(n / 10 ** 9)))
    elif n >= 10 ** 6:
        return "{}M".format(int(round(n / 10 ** 6)))
    elif n >= 10 ** 3:
        return "{}K".format(int(round(n / 10 ** 3)))
    else:
        return str(n)


def run_float_benchmark(engine, n=10 ** 5, n_runs=5):
    results = {"n": num_str(n), "engine": engine}
    print("Generating objects")
    things = [Thing() for _ in range(n)]

    # build
    print(f"building {engine} index")
    t0 = time.time()
    if engine == SQLITE:
        ri = Tabulated(
            things,
            {"f0": float, "f1": float},
            engine=engine,
            table_index=[("f0", "f1")],
        )
    else:
        ri = Tabulated(things, {"f0": float, "f1": float}, engine=engine)
    t1 = time.time()
    results[f"build {engine}"] = time_str(t1 - t0)

    exp_max = int(round(math.log10(n)))
    results["baseline"] = dict()
    results[f"{engine}"] = dict()
    print("running queries")
    for exp in range(0, exp_max + 1):
        n_items = 10 ** exp

        # do linear
        matches, t = linear_floats(things, n_items, n_runs)
        results[f"baseline"][num_str(n_items)] = (num_str(matches), time_str(t))

        # do tabulated
        query_floats(
            ri, n_items, 2
        )  # warm up caches first to produce steady-state-like performance
        matches, t = query_floats(ri, n_items, 2)
        results[engine][num_str(n_items)] = (num_str(matches), time_str(t))

    # __contains__
    to_find = [random.choice(things) for _ in range(100)]
    t0 = time.time()
    for t in to_find:
        _ = t in ri
    t1 = time.time()
    results[engine]["contains"] = time_str((t1 - t0) / len(to_find))

    # update
    to_update = [random.choice(things) for _ in range(100)]
    t0 = time.time()
    for t in to_find:
        ri.update(t, {"f1": 100})
    t1 = time.time()
    results[engine]["update"] = time_str((t1 - t0) / len(to_update))

    # remove
    rm_idxs = list(set(random.choice(range(len(ri))) for _ in range(1000)))[:100]
    to_rm = [things[i] for i in rm_idxs]
    t0 = time.time()
    for t in to_rm:
        ri.remove(t)
    t1 = time.time()
    results[engine]["remove"] = time_str((t1 - t0) / len(to_rm))

    return results


if __name__ == "__main__":
    results = dict()
    for engine in PANDAS, SQLITE:
        results.update(run_float_benchmark(engine, 10 ** 5, n_runs=8))
    for k, v in results.items():
        if k in ["baseline", SQLITE, PANDAS]:
            print(" ", k)
            for ke, ve in v.items():
                print("   ", ke, ve)
        else:
            print(k, v)
