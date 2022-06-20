# RangeIndex

[![tests Actions Status](https://github.com/manimino/rangeindex/workflows/tests/badge.svg)](https://github.com/manimino/rangeindex/actions)

Data structure for finding Python objects by `<`, `<=`, `==`, `>=`, `>` on their attributes.

`pip install rangeindex`

### Usage
```
from rangeindex import RangeIndex
ri = RangeIndex(list_of_objects, on={'size': int, 'brightness': float})
matching_objects = ri.find('size >= 1000 and brightness > 0.5')
```

You can `add()`, `add_many()`, `update()`, and `remove()` items from a RangeIndex.

[Docs]()

### How it works

That RangeIndex object will contain a table with 3 columns:
 - size
 - brightness
 - a Python object reference

On `find()`, a query will run to find the matching objects.

### Example

You have a million cat photos. Find big, bright pictures of Tiger The Cat.

```
import random
import time
from rangeindex import RangeIndex

class CatPhoto:
    def __init__(self):
        self.width = random.choice(range(200, 2000))
        self.height = random.choice(range(200, 2000))
        self.brightness = random.random()*10
        self.name = random.choice(['Luna', 'Willow', 'Elvis', 'Nacho', 'Tiger'])
        self.image_data = 'Y2Ugbidlc3QgcGFzIHVuZSBjaGF0dGU='

# Make a million
photos = [CatPhoto() for _ in range(10**6)]

# Build RangeIndex
ri = RangeIndex(photos, 
                on={'height': int, 'width': int, 'brightness': float, 'name': str}, 
                engine='sqlite',
                table_index=[('width', 'height', 'brightness')])
                
# Find matches
matches = ri.find("height > 1900 and width >= 1900 and brightness >= 9 and name='Tiger'")
```

In this case, RangeIndex `find()` is more than 10x faster than the equivalent Python expression:

`matches = [p for p in photos if p.height >= 1900 and p.width >= 1900 and p.brightness >= 9 and p.name='Tiger']`

### Engine Comparison

RangeIndex has two engines available, `sqlite` and `pandas`. The default is `sqlite`.

If your queries typically return just a few results, use `engine=sqlite`. But if you're doing full table 
scans often, `engine=pandas` will be faster. 

#### Data

|                | Baseline | Sqlite | Pandas |
|----------------|----------|--------|--------|
| Get 1 item     | 1.14s    | 0.9ms  | 41.7ms |
| Get 10 items   | 1.10s    | 2.7ms  | 42.4ms |
| Get 100 items  | 1.09s    | 9.6ms  | 42.5ms |
| Get 1K items   | 1.20s    | 46.8ms | 48.9ms |
| Get 10K items  | 1.30s    | 0.28s  | 83.6ms |
| Get 100K items | 1.83s    | 2.16s  | 0.198s |
| Get 1M items   | 2.61s    | 7.95s  | 0.431s |
| Get 10M items  | 2.64s    | 8.11s  | 0.45s  |

This is a benchmark on random-range queries against a dataset of 10 million (10^7) objects indexed on two numeric 
fields. `Baseline` is a Python list comprehension.

#### Graph

![Benchmark: sqlite does well on small queries, other engines do better on large queries.](perf/benchmark.png)

This is the same data in graph form, showing relative speedup. Each line is divided by `baseline`. 
Note that both axis labels are powers of 10; `10^3` on the Y-axis indicates a 1000X speedup.
