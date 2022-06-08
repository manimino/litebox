import sqlite3
from typing import List, Tuple, Dict, Any, Optional

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
    def __init__(self, fields):
        self.objs = dict()  # maps {id(object): object}
        self.table_name = 'ri_' + str(get_next_table_id())
        self.conn = sqlite3.connect(':memory:')
        self.idx_cols = set()

        # create sqlite table
        tbl = [f'CREATE TABLE {self.table_name} (']
        for field, pytype in fields.items():
            self.idx_cols.add(field)
            s_type = PYTYPE_TO_SQLITE[pytype]
            tbl.append(f'{field} {s_type},')
        tbl.append(f'{PYOBJ_COL} INTEGER')
        tbl.append(')')
        cur = self.conn.cursor()
        cur.execute('\n'.join(tbl))

        # create indices on all columns
        # pyobj column needs an index to do fast updates / deletes
        for col in self.idx_cols:
            idx = f'CREATE INDEX idx_{col} ON {self.table_name}({col})'
            cur.execute(idx)

    def add(self, obj: Any):
        ptr = id(obj)
        self.objs[ptr] = obj
        col_str = ','.join(self.idx_cols) + f',{PYOBJ_COL}'
        value_str = ','.join(['?']*(len(self.idx_cols)+1))
        q = f'INSERT INTO {self.table_name} ({col_str}) VALUES({value_str})'
        values = [obj.__dict__[c] for c in self.idx_cols] + [ptr]
        cur = self.conn.cursor()
        cur.execute(q, values)
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
        for col in self.idx_cols:
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

    def find_obj_ids(self, query: Optional[List[Tuple]] = None) -> Tuple[int]:
        if not query:
            return list(self.objs.keys())
        q = [f'SELECT {PYOBJ_COL} FROM {self.table_name} WHERE']
        for i, triplet in enumerate(query):
            field, op, value = triplet
            if i < len(query)-1:
                q.append(f'{field} {op} {value} AND')
            else:
                q.append(f'{field} {op} {value}')
        cur = self.conn.cursor()
        rows = cur.execute('\n'.join(q))
        return (r[0] for r in rows.fetchall())

    def find(self, query: Optional[List[Tuple]] = None) -> List[Any]:
        if not query:
            return list(self.objs.values())
        return [self.objs[ptr] for ptr in self.find_obj_ids(query)]
