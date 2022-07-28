from typing import Any


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
