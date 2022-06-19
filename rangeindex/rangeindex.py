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
        **kwargs
    ):
        self._validate_fields(on)
        self.engine = engine.lower()
        if self.engine == SQLITE:
            self.idx = SqliteIndex(on, **kwargs)
        elif self.engine == PANDAS:
            self.idx = PandasIndex(on, **kwargs)
        else:
            raise InvalidEngineError(
                f"Engine must be one of: '{SQLITE}', '{PANDAS}'"
            )
        if objs is not None:
            self.add_many(objs)

    def add(self, obj: Any):
        self.idx.add(obj)

    def add_many(self, objs: Iterable[Any]):
        self.idx.add_many(objs)

    def find(self, where: Union[str, Optional[List[Tuple]]] = None) -> List:
        if not isinstance(where, str):
            self._validate_query_triplets(where)
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

    def _validate_query_triplets(self, query: Optional[List[Tuple]]):
        if query is None:
            return
        if not isinstance(query, Iterable):
            raise QueryMalformedError(
                "Query must be a list of tuples, example: [('field', '<', 3)]"
            )
        if not len(query):
            return
        for i, triplet in enumerate(query):
            if not isinstance(triplet, Iterable):
                raise QueryMalformedError(
                    "Query must be a list of tuples, example: [('field', '<', 3)]"
                )
            if len(triplet) != 3:
                raise QueryMalformedError(
                    "Error in query element {}: expected a tuple of length 3, but got {}".format(
                        i, triplet
                    )
                )
            field, op, value = triplet
            if op.upper() not in [
                "<",
                ">",
                "==",
                "=",
                "!=",
                ">=",
                "<=",
                "IS",
                "IS NOT",
            ]:
                raise QueryBadOperatorError(
                    "Error in query at {}: {} is not a valid operator".format(
                        triplet, op
                    )
                )
            if field not in self.idx.fields:
                raise QueryUnknownFieldError(
                    "Error in query at {}: {} is not an indexed field".format(
                        triplet, field
                    )
                )
            if value is not None:
                if self.idx.fields[field] in [int, float] and type(value) not in [
                    int,
                    float,
                ]:
                    raise QueryTypeError(
                        "Error in query {}: expected type {} but got {}".format(
                            triplet, self.idx.fields[field], type(value)
                        )
                    )
                elif self.idx.fields[field] == str and type(value) != str:
                    raise QueryTypeError(
                        "Error in query {}: expected type {} but got {}".format(
                            triplet, self.idx.fields[field], type(value)
                        )
                    )
            if value is None and op.upper() not in ["IS", "IS NOT"]:
                raise QueryBadNullComparator(
                    "Error in query at {}: Use 'IS' or 'IS NOT' as the operator "
                    "when comparing to NULL values.".format(triplet)
                )

    def __len__(self):
        return len(self.idx)
