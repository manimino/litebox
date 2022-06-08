from typing import Iterable, Optional, List, Any, Dict, Set, Tuple

# These size thresholds determine whether a tuple or set is used to store the matching objects for a field value.
# When there are few objects, a tuple's RAM-efficiency makes it the better container.
# At a high number of objects, a set becomes necessary for lookup speed reasons.
# There are two thresholds to give hysteresis; we don't want to convert between the two repeatedly for small changes.
THRESH_LOW = 50
THRESH_HIGH = 100


"""
implementation idea

we use sqlite
on init, user tells us class of each field (number or str)
we use that to build a table with 1 column per field plus 1 column of obj ids
index on every column except obj id
then do lookups via um
sqlalchemy maybe
or similar
"""

from rangeindex import SqliteIndex


class RangeIndex:
    def __init__(self, fields: Dict[str, type]):
        self.objs = dict()
        self.idx = SqliteIndex(fields)

    def _matches(self, obj, field, op, val):
        if op in ['==', '=']:
            return obj.__dict__[field] == val
        if op == '>':
            return obj.__dict__[field] > val
        if op == '>=':
            return obj.__dict__[field] >= val
        if op == '<':
            return obj.__dict__[field] < val
        if op == '<=':
            return obj.__dict__[field] <= val
        raise SomeError('bad op')

    def find(self, query: List[Tuple]) -> List:
        """
        :param query: [('field1', '>', 0.1), ('field2', '<', 42.5)]

        :return: List of matching objects
        """
        # Linear-time first pass implementation for minimum-viable-product reasons
        # will use bplustree when implemented
        matched_ptrs = set(self.objs.keys())

        for q in query:
            for field, op, val in q:
                for ptr in matched_ptrs:
                    obj = self.objs[ptr]
                    if not self._matches(obj, field, op, val):
                        matched_ptrs.remove(ptr)

        return [self.objs[ptr] for ptr in self.objs]


class SomeError(Exception):
    pass
