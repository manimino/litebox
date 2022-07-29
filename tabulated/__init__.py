import importlib
from tabulated.sqlite_table import LiteBox


if importlib.util.find_spec("pandas"):
    from tabulated.pandas_table import PandasBox
