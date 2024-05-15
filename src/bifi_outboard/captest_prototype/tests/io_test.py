# io_tests.py

import pathlib
from ..io import read_pvsyst_hourly

dta_dir = pathlib.Path(__file__).parent / 'data'

def test_read_pvsyst_hourly():
    ans = read_pvsyst_hourly(
        dta_dir / 'Seattle_Project_HourlyRes_E.CSV'
        , sep=';'
        , date_format='%d/%m/%y %H:%M')
    assert 'date' == ans.index.name
