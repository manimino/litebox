# LiteBox

Container for finding Python objects by attribute using SQLite.

`pip install litebox`

[![tests Actions Status](https://github.com/manimino/litebox/workflows/tests/badge.svg)](https://github.com/manimino/litebox/actions)
[![performance Actions Status](https://github.com/manimino/litebox/workflows/performance/badge.svg)](https://github.com/manimino/litebox/actions)

____

### Usage
```
from litebox import LiteBox
lb = LiteBox(
    [{'num': 1, 'size': 1000, 'shape': 'square'}],   # provide a collection of objects or dicts 
    {'size': int, 'shape': str})                     # specify attributes to store
lb.find('size >= 1000 and shape == "square"')        # find by attribute value
```

The objects can be anything - `class`, `dataclass`, `namedtuple`, `dict`, `string`, `int`, etc.

LiteBox supports `add()`, `add_many()`, `update()`, and `remove()`.

#### Nested attributes

Define a function to access nested or derived attributes.

```
from litebox import LiteBox

objs = [
    {'num': 1, 'nested': {'a': 2, 'b': 3}}, 
    {'num': 2, 'nested': {'a': 4, 'b': 5}}
]

def nested_attr(obj):
    return obj['nested']['a']

lb = LiteBox(objs, {nested_attr: int})
lb.find('nested_attr == 2')  # returns obj 1
```

____

### How it works

When you do: `LiteBox(list_of_objects, on={'size': int, 'shape': string})`

A SQLite table is created with 3 columns:
 - size
 - shape
 - Python object reference

On `find()`, a query will run to find the matching objects.

Only the relevant attributes of the object are copied into the table. The rest of the object remains in memory.

An ideal use case is when you have "heavy" objects containing images / audio / large texts, plus some small
metadata fields that you want to find by. Just make a LiteBox on the metadata, and use it to find
the object without needing to serialize / deserialize the heavy stuff.

LiteBox is especially good when finding by `<` and `>`. If you only need `==`, consider 
[HashBox](https://pypi.org/project/hashbox/) -- it is based on dict lookups which are faster in that case. 

____

## API

### Init 

```
LiteBox(
        objs: Optional[Iterable[Any]] = None,
        on: Optional[Dict[str, Any]] = None,
        index: Optional[List[ Union[Tuple[str], str]]] = None
)
```

Creates a LiteBox.

 - `objs` is optional. It can be any container of class, dataclass, dict, or namedtuple objects.
 - `on` is required. It specifies the attributes and types to index. The allowed types are float, int, bool, and str.
 - `index` specifies the indices to create on the SQLite table. If unspecified, a single-column index is made on each
attribute. 

The `index` parameter is the key to getting good performance. A multi-column index can often speed up `find()` 
operations. `index=[('a', 'b', 'c'), 'd']` will create a multi-column index on `(a, b, c)` and a single-column index 
on `d`.  Conversely, some columns such as those containing only a few different values may perform better without an 
index.

See [SQLite index documentation](https://www.sqlite.org/queryplanner.html) for more insights.

### find()

`find(where: Optional[str]) -> List` finds objects matching the query string in `where`.

Examples: 
 - `lb.find('b == True and string == "okay"')`
 - `lb.find('(x == 0 and y >= 1000.0) or x == 9')`
 - `lb.find('x is null')`

If `where` is unspecified, all objects in the container are returned. 

Consult the syntax for [SQLite queries](https://www.sqlite.org/lang_select.html) as needed.

### add(), add_many()

```
add(obj:Any)
add_many(objs:Iterable[Any])
```

The `add()` method adds a single object. If you have many objects, it is much faster to `add_many()` than it is to
call `add()` on each one.

If an added object is missing an attribute, the object will still be added. The missing attribute will be given a 
`None` value.

### update()

`update(self, obj: Any)` updates attributes of a single object in the index. 
It's just a shorthand for `remove()` and then `add()`.

If you change an object's attributes without calling `update()`, the LiteBox will be out of sync and
return stale results. Consider implementing a `setattr` listener on your object to update LiteBox when your objects
change.

### remove()

`remove(self, obj: Any)` removes an object. 

### Container methods

You can do the usual container things:
 - Length: `len(lb)`
 - Contains: `obj in lb`
 - Iteration: `for obj in lb: ...`

____

## Performance

LiteBox can be tremendously faster (>100x) than linear-time methods such as Python list comprehension. Speedup depends 
primarily on number of objects returned; fewer is faster.

See performance tests in [examples](/examples).
