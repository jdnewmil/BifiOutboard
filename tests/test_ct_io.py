# test_ct_io.py

import pathlib
import pandas as pd
import bifi_outboard as bob


dtadir = pathlib.Path('data')

def test_load_pvsyst_df():
    fname0 = dtadir / 'FT' / 'Test Bifi Sheds_Project_VC0_HourlyRes_0.CSV'
    ans = bob.pvcaptest.io.load_pvsyst_df(fname0)
    assert isinstance(ans, pd.DataFrame)
