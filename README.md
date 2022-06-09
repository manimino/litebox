# RangeIndex

Find Python objects by their attributes.

`pip install rangeindex`

Find objects that have `shape==circle` and `size < 5`:

```
from rangeindex import RangeIndex

ri = RangeIndex({'size': float, 'shape': str})
ri.add(object)
ri.add_many(list_of_objects)
ri.find([('shape', '==', 'circle'), ('size', '<', 3)])
```

[See docs for more.](https://pypi.org/project/rangeindex/)

### Performance 

 * RangeIndex `find()` is often 100x to 1000x faster than linear search.
 * Uses ~100 bytes of RAM per object indexed, so 1 million objects takes ~100MB.

[More details](perf/perf.md)

### Advantages

 * Works on your existing Python objects.
 * Objects are only referenced, not copied.
 * Uses an in-memory SQLite under the hood. So it's fast, RAM-efficient, and well-tested.

### Limitations

 * Indexed fields must be type `float`, `int`, or `str`.
 * If you only need exact-value lookups, consider [HashIndex](https://github.com/manimino/hashindex/) instead.
 * Not thread-safe.
 * Not an entire DB, just the part you probably need.
