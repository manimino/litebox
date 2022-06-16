import pytest

from rangeindex.constants import DUCKDB, SQLITE, PANDAS


@pytest.fixture(params=[DUCKDB, SQLITE, PANDAS])
def backend(request):
    return request.param
