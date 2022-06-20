from math import log2
from typing import List, Tuple, Dict, Any, Optional, Iterable

import sqlite3

from rangeindex.constants import *
from rangeindex.globals import get_next_table_id


PYTYPE_TO_SQLITE = {float: "NUMBER", int: "NUMBER", str: "TEXT", bool: "NUMBER"}


class SqliteIndex:
    def __init__(self, on: Dict[str, type], table_index: Optional[List[Tuple[str]]] = None):
        self.objs = dict()  # maps {id(object): object}
        self.table_name = "ri_" + str(get_next_table_id())
        self.conn = sqlite3.connect(":memory:")
        self.fields = on

        self.table_index = table_index
        if self.table_index is None:
            # By default, create a single-column index on each field.
            # If you really want no indices whatsoever, specify indices=[].
            self.table_index = [(f,) for f in self.fields]

        # create sqlite table
        tbl = [f"CREATE TABLE {self.table_name} ("]
        for field, pytype in self.fields.items():
            s_type = PYTYPE_TO_SQLITE[pytype]
            tbl.append(f"{field} {s_type},")
        tbl.append(f"{PYOBJ_ID_COL} INTEGER PRIMARY KEY")
        tbl.append(")")
        tbl.append('WITHOUT ROWID')
        cur = self.conn.cursor()
        cur.execute("\n".join(tbl))
        # Deferring creation of indices until after data has been added is much faster.
        self.indices_made = False

    def _create_indices(self):
        """Create indices for the SQLite table"""
        cur = self.conn.cursor()
        for index in self.table_index:
            index_name = "_".join(index)
            index_cols = ",".join(index)
            idx_str = (
                f"CREATE INDEX idx_{index_name} ON {self.table_name}({index_cols})"
            )
            cur.execute(idx_str)
            # Note that the PYOBJ_ID_COL is indexed by virtue of being the primary key.
        self.indices_made = True

    def add(self, obj: Any):
        """Add a single object to the index. Use add_many instead where possible."""
        ptr = id(obj)
        if ptr in self.objs:
            return  # already got it

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

    def add_many(self, objs: Iterable[any]):
        """Add a collection of objects to the index."""
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
        """Remove a single object from the index. Fast operation (<1ms usually)."""
        ptr = id(obj)
        del self.objs[ptr]
        q = f"DELETE FROM {self.table_name} WHERE {PYOBJ_ID_COL}=?"
        cur = self.conn.cursor()
        cur.execute(q, (ptr,))
        self.conn.commit()

    def update(self, obj: Any, updates: Dict[str, Any]):
        """Update a single object in the index. Fast operation (<1ms usually)."""
        set_cols = []
        set_values = []
        for attr, new_value in updates.items():
            if attr in self.fields:
                set_cols.append(f"{attr}=?")
                set_values.append(updates[attr])
        set_str = ",".join(set_cols)
        q = f"UPDATE {self.table_name} SET {set_str} WHERE {PYOBJ_ID_COL}=?"
        ptr = id(obj)
        set_values.append(ptr)
        cur = self.conn.cursor()
        cur.execute(q, set_values)
        self.conn.commit()
        # apply changes to the obj as well
        for field, new_value in updates.items():
            setattr(obj, field, new_value)

    def find(self, where: Optional[str] = None) -> List[Any]:
        """Find Python objects that match the query constraints."""
        if not where:
            return list(self.objs.values())

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
        limit_int = int(len(self.objs) / log2(len(self.objs) + 0.000001))
        query = f"SELECT {PYOBJ_ID_COL} FROM {self.table_name} WHERE {where} LIMIT {limit_int}"
        cur = self.conn.cursor()
        cur.execute(query)
        ptrs = [r[0] for r in cur]
        if len(ptrs) < limit_int:
            return list(self.objs[ptr] for ptr in ptrs)

        # If we're here, we got too many rows. So this query would be best run
        # without an index.
        query = (
            f"SELECT {PYOBJ_ID_COL} FROM {self.table_name} NOT INDEXED WHERE {where}"
        )
        cur.execute(query)
        return list(self.objs[r[0]] for r in cur)

    def __len__(self) -> int:
        return len(self.objs)

    def __contains__(self, obj) -> bool:
        return id(obj) in self.objs

    def __iter__(self):
        return iter(self.objs.values())

    def __next__(self):
        return next(self.objs.values())
