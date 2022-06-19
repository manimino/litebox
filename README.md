# RangeIndex

Data structure for finding Python objects by `<`, `<=`, `==`, `>=`, `>` on their attributes.

`pip install rangeindex`

Putting your objects in a RangeIndex will greatly accelerate lookup times. 

You can expect a speedup of 10x ~ 1000x, versus doing a linear scan in Python like
`matches = [obj for obj in objects if obj.x > ...]`.

### Example

Make a million objects, filter them on size and shape. 

```
import random
from rangeindex import RangeIndex

# Define an object
class Object:
    def __init__(self):
        self.size = random.random()
        self.shape = random.choice(['square', 'circle'])
        self.other_data = 'aXQncyBhIHNlY3JldCB0byBldmVyeWJvZHk='

# Make a million of them
objects = [Object() for _ in range(10**6)]

# Build an index on 'shape' and 'size' containing all objects
ri = RangeIndex(objects, 
                on={'size': float, 'shape': str}, 
                engine='sqlite')

# Find matches
matches = ri.find("size < 0.001 and shape == 'circle'")
```

### Usage

You can `add()`, `add_many()`, `update()`, and `remove()` items.

[See docs for more details.](https://pypi.org/project/rangeindex/)

### Engines

RangeIndex has two engines available, `sqlite` and `pandas`. The default is `sqlite`.

#### SQLite

SQLite uses a B-tree index that dramatically speeds up small queries, as well as `update` and `remove` operations.
However, it slows down to near linear speed or worse with large queries. 

#### Pandas

Pandas does not use an index data structure; its performance gains over Python are due to its internal use of numpy 
arrays, which allow vectorized operations. It uses a small amount of RAM. Its `update` and `remove` operations are 
slower than SQLite.

### Performance

![Benchmark: sqlite does well on small queries, other engines do better on large queries.](perf/benchmark.png)

This is a benchmark on random-range queries against a dataset of 1 million (10^6) objects indexed on two `float` 
fields.

The dashed line `linear` is a Python generator expression. `sqlite` and `pandas` are compared to that line.

Note that both axis labels are powers of 10; `10^3` on the Y-axis indicates a 1000X speedup.

SQLite here offers a 15X ~ 1000X speedup when matching 1000 or fewer items, but it is about 3X slower than `linear` when 
matching all objects. 

Pandas is 5X ~ 20X faster than `linear` under all conditions.
