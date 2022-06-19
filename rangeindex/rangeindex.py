from typing import *

from rangeindex.constants import *
from rangeindex.exceptions import *
from rangeindex.idx_pandas import PandasIndex
from rangeindex.idx_sqlite import SqliteIndex


class RangeIndex:
    def __init__(
        self,
        objs: Optional[List[Any]] = None,
        on: Dict[str, Any] = None,
        engine: str = SQLITE,
        **kwargs,
    ):
        self._validate_fields(on)
        self.engine = engine.lower()
        if self.engine == SQLITE:
            self.idx = SqliteIndex(on=on, **kwargs)
        elif self.engine == PANDAS:
            self.idx = PandasIndex(on=on, **kwargs)
        else:
            raise InvalidEngineError(f"Engine must be one of: '{SQLITE}', '{PANDAS}'")
        if objs is not None:
            self.add_many(objs)

    def add(self, obj: Any):
        self.idx.add(obj)

    def add_many(self, objs: Iterable[Any]):
        self.idx.add_many(objs)

    def find(self, where: Union[str, Optional[List[Tuple]]] = None) -> List:
        return self.idx.find(where)

    def remove(self, obj: Any):
        self.idx.remove(obj)

    def update(self, obj: Any, updates: Dict[str, Any]):
        self.idx.update(obj, updates)

    @staticmethod
    def _validate_fields(fields):
        if not fields or not isinstance(fields, dict):
            raise InvalidFields("Need a nonempty dict of fields, such as {'x': float}")
        for i, f in enumerate(fields):
            if fields[f] not in [int, float, str]:
                raise TypeError(
                    "Expected int, float, or str field type at position {}, but got {}".format(
                        i, fields[f]
                    )
                )
            if not isinstance(f, str):
                raise TypeError(
                    "Field name must be a str, got {} at position {}".format(f, i)
                )

    def __len__(self):
        return len(self.idx)
