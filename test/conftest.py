import pytest

from tabulated.sqlite_table import LiteBox
from tabulated.pandas_table import PandasBox


@pytest.fixture(params=[LiteBox, PandasBox])
def table_class(request):
    return request.param


class AssertRaises:
    """
    While the unittest package has an assertRaises context manager, it is incompatible with pytest + fixtures.
    Cleaner to just implement an AssertRaises here.
    """

    def __init__(self, exc_type):
        self.exc_type = exc_type

    def __enter__(self):
        pass

    def __exit__(self, exception_type, exception_value, exception_traceback):
        assert exception_type == self.exc_type
        return True  # suppress the exception
