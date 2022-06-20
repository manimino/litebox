from typing import *

import pandas as pd

from rangeindex.constants import *


PYTYPE_TO_PANDAS = {float: "float64", int: "int64", bool: "bool", str: "O"}


class PandasIndex:
    def __init__(self, on: Dict[str, type], **kwargs):
        self.fields = on

        # make empty dataframe
        self.df = pd.DataFrame(
            {
                field: pd.Series(dtype=PYTYPE_TO_PANDAS[dtype])
                for field, dtype in self.fields.items()
            }
        )
        self.df[PYOBJ_ID_COL] = pd.Series(dtype="uint64")
        self.df[PYOBJ_COL] = pd.Series(dtype="O")

    def add(self, obj: Any):
        """Add a single object to the index. Use add_many instead where possible."""
        ptr = id(obj)
        if ptr in set(self.df[PYOBJ_ID_COL]):
            return
        new_df = pd.DataFrame(
            {field: [getattr(obj, field, None)] for field, dtype in self.fields.items()}
        )
        new_df[PYOBJ_ID_COL] = [ptr]
        new_df[PYOBJ_COL] = [obj]
        self.df = pd.concat([self.df, new_df])

    def add_many(self, objs: List[Any]):
        """Add a collection of objects to the index."""
        obj_ids = [id(obj) for obj in objs]

        # Build a dict first to eliminate repeats in objs. Also eliminate objs we already have.
        # Assumption: dictionaries are sorted (true in Python 3.6+)
        old_obj_ids = set(self.df[PYOBJ_ID_COL])
        new_objs = {
            obj_ids[i]: objs[i]
            for i in range(len(obj_ids))
            if obj_ids[i] not in old_obj_ids
        }

        # Insert objs by creating a temporary dataframe and adding that to the DB.
        # This is recommended by the DuckDB docs, and is much faster than inserting with cursor.executemany().
        new_df = pd.DataFrame(
            {
                field: [getattr(obj, field, None) for obj in new_objs.values()]
                for field, dtype in self.fields.items()
            }
        )
        new_df[PYOBJ_ID_COL] = list(new_objs.keys())
        new_df[PYOBJ_COL] = list(new_objs.values())
        self.df = pd.concat([self.df, new_df])

    def find(self, where: Optional[str] = None) -> List:
        """Find Python objects that match the query constraints."""
        if not where:
            return self.df[PYOBJ_COL].to_list()
        return self.df.query(where)[PYOBJ_COL].to_list()

    def remove(self, obj: Any):
        """Remove a single object from the index. Slow operation (requires table scan + rebuilding parts of table)."""
        i = self.df[self.df[PYOBJ_ID_COL] == id(obj)].index[0]
        self.df.drop(i, inplace=True)

    def update(self, obj: Any, updates: Dict[str, Any]):
        """Update a single object in the index. Somewhat slow operation (requires table scan)."""
        i = self.df[self.df[PYOBJ_ID_COL] == id(obj)].index[0]
        for field, new_value in updates.items():
            if field in self.fields:
                self.df.at[i, field] = new_value
            # apply changes to the obj as well
            setattr(obj, field, new_value)

    def __len__(self) -> int:
        return len(self.df)

    def __contains__(self, obj) -> bool:
        return id(obj) in self.df[PYOBJ_ID_COL]

    def __iter__(self):
        return iter(self.df[PYOBJ_COL])

    def __next__(self):
        return next(self.df[PYOBJ_COL])
