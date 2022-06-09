import sqlite3
from collections.abc import Iterable
from typing import List, Tuple, Dict, Any, Optional
import ctypes

PYTYPE_TO_SQLITE = {
    int: 'INTEGER',
    str: 'TEXT',
    float: 'REAL'
}

PYOBJ_COL = 'py_obj_id_reserved'

table_id = 0  # keeps sqlite table names unique when using multiple indices


def get_next_table_id():
    global table_id
    table_id += 1
    return table_id


class RangeIndex:
    def __init__(self, fields: Dict[str, type]):
        self._validate_fields(fields)
        self.objs = dict()  # maps {id(object): object}
        self.table_name = 'ri_' + str(get_next_table_id())
        self.conn = sqlite3.connect(':memory:')
        self.fields = fields

        # TODO: store a sorted (list? deque? skiplist?) of tuples of (key, obj)
        # when there are many object keys found, it will be faster to
        # linear scan over all our objects and match keys
        # than it is to do a million dict lookups.

        # create sqlite table
        tbl = [f'CREATE TABLE {self.table_name} (']
        for field, pytype in fields.items():
            s_type = PYTYPE_TO_SQLITE[pytype]
            tbl.append(f'{field} {s_type},')
        tbl.append(f'{PYOBJ_COL} INTEGER')
        tbl.append(')')
        cur = self.conn.cursor()
        cur.execute('\n'.join(tbl))

        # create indices on all columns
        # pyobj column needs an index to do fast updates / deletes
        for col in self.fields:
            idx = f'CREATE INDEX idx_{col} ON {self.table_name}({col})'
            cur.execute(idx)

    def add(self, obj: Any):
        # TODO make this a constant
        col_str = ','.join(self.fields.keys()) + f',{PYOBJ_COL}'
        value_str = ','.join(['?']*(len(self.fields)+1))
        q = f'INSERT INTO {self.table_name} ({col_str}) VALUES({value_str})'

        ptr = id(obj)
        self.objs[ptr] = obj
        values = [obj.__dict__.get(c, None) for c in self.fields] + [ptr]
        cur = self.conn.cursor()
        cur.execute(q, values)
        self.conn.commit()

    def add_many(self, objs: List[any]):
        value_str = ','.join(['?'] * (len(self.fields) + 1))
        col_str = ','.join(self.fields.keys()) + f',{PYOBJ_COL}'
        q = f'INSERT INTO {self.table_name} ({col_str}) VALUES ({value_str})'

        rows = []
        for obj in objs:
            ptr = id(obj)
            self.objs[ptr] = obj
            values =  [obj.__dict__.get(c, None) for c in self.fields] + [ptr]
            rows.append(values)

        cur = self.conn.cursor()
        cur.executemany(q, rows)
        self.conn.commit()

    def remove(self, obj: Any):
        ptr = id(obj)
        del self.objs[ptr]
        q = f'DELETE FROM {self.table_name} WHERE {PYOBJ_COL}=?'
        cur = self.conn.cursor()
        cur.execute(q, (ptr,))
        self.conn.commit()

    def update(self, obj: Any, updates: Dict[str, Any]):
        set_cols = []
        set_values = []
        for col in self.fields:
            if col in updates:
                set_cols.append(f'{col}=?')
                set_values.append(updates[col])
        set_str = ','.join(set_cols)
        q = f'UPDATE {self.table_name} SET {set_str} WHERE {PYOBJ_COL}=?'
        ptr = id(obj)
        set_values.append(ptr)
        print(q, set_values)
        cur = self.conn.cursor()
        cur.execute(q, set_values)
        self.conn.commit()

    def find(self, query: Optional[List[Tuple]] = None) -> List[Any]:
        if not query:
            return list(self.objs.values())
        return list(self.objs[ptr] for ptr in self.find_obj_ids(query))

    def find_obj_ids(self, query: Optional[List[Tuple]] = None) -> List:
        """Find Python object ids that match the query constraints."""
        self._validate_query(query)
        if not query:
            return tuple(self.objs.keys())
        q = [f'SELECT {PYOBJ_COL} FROM {self.table_name} WHERE']
        values = []
        for i, triplet in enumerate(query):
            field, op, value = triplet
            values.append(value)
            if i < len(query)-1:
                q.append(f'{field} {op} ? AND')
            else:
                q.append(f'{field} {op} ?')
        cur = self.conn.cursor()
        rows = cur.execute('\n'.join(q), values)
        return list(r[0] for r in rows.fetchall())

    def _validate_fields(self, fields):
        if not fields or not isinstance(fields, dict):
            raise InvalidFields("Need a nonempty dict of fields, e.g. {'x': float}")
        for i, f in enumerate(fields):
            if fields[f] not in [int, float, str]:
                raise TypeError('Expected int, float, or str field type at position {}, but got {}'.format(i, fields[f]))
            if not isinstance(f, str):
                raise TypeError('Field name must be a str, got {} at position {}'.format(f, i))

    def _validate_query(self, query: Optional[List[Tuple]]):
        if query is None:
            return
        if not isinstance(query, Iterable):
            raise QueryMalformedError("Query must be a list of tuples, example: [('field', '<', 3)]")
        if not len(query):
            return
        for i, triplet in enumerate(query):
            if not isinstance(triplet, Iterable):
                raise QueryMalformedError("Query must be a list of tuples, example: [('field', '<', 3)]")
            if len(triplet) != 3:
                raise QueryMalformedError("Error in query element {}: expected a tuple of length 3, but got {}".format(
                    i, triplet))
            field, op, value = triplet
            if op.upper() not in ['<', '>', '==', '=', '!=', '>=', '<=', 'IS', 'IS NOT']:
                raise QueryBadOperatorError("Error in query at {}: {} is not a valid operator".format(triplet, op))
            if field not in self.fields:
                raise QueryUnknownFieldError("Error in query at {}: {} is not an indexed field".format(
                    triplet, field))
            if value is not None:
                if self.fields[field] in [int, float] and type(value) not in [int, float]:
                    raise QueryTypeError("Error in query {}: expected type  but got {}".format(
                        triplet, self.fields[field], type(value)))
                elif self.fields[field] == str and type(value) != str:
                    raise QueryTypeError("Error in query {}: expected type  but got {}".format(
                        triplet, self.fields[field], type(value)))
            if value is None and op.upper() not in ['IS', 'IS NOT']:
                raise QueryBadNullComparator("Error in query at {}: Use 'IS' or 'IS NOT' as the operator "
                                             "when comparing to None values.".format(triplet))


class InvalidFields(Exception):
    pass


class QueryMalformedError(Exception):
    pass


class QueryBadOperatorError(Exception):
    pass


class QueryTypeError(Exception):
    pass


class QueryUnknownFieldError(Exception):
    pass


class QueryBadNullComparator(Exception):
    pass