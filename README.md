# RangeIndex

Find Python objects by query on their attributes.

`pip install rangeindex`

### Example

Find circle-shaped objects that have size < 3.

```
from rangeindex import RangeIndex

ri = RangeIndex({'size': float, 'shape': str})
for obj in my_objects:
    ri.add(obj)
ri.find([('shape', '==', 'circle'), ('size', '<', 3)])
```

[See docs for more.](https://pypi.org/project/rangeindex/)

### Advantages

 * Works on your existing Python objects.
 * Objects are only referenced, not copied.
 * Uses an in-memory SQLite under the hood. So it's fast, RAM-efficient, and well-tested.

### Limitations

 * Indexed fields must be of type `float`, `int`, or `str`.
 * If you only need exact-value lookups, [HashIndex](github.com/manimino/hashindex) is faster.
 * Not an entire DB, just the part you probably need.
 * Not thread-safe.
