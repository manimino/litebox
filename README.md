# RangeIndex

Data structure for looking up Python objects by `<`, `<=`, `==`, `>=`, `>` on their attributes.

`pip install rangeindex`

 * Lookup is typically 100x to 1000x faster than linear search.
 * Uses an in-memory SQLite. Better than any pure-python index.
 * Uses about 100MB RAM per million objects indexed.
 * Needs Python 3.6+. No other dependencies.

[See docs for more details.](https://pypi.org/project/rangeindex/)

### Example

Make a million objects:
```
import random

class Object:
    def __init__(self):
        self.size = random.random()
        self.shape = random.choice(['square', 'circle'])

objects = [Object() for _ in range(10**6)]
```

Index them on `size` and `shape`:
```
from rangeindex import RangeIndex

ri = RangeIndex({'size': float, 'shape': str})
ri.add_many(objects)
```

Find objects that have `size < 0.01` and `shape == circle`: 
```
found = ri.find([('size', '<', 0.01), ('shape', '==', 'circle')])
for f in found:
    print(f.shape, f.size)
```

### Limitations

 * Indexed fields must be type `float`, `int`, or `str`.
 * Not thread-safe.
 * No persistence. This is for in-memory objects only.
 * Not an entire DB, just the part you probably need.
