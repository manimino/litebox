# RangeIndex

Data structure for looking up Python objects by `<`, `<=`, `==`, `>=`, `>` on their attributes.

`pip install rangeindex`

Putting your objects in a RangeIndex will greatly accelerate lookup times. 

You can expect a speedup of 10x ~ 100x, versus doing a linear scan in Python like
`matching_objects = [obj for obj in objects if obj.x > ...]`.

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
        self.data = 'aXQncyBhIHNlY3JldCB0byBldmVyeWJvZHk='

# Make a million of them
objects = [Object() for _ in range(10**6)]

# Build an index on 'shape' and 'size' containing all objects
ri = RangeIndex({'size': float, 'shape': str}, objects, engine='sqlite')

# Find objects matching criteria
found = ri.find("size < 0.0001 and shape == 'circle'")
```

### Usage

You can `add()`, `add_many()`, `update()`, and `remove()` items from your RangeIndex.

[See docs for more details.](https://pypi.org/project/rangeindex/)

### Engines

RangeIndex has two engines available, `sqlite`, `pandas`. If not specified, it defaults to `sqlite`.

#### SQLite

SQLite uses a B-tree index that dramatically speeds up small queries, as well as `update` and `remove` operations.
However, it slows down to near linear speed or worse with large queries and large numbers of fields indexed. Uses
significant RAM.

#### Pandas

Pandas does not use an index data structure; its performance gains over Python are due to its internal use of numpy 
arrays, which allow vectorized operations. It will outperform by roughly 10x ~ 20x on float and int data, but
underperforms on strings. It uses a small amount of RAM. Its `update` and `remove` operations are slower than SQLite.

### Performance

![Benchmark: sqlite does well on small queries, other engines do better on large queries.](perf/benchmark.png)

This was generated using random-range queries against a dataset of 1 million objects indexed on two `float` fields.
