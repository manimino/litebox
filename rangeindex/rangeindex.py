import importlib.util

from typing import Optional, Dict, Iterable, Any, List

from rangeindex.constants import SQLITE, PANDAS
from rangeindex.exceptions import InvalidEngineError, InvalidFields, MissingPandasError
from rangeindex.idx_sqlite import SqliteIndex


class RangeIndex:
    def __init__(
        self,
        objs: Optional[Iterable[Any]] = None,
        on: Optional[Dict[str, Any]] = None,
        engine: str = SQLITE,
        **kwargs,
    ):
        self.engine = engine.lower()
        if self.engine == SQLITE:
            self.idx = SqliteIndex(on=on, **kwargs)
        elif self.engine == PANDAS:
            if importlib.util.find_spec("pandas"):
                from rangeindex.idx_pandas import PandasIndex

                self.idx = PandasIndex(on=on, **kwargs)
            else:
                raise MissingPandasError(
                    "Pandas not installed, please pip install pandas to use this engine."
                )
        else:
            raise InvalidEngineError(f"Engine must be one of: '{SQLITE}', '{PANDAS}'")
        if objs is not None:
            self.add_many(objs)

    def add(self, obj: Any):
        """Add a single object to the index. Use add_many instead where possible."""
        self.idx.add(obj)

    def add_many(self, objs: Iterable[Any]):
        """Add a collection of objects to the index."""
        self.idx.add_many(objs)

    def find(self, where: Optional[str] = None) -> List:
        """Find Python objects that match the query constraints."""
        return self.idx.find(where)

    def remove(self, obj: Any):
        """Remove a single object from the index. Fast in sqlite, slow in pandas."""
        self.idx.remove(obj)

    def update(self, obj: Any, updates: Dict[str, Any]):
        """Update a single object in the index. Fast in sqlite, somewhat slow in pandas."""
        self.idx.update(obj, updates)

    @staticmethod
    def _validate_fields(fields):
        """Check that fields are correct. Raise exception if not."""
        if not fields or not isinstance(fields, dict):
            raise InvalidFields("Need a nonempty dict of fields, such as {'x': float}")
        for i, f in enumerate(fields):
            if fields[f] not in [int, float, bool, str]:
                raise TypeError(
                    "Expected int, float, bool, or str field type at position {}, but got {}".format(
                        i, fields[f]
                    )
                )
            if not isinstance(f, str):
                raise TypeError(
                    "Field name must be a str, got {} at position {}".format(f, i)
                )

    def __len__(self) -> int:
        return len(self.idx)

    def __contains__(self, obj) -> bool:
        return obj in self.idx

    def __iter__(self):
        return iter(self.idx)

    def __next__(self):
        return next(self.idx)
