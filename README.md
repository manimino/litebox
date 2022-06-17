# RangeIndex

Data structure for quickly looking up Python objects by `<`, `<=`, `==`, `>=`, `>` on their attributes.

`pip install rangeindex`

Putting your objects in a RangeIndex will greatly accelerate lookup times. 

For small queries, you can expect a speedup of 10x ~ 100x, versus doing a linear scan in Python such as
`matching_objects = [obj for obj in objects if obj.x = ...]`.

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

### Expected performance

![Benchmark: sqlite does well on small queries, other engines do better on large queries.](perf/benchmark.png)

[See docs for more details.](https://pypi.org/project/rangeindex/)
