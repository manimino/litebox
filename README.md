# Tabulated

[![tests Actions Status](https://github.com/manimino/tabulated/workflows/tests/badge.svg)](https://github.com/manimino/tabulated/actions)
[![performance Actions Status](https://github.com/manimino/tabulated/workflows/performance/badge.svg)](https://github.com/manimino/tabulated/actions)

Container for finding Python objects by `<`, `<=`, `==`, `>=`, `>` on their attributes.

`pip install tabulated`

____

### Usage
```
from tabulated import Tabulated
ri = Tabulated(
    [{'item': 1, 'size': 1000, 'shape': 'square'}],  # list of objects / dicts 
    {'size': int, 'shape': str})                     # which fields to index on
ri.find('size >= 1000 and shape == "square"')
```

The objects can be any container of `class`, `dataclass`, `namedtuple`, or `dict` objects.

You can `add()`, `add_many()`, `update()`, and `remove()` items from a Tabulated.

____

### How it works

When you do: `Tabulated(list_of_objects, on={'size': int, 'brightness': float})`

A table is created with 3 columns:
 - size
 - brightness
 - Python object reference

On `find()`, a query will run to find the matching objects.

____

## Methods

### Init

```
Tabulated(
        objs: Optional[Iterable[Any]] = None,
        on: Optional[Dict[str, Any]] = None,
        engine: str = SQLITE,
        **kwargs
)
```

Creates a Tabulated.

 - `objs` is optional. It can be any container of class, dataclass, dict, or namedtuple objects.
 - `on` is required. It specifies the attributes and types to index. The allowed types are float, int, bool, and str.
 - `engine` is either 'sqlite' or 'pandas', defaults to sqlite. Pandas is an optional dependency; you only need to
install pandas if using that engine.

If the engine is sqlite, you may optionally specify `table_index`. This controls the table index that SQLite uses when 
performing queries. If unspecified, a single-column index is made on each
attribute. Example: `table_index=[('a', 'b', 'c'), ('d')]` will create a multi-column index on `(a, b, c)` and a 
single-column index on `d`. Multi-column indexes will often speed up `find()` operations; see 
[SQLite documentation](https://www.sqlite.org/queryplanner.html).

### add(), add_many()

```
add(obj:Any)
add_many(objs:Iterable[Any])
```

You can add a single object with `add()`. If you have many objects, it is much faster to `add_many()` than it is to
call `add()` on each.

If an added object is missing an attribute, the object will still be added. The missing attribute will be given a 
null value in the index.

### find()

`find(where: Optional[str]) -> List` finds objects matching the query string in `where`.

Examples: 
 - `ri.find('b == True and string == "okay"')`
 - `ri.find('(x == 0 and y >= 1000.0) or x == 9')`

If `where` is unspecified, all objects in the Tabulated are returned. 

The syntax of `where` is nearly identical between pandas and sqlite. Exceptions:
 - In sqlite, use `find('x is null')` / `find('x is not null')`. 
 - In pandas, use `find('x != x')` to match nulls, or `find('x == x')` for non-nulls. 
 - Sqlite accepts either `=` or `==` for equality; pandas accepts only `==`.
 
Consult the syntax for [SQLite queries](https://www.sqlite.org/lang_select.html) or 
[pandas queries](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.query.html) as needed.

### update()

`update(self, obj: Any, updates: Dict[str, Any])` updates attributes of a single object in the index.

`updates` is a dict containing the new values for each changed attribute, e.g. `{'x': 5.5, 'b': True}`.

If you change an indexed object's attributes without calling `update()`, the Tabulated will be out of sync and
return inaccurate results. 

`update()` will changes both the value in the Tabulated table and the object's value.

Update is fast (less than 1 ms), it's O(log n) in both sqlite and pandas.

### remove()

`remove(self, obj: Any)` removes an object. 

Remove is fast (less than 1ms) in SQLite but slower (tens of ms) in Pandas. 
This is because removing an item requires rebuilding arrays there.

### Container methods

You can do the container things:
 - Length: `len(ri)`
 - Contains: `obj in ri`
 - Iteration: `for obj in ri: ...`

____

## Performance

### Engine Comparison

Tabulated has two engines available, `sqlite` and `pandas`. The default is `sqlite`.

If your queries typically return just a few results, use `engine='sqlite'`. But if you're doing full table 
scans often, `engine='pandas'` will be faster. 

#### Time Comparison

|                 | Baseline | Sqlite | Pandas |
|-----------------|----------|--------|--------|
| Find 1 item     | 0.9s     | 0.2ms  | 43.1ms |
| Find 10 items   | 0.9s     | 0.7ms  | 44.9ms |
| Find 100 items  | 1.0s     | 1.9ms  | 43.8ms |
| Find 1K items   | 1.0s     | 6.7ms  | 43.9ms |
| Find 10K items  | 1.1s     | 27.2ms | 47.6ms |
| Find 100K items | 1.2s     | 0.18s  | 88.3ms |
| Find 1M items   | 1.7s     | 1.37s  | 0.24s  |
| Find 10M items  | 2.9s     | 10.6s  | 0.45s  |

This is a benchmark on random range queries against a dataset of 10 million (10^7) objects indexed on two numeric 
fields. `Baseline` is a Python list comprehension.

#### Graph

![Benchmark: sqlite does well on small queries, other engines do better on large queries.](notebooks/benchmark.png)

This is the same data in graph form, showing relative speedup. Each line is divided by `baseline`. 
Note that both axis labels are powers of 10. So `10^3` on the Y-axis indicates a 1000X speedup.

____

## Performance Examples

### SQLite engine, multi-column index

You have a million cat photos. Find big, bright pictures of Tiger the Cat.

```
import random
import time
from tabulated import Tabulated


class CatPhoto:
    def __init__(self):
        self.name = random.choice(["Luna", "Willow", "Elvis", "Nacho", "Tiger"])
        self.width = random.choice(range(200, 2000))
        self.height = random.choice(range(200, 2000))
        self.brightness = random.random() * 10
        self.image_data = "Y2Ugbidlc3QgcGFzIHVuZSBjaGF0dGU="


random.seed(42)

# Make a million
photos = [CatPhoto() for _ in range(10 ** 6)]

# Build Tabulated

t0 = time.time()
ri = Tabulated(
    photos,
    on={"height": int, "width": int, "brightness": float, "name": str},
    engine="sqlite",
    table_index=[("width", "height", "brightness")],
)
t_build = time.time() - t0

# Find Tabulated matches
t0 = time.time()
ri_matches = ri.find(
    "name == 'Tiger' and height >= 1900 and width >= 1900 and brightness >= 9.0"
)
t_tabulated = time.time() - t0
print(t_tabulated)

# Find list comprehension matches
t0 = time.time()
lc_matches = [p for p in photos if p.name == 'Tiger' and p.height >= 1900 and p.width >= 1900 and p.brightness >= 9.0]
t_listcomp = time.time() - t0
print(t_listcomp)

print(f'Tabulated found {len(ri_matches)} matches in {round(t_tabulated, 6)} seconds.')
print(f'List comprehension found {len(lc_matches)} matches in {round(t_listcomp, 6)} seconds.')
print(f'Speedup: {round(t_listcomp / t_tabulated)}x')
```

Tabulated returns the same matches about 20x faster in this case (60ms vs 3ms).

### Pandas engine

```
import random
import time

from tabulated import Tabulated


random.seed(42)
data = [{'item': i, 'num': random.random()} for i in range(10**6)]
ri = Tabulated(data, {'num': float})
t0 = time.time()
ri_matches = ri.find('num <= 0.001')
t_tabulated = time.time() - t0

t0 = time.time()
lc_matches = [d for d in data if d['num'] <= 0.001]
t_listcomp = time.time() - t0

print(f'Tabulated found {len(ri_matches)} matches in {round(t_tabulated, 6)} seconds.')
print(f'List comprehension found {len(lc_matches)} matches in {round(t_listcomp, 6)} seconds.')
print(f'Speedup: {round(t_listcomp / t_tabulated)}x')
```

Tabulated outperforms by around 45x here (45ms vs 1ms).
