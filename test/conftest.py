import pytest

from tabulated.constants import SQLITE, PANDAS


@pytest.fixture(params=[SQLITE, PANDAS])
def engine(request):
    return request.param
