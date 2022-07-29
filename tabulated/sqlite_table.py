from typing import List, Tuple, Dict, Any, Optional, Iterable, Union, Optional

import sqlite3

from tabulated.constants import *
from tabulated.exceptions import NotInIndexError
from tabulated.globals import get_next_table_id
from tabulated.utils import get_field, set_field, validate_fields

PYTYPE_TO_SQLITE = {float: "NUMBER", int: "NUMBER", str: "TEXT", bool: "NUMBER"}


class SqliteTable:
    def __init__(
        self, objs: Optional[Iterable[Any]] = None,
            on: Dict[str, type] = None,
            index: Optional[List[Union[Tuple[str],str]]] = None
    ):
        validate_fields(on)
        self.fields = on
        self.obj_map = dict()  # maps {id(object): object}
        self.table_name = "ri_" + str(get_next_table_id())
        self.conn = sqlite3.connect(":memory:")

        # create sqlite table
        tbl = [f"CREATE TABLE {self.table_name} ("]
        for field, pytype in self.fields.items():
            s_type = PYTYPE_TO_SQLITE[pytype]
            tbl.append(f"{field} {s_type},")
        tbl.append(f"{PYOBJ_ID_COL} INTEGER PRIMARY KEY")
        tbl.append(")")
        cur = self.conn.cursor()
        cur.execute("\n".join(tbl))

        if objs is not None:
            self.add_many(objs)

        # Deferring creation of indices until after data has been added is much faster.
        self._create_indices()

    def _create_indices(self, index: Optional[List[Union[Tuple[str],str]]] = None):
        """Create indices for the SQLite table"""
        cur = self.conn.cursor()

        if index is None:
            # By default, create a single-column index on each field.
            # If you really want no indices whatsoever, specify indices=[].
            index = [(f,) for f in self.fields]

        for idx in index:
            if isinstance(idx, str):
                index_name = idx
                index_cols = idx
            else:
                index_name = "_".join(idx)
                index_cols = ",".join(idx)
            idx_str = (
                f"CREATE INDEX idx_{index_name} ON {self.table_name}({index_cols})"
            )
            cur.execute(idx_str)
            # Note that the PYOBJ_ID_COL is indexed by virtue of being the primary key.

    def add(self, obj: Any):
        """Add a single object to the index. Use add_many instead where possible."""
        ptr = id(obj)
        if ptr in self.obj_map:
            return  # already got it

        col_str = ",".join(self.fields.keys()) + f",{PYOBJ_ID_COL}"
        value_str = ",".join(["?"] * (len(self.fields) + 1))
        q = f"INSERT INTO {self.table_name} ({col_str}) VALUES({value_str})"

        self.obj_map[ptr] = obj
        values = [get_field(obj, c) for c in self.fields] + [ptr]
        cur = self.conn.cursor()
        cur.execute(q, values)

    def add_many(self, objs: Iterable[any]):
        """Add a collection of objects to the index."""
        obj_ids = [id(obj) for obj in objs]

        # Build a dict first to eliminate repeats in objs. Also skip objs already in the index.
        new_objs = {
            obj_ids[i]: objs[i]
            for i in range(len(obj_ids))
            if obj_ids[i] not in self.obj_map
        }

        # do inserts
        value_str = ",".join(["?"] * (len(self.fields) + 1))
        col_str = ",".join(self.fields.keys()) + f",{PYOBJ_ID_COL}"
        q = f"INSERT INTO {self.table_name} ({col_str}) VALUES ({value_str})"

        rows = []
        for ptr, obj in new_objs.items():
            values = [get_field(obj, c) for c in self.fields] + [ptr]
            rows.append(values)

        cur = self.conn.cursor()
        cur.executemany(q, rows)
        self.obj_map.update(new_objs)

    def remove(self, obj: Any):
        """Remove a single object from the index. Fast operation (<1ms usually)."""
        ptr = id(obj)
        if ptr not in self.obj_map:
            raise NotInIndexError(f"Could not find object with id: {ptr}")
        del self.obj_map[ptr]
        q = f"DELETE FROM {self.table_name} WHERE {PYOBJ_ID_COL}=?"
        cur = self.conn.cursor()
        cur.execute(q, (ptr,))

    def update(self, obj: Any, updates: Dict[str, Any]):
        """Update a single object in the index. Fast operation (<1ms usually)."""
        ptr = id(obj)
        if ptr not in self.obj_map:
            raise NotInIndexError(f"Could not find object with id: {ptr}")
        set_cols = []
        set_values = []
        for attr, new_value in updates.items():
            if attr in self.fields:
                set_cols.append(f"{attr}=?")
                set_values.append(updates[attr])
        set_str = ",".join(set_cols)
        q = f"UPDATE {self.table_name} SET {set_str} WHERE {PYOBJ_ID_COL}=?"
        set_values.append(ptr)
        cur = self.conn.cursor()
        cur.execute(q, set_values)
        self.conn.commit()
        # apply changes to the obj as well
        for field, new_value in updates.items():
            set_field(obj, field, new_value)

    def find(self, where: Optional[str] = None) -> List[Any]:
        """Find Python objects that match the query constraints."""
        if not where:
            return list(self.obj_map.values())

        """
        Optimization: SQLite will often try to use its indexes in scenarios where it shouldn't.
        This results in poor time performance on queries returning a large number of items.
        Benchmarking says we should cut this off at a bit above sqrt(n_objects).
        """

        limit_int = int(len(self.obj_map) ** 0.65)
        query = f"SELECT {PYOBJ_ID_COL} FROM {self.table_name} WHERE {where} LIMIT {limit_int}"
        cur = self.conn.cursor()
        cur.execute(query)
        ptrs = [r[0] for r in cur]
        if len(ptrs) < limit_int:
            objs = list(self.obj_map[ptr] for ptr in ptrs)
            return objs

        # If we're here, we got too many rows. So this query would be best run
        # without an index.
        query = (
            f"SELECT {PYOBJ_ID_COL} FROM {self.table_name} NOT INDEXED WHERE {where}"
        )
        cur.execute(query)
        return list(self.obj_map[r[0]] for r in cur)

    def __len__(self) -> int:
        return len(self.obj_map)

    def __contains__(self, obj) -> bool:
        return id(obj) in self.obj_map

    def __iter__(self):
        return iter(self.obj_map.values())
