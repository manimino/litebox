# RangeIndex Performance

#### Insert speed

 * Add an object: a few microseconds
 * Add a million objects: a few seconds
 * Using `add_many(list_of_objs)` instead of calling `add(obj)` for each object is about twice as fast.
 
#### Find speed (vs. linear search)

If you were not using a RangeIndex, you might use Python to get all 
matching objects in linear time. For example, `filter(lambda obj: obj.x < 3, objects)` or 
`tuple(obj for obj in objects if obj.x < 3)`. 

RangeIndex will usually be much faster than a linear search. The speedup depends on how many 
objects your `ri.find()` returns. The break-even point is where `find` matches about 5~10% of the dataset.

Example - when you have 1 million objects:

**Num of matches**| **RangeIndex** | **linear search** |**Speedup**
:-----:|:--------------:|:-----------------:|:-----:
1|     0.1ms      |       80ms       |784x
10|     0.12ms     |       80ms       |638x
100|     0.33ms     |       80ms       |239x
1K|     1.8ms      |       80ms        |45x
10K|      10ms      |       80ms        |5x
100K|     160ms      |       80ms        |0.5x
1M|     1.42s      |       120ms       |0.1x

If you have fewer than 1000 objects, just use a linear search. Beyond that, RangeIndex will be useful.

#### Memory usage

 * Indexing an object costs about 70 bytes of overhead. 
 * Each indexed numeric field costs about 30 bytes. 
 * Indexing 1 million objects on one numeric field takes about 100MB. 
 * Indexing 1 million objects on 10 numeric fields takes about 400MB. 
 * Indexing on string fields will vary according to the length of the strings.
