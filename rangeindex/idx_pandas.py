from typing import *

import pandas as pd

from rangeindex.constants import *


class PandasIndex:

    def __init__(self, fields: Dict[str, type]):
        self.df = None
        self.fields = fields

    def add(self, obj: Any):
        for f in self.fields:
            pass

    def add_many(self, objs: Iterable[Any]):
        obj_ids = set(self.df[PYOBJ_ID_COL])
        new_objs = [(id(obj), obj) for obj in objs]

        new_df = pd.DataFrame()
        new_df[PYOBJ_ID_COL] = None
        self.idx.add_many(objs)

    def find(self, where: Union[str, Optional[List[Tuple]]] = None) -> List:
        if not isinstance(where, str):
            self._validate_query_triplets(where)
        return self.idx.find(where)

    def remove(self, obj: Any):
        self.idx.remove(obj)

    def update(self, obj: Any, updates: Dict[str, Any]):
        self.idx.update(obj, updates)

    def __len__(self):
        return len(self.df)

    def __contains__(self, obj):
        return id(obj) in self.df[PYOBJ_ID_COL]