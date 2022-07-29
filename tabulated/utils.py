from typing import Any, Dict
from tabulated.exceptions import InvalidFields


def get_field(obj: Any, field: str):
    """Get a field from a Python object (class, dataclass, namedtuple) or from a dict"""
    if isinstance(obj, dict):
        return obj.get(field, None)
    else:
        return getattr(obj, field, None)


def set_field(obj: Any, field: str, new_value: Any):
    """Set a field on a Python object (class, dataclass, namedtuple) or from a dict"""
    if isinstance(obj, dict):
        obj[field] = new_value
    else:
        setattr(obj, field, new_value)


def validate_fields(fields: Dict[str, type]):
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
