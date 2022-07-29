import importlib
from tabulated.sqlite_table import SqliteTable


if importlib.util.find_spec("pandas"):
    from tabulated.pandas_table import PandasTable
