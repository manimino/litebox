"""
You have a million cat photos. Find big, bright pictures of Tiger the Cat.

LiteBox outperforms a list comprehension by about 20x in this case (60ms vs 3ms).
"""

import random
import time
from litebox import LiteBox


class CatPhoto:
    def __init__(self):
        self.name = random.choice(["Luna", "Willow", "Elvis", "Nacho", "Tiger"])
        self.width = random.choice(range(200, 2000))
        self.height = random.choice(range(200, 2000))
        self.brightness = random.random() * 10
        self.image_data = "Y2Ugbidlc3QgcGFzIHVuZSBjaGF0dGU="


random.seed(42)

# Make a million
photos = [CatPhoto() for _ in range(10 ** 6)]

# Build LiteBox

t0 = time.time()
tb = LiteBox(
    photos,
    on={"height": int, "width": int, "brightness": float, "name": str},
    index=[("width", "height", "brightness")],
)
t_build = time.time() - t0

# Find LiteBox matches
t0 = time.time()
tb_matches = tb.find(
    "name == 'Tiger' and height >= 1900 and width >= 1900 and brightness >= 9.0"
)
t_litebox = time.time() - t0
print(t_litebox)

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
print(t_listcomp)

print(f"LiteBox found {len(tb_matches)} matches in {round(t_litebox, 6)} seconds.")
print(
    f"List comprehension found {len(lc_matches)} matches in {round(t_listcomp, 6)} seconds."
)
print(f"Speedup: {round(t_listcomp / t_litebox)}x")
