import duckdb
import pandas as pd
from collections.abc import Iterable
from typing import List, Tuple, Dict, Any, Optional

PYTYPE_TO_SQLITE = {
    int: 'BIGINT',
    str: 'VARCHAR',
    float: 'DOUBLE'
}

PYOBJ_COL = 'obj_id_reserved'

table_id = 0  # keeps table names unique when using multiple indices


def get_next_table_id():
    global table_id
    table_id += 1
    return table_id


class RangeIndex:

    def __init__(self, fields: Dict[str, Any]):
        self._validate_fields(fields)
        self.fields = fields
        self.objs = dict()  # maps {id(object): object}
        self.table_name = 'table_' + str(get_next_table_id())
        self.con = duckdb.connect(database=':memory:')

        # create duckdb table
        cols = [f'{field} {PYTYPE_TO_SQLITE[ftype]}' for field, ftype in fields.items()]
        cols.append(f'{PYOBJ_COL} UBIGINT')
        col_str = ', '.join(cols)
        self.con.execute(f"CREATE TABLE {self.table_name}({col_str})")

    def add(self, obj: Any):
        ptr = id(obj)
        values = [getattr(obj, f, None) for f in self.fields] + [ptr]
        qmarks = ','.join(['?']*(len(self.fields) + 1))
        self.con.execute(f'INSERT INTO {self.table_name} VALUES ({qmarks})', values)
        self.objs[ptr] = obj

    def add_many(self, objs: List[Any]):
        # Create a temporary dataframe and add it to the DB.
        # This is recommended by the DuckDB docs, and is much faster than inserting with cursor.executemany().
        df = pd.DataFrame({
            field: [getattr(obj, field, None) for obj in objs] for field in self.fields
        })
        obj_ids = [id(obj) for obj in objs]
        df[PYOBJ_COL] = obj_ids
        self.objs.update(zip(obj_ids, objs))
        self.con.execute(f"INSERT INTO {self.table_name} SELECT * FROM df")

    def find(self, query: Optional[List[Tuple]] = None) -> List:
        if not query:
            return list(self.objs.values())
        return list(self.objs[ptr] for ptr in self.find_obj_ids(query))

    def find_obj_ids(self, query: Optional[List[Tuple]] = None) -> List:
        self._validate_query(query)
        q = [f'SELECT {PYOBJ_COL} FROM {self.table_name} WHERE']
        values = []
        for i, triplet in enumerate(query):
            field, op, value = triplet

            if value is None:
                q.append(f'{field} {op} NULL')
            else:
                q.append(f'{field} {op} ?')
                values.append(value)
            if i < len(query)-1:
                q.append('AND')

        self.con.execute('\n'.join(q), values)
        rows = list(r[0] for r in self.con.fetchall())
        return rows

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
        self.con.execute(q, set_values)

    def remove(self, obj: Any):
        ptr = id(obj)
        del self.objs[ptr]
        q = f'DELETE FROM {self.table_name} WHERE {PYOBJ_COL}=?'
        self.con.execute(q, (ptr,))

    @staticmethod
    def _validate_fields(fields):
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
                    raise QueryTypeError("Error in query {}: expected type {} but got {}".format(
                        triplet, self.fields[field], type(value)))
                elif self.fields[field] == str and type(value) != str:
                    raise QueryTypeError("Error in query {}: expected type {} but got {}".format(
                        triplet, self.fields[field], type(value)))
            if value is None and op.upper() not in ['IS', 'IS NOT']:
                raise QueryBadNullComparator("Error in query at {}: Use 'IS' or 'IS NOT' as the operator "
                                             "when comparing to NULL values.".format(triplet))


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
