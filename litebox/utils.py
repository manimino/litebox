from typing import Union, Dict, Callable
from litebox.exceptions import InvalidFields


def get_field_name(field: Union[str, Callable]):
    if isinstance(field, str):
        return field
    else:
        return field.__name__


def get_field(obj, field):
    """Get a field from a Python object (class, dataclass, namedtuple) or from a dict"""
    if callable(field):
        val = field(obj)
    elif isinstance(obj, dict):
        val = obj.get(field, None)
    else:
        val = getattr(obj, field, None)
    return val


def validate_fields(fields: Dict[Union[str, Callable], type]):
    """Check that fields are correct. Raise exception if not."""
    if not fields or not isinstance(fields, dict):
        raise InvalidFields("Need a nonempty dict of fields, such as {'x': float}")
    for i, f in enumerate(fields):
        if fields[f] not in [int, float, bool, str]:
            raise InvalidFields(
                "Expected int, float, bool, or str field type at position {}, but got {}".format(
                    i, fields[f]
                )
            )
        if not isinstance(f, str) and not callable(f):
            raise InvalidFields(
                "Field name must be a str or function, got {} at position {}".format(f, i)
            )
