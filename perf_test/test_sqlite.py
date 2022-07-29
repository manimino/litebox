import random
import time
from tabulated import Tabulated


class CatPhoto:
    def __init__(self):
        self.name = random.choice(["Luna", "Willow", "Elvis", "Nacho", "Tiger"])
        self.width = random.choice(range(200, 2000))
        self.height = random.choice(range(200, 2000))
        self.brightness = random.random() * 10
        self.image_data = "Y2Ugbidlc3QgcGFzIHVuZSBjaGF0dGU="


def test_perf():
    random.seed(42)

    # Make a million
    photos = [CatPhoto() for _ in range(10 ** 6)]

    # Build Tabulated
    t0 = time.time()
    ri = Tabulated(
        photos,
        on={"height": int, "width": int, "brightness": float, "name": str},
        engine="sqlite",
        table_index=[("width", "height", "brightness")],
    )
    t_build = time.time() - t0

    # Find Tabulated matches
    t0 = time.time()
    ri_matches = ri.find(
        "name == 'Tiger' and height >= 1900 and width >= 1900 and brightness >= 9.0"
    )
    t_tabulated = time.time() - t0

    # Find list comprehension matches
    t0 = time.time()
    lc_matches = [
        p
        for p in photos
        if p.name == "Tiger"
        and p.height >= 1900
        and p.width >= 1900
        and p.brightness >= 9.0
    ]
    t_listcomp = time.time() - t0

    print(
        f"LiteBox found {len(ri_matches)} matches in {round(t_tabulated, 6)} seconds."
    )
    print(
        f"List comprehension found {len(lc_matches)} matches in {round(t_listcomp, 6)} seconds."
    )
    assert len(ri_matches) == len(lc_matches)
    assert len(ri_matches) > 0
    assert (t_listcomp / t_tabulated) > 10  # at least a 10x speedup
    assert (
        t_listcomp < 1
    )  # normally ~50ms. If it's over 1s, the timings are off in general.
    assert t_build < 10  # normally builds in
