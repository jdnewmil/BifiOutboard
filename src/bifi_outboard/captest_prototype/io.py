# io.py
"""Input/output routines."""

from typing import Optional
import pandas as pd


def read_pvsyst_hourly(
    con
    , sep: str = ';'
    , dayfirst: bool = True
    , date_format: Optional[str] = None
) -> pd.DataFrame:
    return pd.read_csv(
        con
        , encoding='windows-1252'
        , skiprows=list(range(10))+[11, 12]
        , sep=sep
        , parse_dates=True
        , dayfirst=dayfirst
        , index_col=0
        , date_format=date_format)
