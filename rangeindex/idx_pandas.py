from typing import *

import pandas as pd

from rangeindex.constants import *


PYTYPE_TO_PANDAS = {float: "float64", int: "int64", str: "O"}


class PandasIndex:
    def __init__(self, fields: Dict[str, type], **kwargs):
        self.fields = fields

        # make empty dataframe
        self.df = pd.DataFrame(
            {
                field: pd.Series(dtype=PYTYPE_TO_PANDAS[dtype])
                for field, dtype in fields.items()
            }
        )
        self.df[PYOBJ_ID_COL] = pd.Series(dtype="uint64")
        self.df[PYOBJ_COL] = pd.Series(dtype="O")

    def add(self, obj: Any):
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

    def find(self, where: Union[str, Optional[List[Tuple]]] = None) -> List:
        if not where:
            return self.df[PYOBJ_COL].to_list()
        if isinstance(where, str):
            q_str = where
        else:
            q_str = self._tuples_to_query_str(where)
        return self.df.query(q_str)[PYOBJ_COL].to_list()

    def _tuples_to_query_str(self, where: Optional[List[Tuple]] = None) -> str:
        q = []
        for i, triplet in enumerate(where):
            field, op, value = triplet

            if value is None:
                # field.isna() works inconsistently here.
                # Best to use NaN logic instead.
                if op.lower() == "is":
                    q.append(f"{field} != {field}")
                elif op.lower() == "is not":
                    q.append(f"{field} == {field}")
            else:
                if self.fields[field] == str:
                    q.append(f'{field} {op} "{value}"')
                else:
                    q.append(f"{field} {op} {value}")
        return " and ".join(q)

    def remove(self, obj: Any):
        i = self.df[self.df[PYOBJ_ID_COL] == id(obj)].index[0]
        self.df.drop(i, inplace=True)

    def update(self, obj: Any, updates: Dict[str, Any]):
        i = self.df[self.df[PYOBJ_ID_COL] == id(obj)].index[0]
        for field, value in updates.items():
            self.df.at[i, field] = value

    def __len__(self):
        return len(self.df)

    def __contains__(self, obj):
        return id(obj) in self.df[PYOBJ_ID_COL]
