# RangeIndex

Find Python objects by query on their attributes.

`pip install rangeindex`

### Example

Find circle-shaped objects that have size < 3.

```
from rangeindex import RangeIndex

ri = RangeIndex({'size': float, 'shape': str})
ri.add(object)
ri.add_many(list_of_objects)
ri.find([('shape', '==', 'circle'), ('size', '<', 3)])
```

[See docs for more.](https://pypi.org/project/rangeindex/)

### Advantages

 * Works on your existing Python objects.
 * Objects are only referenced, not copied.
 * Uses an in-memory SQLite under the hood. So it's fast, RAM-efficient, and well-tested.

### Limitations

 * Indexed fields must be type `float`, `int`, or `str`.
 * If you only need exact-value lookups, [HashIndex](https://github.com/manimino/hashindex/) is faster.
 * Not an entire DB, just the part you probably need.
 * Not thread-safe.

### Typical performance

 * Add an object: a few microseconds
 * Add a million objects: a few seconds
 * Find 100 matching objects in a set of 1 million: 0.1 milliseconds (~100x faster than linear search).
 * However, finds that return all / most of your objects will be slower than linear search. 
 * RAM usage will depend on how many indices you have. For `float` and `int` indices, 
   it's about 50 bytes per object per index. So 10M objects * 2 indices * 50 bytes = 1GB.
