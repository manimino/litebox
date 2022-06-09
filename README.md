# RangeIndex

Find Python objects by `<`, `<=`, `==`, `>=`, `>` on their attributes.

 * Works on your existing Python objects.
 * Objects are only referenced, not copied.
 * Uses an in-memory SQLite under the hood. So it's fast, RAM-efficient, and well-tested.
 
`pip install rangeindex`

### Performance 

 * RangeIndex `find()` is often 100x to 1000x faster than linear search.
 * Uses ~100 bytes of RAM per object indexed, so 1 million objects takes ~100MB.

[Performance details](perf/perf.md)

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

[See docs for more.](https://pypi.org/project/rangeindex/)

### Limitations

 * Indexed fields must be type `float`, `int`, or `str`.
 * If you only need exact-value lookups, consider [HashIndex](https://github.com/manimino/hashindex/) instead.
 * Not thread-safe.
 * Not an entire DB, just the part you probably need.
