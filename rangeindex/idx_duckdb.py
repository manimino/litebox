import duckdb
import pandas as pd
from typing import List, Tuple, Dict, Any, Optional, Union

from rangeindex.constants import *
from rangeindex.globals import get_next_table_id

PYTYPE_TO_DUCKDB = {int: "BIGINT", str: "VARCHAR", float: "DOUBLE"}


class DuckDBIndex:
    def __init__(self, fields: Dict[str, Any]):
        self.fields = fields
        self.objs = dict()  # maps {id(object): object}
        self.table_name = "table_" + str(get_next_table_id())
        self.con = duckdb.connect(database=":memory:")

        # create duckdb table
        cols = [f"{field} {PYTYPE_TO_DUCKDB[ftype]}" for field, ftype in fields.items()]
        cols.append(f"{PYOBJ_ID_COL} UBIGINT")
        col_str = ", ".join(cols)
        self.con.execute(f"CREATE TABLE {self.table_name}({col_str})")

    def add(self, obj: Any):
        ptr = id(obj)
        if ptr in self.objs:  # already have this object
            return
        values = [getattr(obj, f, None) for f in self.fields] + [ptr]
        qmarks = ",".join(["?"] * (len(self.fields) + 1))
        self.con.execute(f"INSERT INTO {self.table_name} VALUES ({qmarks})", values)
        self.objs[ptr] = obj

    def add_many(self, objs: List[Any]):
        obj_ids = [id(obj) for obj in objs]

        # Build a dict first to eliminate repeats in objs. Also eliminate objs we already have.
        # Assumption: dictionaries are sorted (true in Python 3.6+)
        new_objs = {
            obj_ids[i]: objs[i]
            for i in range(len(obj_ids))
            if obj_ids[i] not in self.objs
        }

        # Insert objs by creating a temporary dataframe and adding that to the DB.
        # This is recommended by the DuckDB docs, and is much faster than inserting with cursor.executemany().
        df = pd.DataFrame(
            {
                field: [getattr(obj, field, None) for obj in new_objs.values()]
                for field in self.fields
            }
        )
        df[PYOBJ_ID_COL] = list(new_objs.keys())
        self.con.execute(f"INSERT INTO {self.table_name} SELECT * FROM df")
        self.objs.update(new_objs)

    def find(self, where: Union[str, Optional[List[Tuple]]] = None) -> List:
        if not where:
            return list(self.objs.values())

        if isinstance(where, str):
            query = self._to_sql(where)
            self.con.execute(query)
        else:
            qstr, values = self._tuples_to_query_str(where)
            self.con.execute(qstr, values)
        rows = list(r[0] for r in self.con.fetchall())
        return list(self.objs[ptr] for ptr in rows)

    def _to_sql(self, where: str):
        return f"SELECT {PYOBJ_ID_COL} FROM {self.table_name} WHERE {where}"

    def _tuples_to_query_str(
        self, where: Optional[List[Tuple]] = None
    ) -> Tuple[str, List]:
        q = [f"SELECT {PYOBJ_ID_COL} FROM {self.table_name} WHERE"]
        values = []
        for i, triplet in enumerate(where):
            field, op, value = triplet

            if value is None:
                q.append(f"{field} {op} NULL")
            else:
                q.append(f"{field} {op} ?")
                values.append(value)
            if i < len(where) - 1:
                q.append("AND")
        return "\n".join(q), values

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
        self.con.execute(q, set_values)

    def remove(self, obj: Any):
        ptr = id(obj)
        del self.objs[ptr]
        q = f"DELETE FROM {self.table_name} WHERE {PYOBJ_ID_COL}=?"
        self.con.execute(q, (ptr,))

    def __len__(self):
        return len(self.objs)

    def __contains__(self, obj):
        return id(obj) in self.objs
