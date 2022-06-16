# RangeIndex

Data structure for looking up Python objects by `<`, `<=`, `==`, `>=`, `>` on their attributes.

`pip install rangeindex`

### Features

 * RangeIndex lookup is typically 100x to 1000x faster than looping over all your objects.
 * Supports `class`, `dataclass`, and `namedtuple` objects.
 * Indexing a million objects takes about 100MB of RAM.
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
        self.data = 'aXQncyBhIHNlY3JldCB0byBldmVyeWJvZHk='

objects = [Object() for _ in range(10**6)]
```

Index them on `size` and `shape`:
```
from rangeindex import RangeIndex

ri = RangeIndex({'size': float, 'shape': str}, objects)
```

Find objects that have `size < 0.001` and `shape == circle`: 
```
found = ri.find('size < 0.001 and shape == "circle"')
for f in found:
    print(f.shape, f.size)
```

### Limitations

 * Indexed fields must be type `float`, `int`, or `str`.
 * Not thread-safe.
