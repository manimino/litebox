from typing import Dict, Any, List, Optional

import numpy as np
import pandas as pd

from tabulated.constants import PYOBJ_COL, PYOBJ_ID_COL
from tabulated.exceptions import NotInIndexError
from tabulated.utils import get_field, set_field, validate_fields
from typing import Iterable, Any, List


PYTYPE_TO_PANDAS = {float: "float64", int: "int64", bool: "bool", str: "O"}


class PandasBox:
    def __init__(
        self, objs: Optional[Iterable[Any]] = None, on: Dict[str, type] = None
    ):
        validate_fields(on)
        self.fields = on

        # make empty dataframe
        col_types = dict()
        for field, dtype in self.fields.items():
            col_types[field] = pd.Series(dtype=PYTYPE_TO_PANDAS[dtype])
        self.df = pd.DataFrame(columns=col_types)
        self.df[PYOBJ_ID_COL] = pd.Series(dtype="uint64")
        self.df[PYOBJ_COL] = pd.Series(dtype="O")
        if objs:
            self.add_many(objs)

    def add(self, obj: Any):
        """Add a single object to the index. Use add_many instead where possible."""
        ptr = id(obj)
        if ptr in set(self.df[PYOBJ_ID_COL]):
            return
        new_df = pd.DataFrame(
            {field: [get_field(obj, field)] for field, dtype in self.fields.items()}
        )
        new_df[PYOBJ_ID_COL] = [ptr]
        new_df[PYOBJ_COL] = [obj]
        self.df = pd.concat([self.df, new_df])
        self.df.sort_values(PYOBJ_ID_COL, inplace=True)

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
                field: [get_field(obj, field) for obj in new_objs.values()]
                for field, dtype in self.fields.items()
            }
        )
        new_df[PYOBJ_ID_COL] = np.array(list(new_objs.keys()), dtype="uint64")
        new_df[PYOBJ_COL] = list(new_objs.values())
        self.df = pd.concat([self.df, new_df])
        self.df.sort_values(PYOBJ_ID_COL, inplace=True)

    def find(self, where: Optional[str] = None) -> List:
        """Find Python objects that match the query constraints."""
        if not where:
            return self.df[PYOBJ_COL].to_list()
        return self.df.query(where)[PYOBJ_COL].to_list()

    def remove(self, obj: Any):
        """Remove a single object from the index. Slow operation (requires rebuilding parts of table)."""
        ptr = id(obj)
        i = self._find_idx(ptr)
        if i == -1:
            raise NotInIndexError(f"Could not find object with id: {ptr}")
        else:
            self.df.drop(index=self.df.index[i], inplace=True)

    def update(self, obj: Any, updates: Dict[str, Any]):
        """Update a single object in the index. Fast - it's O(log(n)) since table is sorted by object id."""
        ptr = id(obj)
        i = self._find_idx(ptr)
        if i == -1:
            raise NotInIndexError(f"Could not find object with id: {ptr}")
        else:
            for field, new_value in updates.items():
                if field in self.fields:
                    # note that we don't use df.iloc here -- in testing, df.iloc appears to do a full
                    # table scan, making our O(log(n)) update into an O(n) update.
                    series = self.df[field]
                    series.values[i] = new_value
                # apply changes to the obj as well
                set_field(obj, field, new_value)

    def _find_idx(self, ptr: int) -> int:
        """
        Look up a pointer in {PYOBJ_ID_COL} and returns its numeric position ("iloc" in pandas terms).

        Returns -1 if not found.
        """
        pyobj_col = self.df[PYOBJ_ID_COL]
        i = pyobj_col.searchsorted(ptr)
        if i == len(pyobj_col):
            # happens when df is empty, or the ptr is bigger than any obj ptr we have
            return -1
        # searchsorted tells us the first index <= target, check for ==
        if pyobj_col.values[i] == ptr:
            return i
        return -1

    def __len__(self) -> int:
        return len(self.df)

    def __contains__(self, obj) -> bool:
        return self._find_idx(id(obj)) != -1

    def __iter__(self):
        return iter(self.df[PYOBJ_COL])
