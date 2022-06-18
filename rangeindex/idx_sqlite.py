from math import log2
from typing import List, Tuple, Dict, Any, Optional

import sqlite3

from rangeindex.constants import *
from rangeindex.globals import get_next_table_id


PYTYPE_TO_SQLITE = {float: "NUMBER", int: "NUMBER", str: "TEXT"}

PYOBJ_COL = "__obj_id_reserved__"

table_id = 0  # keeps sqlite table names unique when using multiple indices


def get_next_table_id():
    global table_id
    table_id += 1
    return table_id


class SqliteIndex:
    def __init__(self, fields: Dict[str, type]):
        self.objs = dict()  # maps {id(object): object}
        self.table_name = "ri_" + str(get_next_table_id())
        self.conn = sqlite3.connect(":memory:")
        self.fields = fields

        # create sqlite table
        tbl = [f"CREATE TABLE {self.table_name} ("]
        for field, pytype in fields.items():
            s_type = PYTYPE_TO_SQLITE[pytype]
            tbl.append(f"{field} {s_type},")
        tbl.append(f"{PYOBJ_ID_COL} INTEGER")
        tbl.append(")")
        cur = self.conn.cursor()
        cur.execute("\n".join(tbl))
        # Deferring creation of indices until after data has been added is much faster.
        self.indices_made = False

    def _create_indices(self):
        # create indices on all columns
        # pyobj column needs an index to do fast updates / deletes
        cur = self.conn.cursor()
        for col in self.fields:
            idx = f"CREATE INDEX idx_{col} ON {self.table_name}({col})"
            cur.execute(idx)
        self.indices_made = True

    def add(self, obj: Any):
        ptr = id(obj)
        if ptr in self.objs:
            return  # already got it

        # TODO make this a constant
        col_str = ",".join(self.fields.keys()) + f",{PYOBJ_ID_COL}"
        value_str = ",".join(["?"] * (len(self.fields) + 1))
        q = f"INSERT INTO {self.table_name} ({col_str}) VALUES({value_str})"

        self.objs[ptr] = obj
        values = [getattr(obj, c, None) for c in self.fields] + [ptr]
        cur = self.conn.cursor()
        cur.execute(q, values)
        self.conn.commit()
        if not self.indices_made:
            self._create_indices()

    def add_many(self, objs: List[any]):
        obj_ids = [id(obj) for obj in objs]

        # Build a dict first to eliminate repeats in objs. Also skip objs already in the index.
        new_objs = {
            obj_ids[i]: objs[i]
            for i in range(len(obj_ids))
            if obj_ids[i] not in self.objs
        }

        # do inserts
        value_str = ",".join(["?"] * (len(self.fields) + 1))
        col_str = ",".join(self.fields.keys()) + f",{PYOBJ_ID_COL}"
        q = f"INSERT INTO {self.table_name} ({col_str}) VALUES ({value_str})"

        rows = []
        for ptr, obj in new_objs.items():
            values = [getattr(obj, c, None) for c in self.fields] + [ptr]
            rows.append(values)

        cur = self.conn.cursor()
        cur.executemany(q, rows)
        self.conn.commit()
        if not self.indices_made:
            self._create_indices()
        self.objs.update(new_objs)

    def remove(self, obj: Any):
        ptr = id(obj)
        del self.objs[ptr]
        q = f"DELETE FROM {self.table_name} WHERE {PYOBJ_ID_COL}=?"
        cur = self.conn.cursor()
        cur.execute(q, (ptr,))
        self.conn.commit()

    def update(self, obj: Any, updates: Dict[str, Any]):
        set_cols = []
        set_values = []
        for col in self.fields:
            if col in updates:
                set_cols.append(f"{col}=?")
                set_values.append(updates[col])
        set_str = ",".join(set_cols)
        q = f"UPDATE {self.table_name} SET {set_str} WHERE {PYOBJ_ID_COL}=?"
        ptr = id(obj)
        set_values.append(ptr)
        print(q, set_values)
        cur = self.conn.cursor()
        cur.execute(q, set_values)
        self.conn.commit()

    def find(self, where: Optional[List[Tuple]] = None) -> List[Any]:
        """Find Python object ids that match the query constraints."""
        if not where:
            return list(self.objs.values())

        if isinstance(where, str):
            where_str = where
            values = []
        else:
            where_str, values = self._tuples_to_query_str(where)

        """
        Optimization: SQLite will often try to use its indexes in scenarios where it shouldn't.
        This results in poor time performance on queries returning a large number of items.
        Bit o'theory here:
         - Looking up k items by index takes O(k*log(n)) time by index.
         - Scanning all items takes O(n) time.
         - So we shouldn't use an index when O(n)/log(n) < O(k).
        Since we don't know what k is until we do the query, we do one query using indices first, using a limit.
        If it turns out that there are over n/log(n) matches, stop the query and retry without using indices.
        In practice, there are surely deeper optimizations available, but this is a good-enough simple threshold
        and makes the worst-case scenario much more palatable (improves benchmarks some 10x or so).
        """
        limit_int = int(len(self.objs) / log2(len(self.objs)+0.000001))
        query = f"SELECT {PYOBJ_ID_COL} FROM {self.table_name} WHERE {where_str} LIMIT {limit_int}"
        cur = self.conn.cursor()
        if values:
            cur.execute(query, values)
        else:
            cur.execute(query)
        ptrs = [r[0] for r in cur]
        if len(ptrs) < limit_int:
            return list(self.objs[ptr] for ptr in ptrs)

        # If we're here, we got too many rows -- this query would be best run
        # without an index. (speedup of ~5X or more for doing this).
        query = f"SELECT {PYOBJ_ID_COL} FROM {self.table_name} NOT INDEXED WHERE {where_str}"
        if values:
            cur.execute(query, values)
        else:
            cur.execute(query)
        return list(self.objs[r[0]] for r in cur)

    @staticmethod
    def _tuples_to_query_str(where: Optional[List[Tuple]] = None) -> Tuple[str, List]:
        q = []
        values = []
        for i, triplet in enumerate(where):
            field, op, value = triplet
            values.append(value)
            if i < len(where) - 1:
                q.append(f"{field} {op} ? AND")
            else:
                q.append(f"{field} {op} ?")
        return "\n".join(q), values

    def __len__(self):
        return len(self.objs)

    def __contains__(self, obj):
        return id(obj) in self.objs
