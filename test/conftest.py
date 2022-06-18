import pytest

from rangeindex.constants import DUCKDB, SQLITE, PANDAS


@pytest.fixture(params=[DUCKDB, SQLITE, PANDAS])
def engine(request):
    return request.param
