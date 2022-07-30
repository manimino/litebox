"""
Find objects where the float attribute 'num' is small.

LiteBox outperforms by around 45x here (45ms vs 1ms).
"""

import random
import time

from litebox import LiteBox


def main():
    random.seed(42)
    data = [{"item": i, "num": random.random()} for i in range(10 ** 6)]
    lb = LiteBox(data, {"num": float})
    t0 = time.time()
    lb_matches = lb.find("num <= 0.0001")
    t_litebox = time.time() - t0

    t0 = time.time()
    lc_matches = [d for d in data if d["num"] <= 0.0001]
    t_listcomp = time.time() - t0

    print(f"LiteBox found {len(lb_matches)} matches in {round(t_litebox, 6)} seconds.")
    print(
        f"LiteBox comprehension found {len(lc_matches)} matches in {round(t_listcomp, 6)} seconds."
    )
    print(f"Speedup: {round(t_listcomp / t_litebox)}x")


if __name__ == '__main__':
    main()
